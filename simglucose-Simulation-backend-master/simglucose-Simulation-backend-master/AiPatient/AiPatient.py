import tensorflow as tf 
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np


#Body weight is not provided in initial dataset so we're gonna estimate an avg weighted male at 75kg

feature_columns = ['glucose', 'calories', 'heart_rate', 'steps', 'basal_rate', 'carb_input']
        
targetGlucose = 115.0

maxDosage = 10.0
maxPerHour = 10.0

DIA = 200 #Duration insulin Action (el w2t eli el insulin byb2a f3al feh) 200 d2ee2a 3.3 hours 


class AiPatient():
    def __init__(self):
        self._bodyWeight = 75
        self._TDD = 0.5 * self._bodyWeight #total daily insulin dose
        self._ICR = 500 / self._TDD  #insulin2Carb ratio
        self._ISF = 1800 / self._TDD #insulin sensitivity
        self._totalDeliveredInsulin = 0



        self._sensorData = pd.read_csv('./AiPatient/PatientData/HUPA0002P.csv')
        
        self._sensorData.drop(columns=['time','bolus_volume_delivered'], inplace=True)
        self._lastReadingsBuffer = self._sensorData.head(12)
        

        self.__scaler = StandardScaler()
        self.__scaler.fit(self._sensorData[feature_columns])        

        try:
            self._predictionModel = load_model('./AiPatient/PatientData/glucose_lstm_model.h5', custom_objects={'mse': MeanSquaredError()})
        except:
            Exception("Failed to Load Glucose Prediction Model!")

        # Simulation dynamics parameters
        self._step_minutes = 5
        self._carb_absorption_minutes = 120  # typical gastric emptying window ~1.5h
        self._carb_events = []  # list of {"remaining_steps": int, "grams_per_step": float}

    def _updateTDD(self):
        alfa = 0.8
        self._TDD = alfa*self._TDD+(1-alfa)*self._totalDeliveredInsulin
    

    def _updateBuffer(self, bufferRow):
        self._lastReadingsBuffer = pd.concat([
            self._lastReadingsBuffer.iloc[1:],                   
            pd.DataFrame([bufferRow], columns=feature_columns)    
        ], ignore_index=True)

    def _updateGlucose(self, glucose, bolus, carbs_absorbed, steps):
         step_duration = self._step_minutes  # minutes per step
         # Moderate carb effect per gram and distribute via absorption
         carb_factor = 1.5  # mg/dL increase per gram absorbed (tunable)
         insulinSensitivity = self._ISF
         activityFactor = 0.002
         noiseStd = 1.5
     
         # scale insulin effect by duration / DIA
         insulin_effect = bolus * insulinSensitivity * (step_duration / DIA)
     
         change = carbs_absorbed * carb_factor - insulin_effect - steps * activityFactor
         noise = np.random.normal(0, noiseStd)

         # floor BG to physiological minimum
         return max(glucose + change + noise, 40)

    def _schedule_carb_event(self, grams: float):
        if grams <= 0:
            return
        steps = max(1, int(self._carb_absorption_minutes / self._step_minutes))
        grams_per_step = grams / steps
        self._carb_events.append({"remaining_steps": steps, "grams_per_step": grams_per_step})

    def _absorb_carbs_for_step(self) -> float:
        if not self._carb_events:
            return 0.0
        absorbed = 0.0
        next_events = []
        for ev in self._carb_events:
            if ev["remaining_steps"] > 0:
                absorbed += ev["grams_per_step"]
                ev["remaining_steps"] -= 1
                if ev["remaining_steps"] > 0:
                    next_events.append(ev)
        self._carb_events = next_events
        return absorbed

    def suggestDose(self, currentGlucose, carbIntake, modelPredictedGlucose=None):
        mealBolus = carbIntake / self._ICR if carbIntake > 0 else 0
        rawCorrection = (currentGlucose-targetGlucose) / self._ISF

        if modelPredictedGlucose is not None:
            predectidedCorrectionBolus = (modelPredictedGlucose-targetGlucose) / self._ISF
            actualCorrection = max(rawCorrection, predectidedCorrectionBolus)
        else:
            actualCorrection = rawCorrection        #this doesn't include any mealBolus data!!!! This also doesn't factor current insulin on board!!! (IMPORTANT WAWA)
        
        finalBolus = max(0, min(maxDosage, actualCorrection))
        return finalBolus
    
    def _predictBolusNextStep(self, buffer):
        scaledBuffer = self.__scaler.transform(buffer[0]).reshape(1,12,6)
        bolus = self._predictionModel.predict(scaledBuffer)[0][0]
        return bolus

    def simulateStep(self, carbIntake=0):
            
         lastReading = self._lastReadingsBuffer.iloc[-1]
    
         currentGlucose = lastReading['glucose']
         calories = lastReading['calories']
         hr = lastReading['heart_rate']
         steps = lastReading['steps']
         basal = lastReading['basal_rate']
    
         # schedule meal carbs across absorption window
         if carbIntake and carbIntake > 0:
             self._schedule_carb_event(float(carbIntake))
         absorbed_carbs = self._absorb_carbs_for_step()

         # model prediction
         predictedBolus = self._predictBolusNextStep(
              self._lastReadingsBuffer.to_numpy(dtype=float).reshape(1, 12, 6)
         )
    
         # update glucose
         new_glucose = self._updateGlucose(
             glucose=currentGlucose,
             bolus=predictedBolus,
             carbs_absorbed=absorbed_carbs,
             steps=steps
         )
    
         # add delivered insulin
         self._totalDeliveredInsulin += predictedBolus
    
         # new evolving row for next timestep
         newRow = np.array([
             new_glucose,
             calories,
             hr,
             steps,
             basal,
             carbIntake  # keep meal event logging in buffer
         ])
    
         # update the 12-step buffer
         self._updateBuffer(newRow)
    
         return {
             "glucose": new_glucose,
             "bolus": predictedBolus,
             "carbs": absorbed_carbs
         }
    



    

