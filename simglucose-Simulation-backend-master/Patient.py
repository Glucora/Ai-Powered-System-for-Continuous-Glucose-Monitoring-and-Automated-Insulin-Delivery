import pandas as pd
from datetime import datetime
PATIENT_FILES_PATH = './patientData' 


patientTypeFile = {
    1 : 'child',
    2 : 'adolescent',
    3 : 'adult'
}


class Patient:
    def __init__(self, patientType=3):
        if patientType < 1 or patientType > 3:
            ValueError(f'{patientType} is Not a valid patient type!')
            return
        
        
        self._paientSimulationDataFrame = pd.read_csv(f'{PATIENT_FILES_PATH}/{patientTypeFile[patientType]}.csv')
        self._paientSimulationDataFrame['Time'] = pd.to_datetime(self._paientSimulationDataFrame['Time'])

        
        self._patientType = patientTypeFile[patientType]
        
        self._glucoseLevelData = []
        self._carbsLevelData = []
        self._insulinInjectioData = []
        self._patientState = None



    def getSimStartTime(self):
        date = pd.to_datetime(self._paientSimulationDataFrame.head(1)['Time'],).iloc[0]
        date = date.tz_localize('UTC')
        return int(date.timestamp())
        

    def _getRowAtNearestTimestamp(self, timestamp):
        
        
        if isinstance(timestamp, (pd.Timestamp, datetime)):
            targetTimeStamp = timestamp
        else:
            targetTimeStamp = datetime.fromtimestamp(timestamp)
        timestamp = pd.to_datetime(timestamp)
        
        idx = (self._paientSimulationDataFrame['Time'] - targetTimeStamp).abs().idxmin()

        return self._paientSimulationDataFrame.iloc[idx]
    
    def getGlucoseLevelAtTimestamp(self, timestamp):
    
        glucoseLevel = self._getRowAtNearestTimestamp(timestamp=timestamp)['BG']
        return glucoseLevel
    
    def getInsulinDeliveredAtTimestamp(self, timestamp):
        glucoseLevel = self._getRowAtNearestTimestamp(timestamp=timestamp)['insulin']
        return glucoseLevel

    def updateGlucoseData(self, absoluteTimestamp):
        self._glucoseLevelData.append(self._getRowAtNearestTimestamp(timestamp=absoluteTimestamp)['BG'])

    def updateInsulinInjectionData(self, absoluteTimestamp):
        self._insulinInjectioData.append(self._getRowAtNearestTimestamp(timestamp=absoluteTimestamp)['insulin'])

    def updateCarbIntakeData(self, absoluteTimestamp):
        self._carbsLevelData.append(self._getRowAtNearestTimestamp(timestamp=absoluteTimestamp)['CHO'])

    def getGlucoseData(self):
        return self._glucoseLevelData

    def getInsulinInjectionData(self):
        return self._insulinInjectioData
    
    def getCarbsIntakeData(self):
        return self._carbsLevelData
    
    def getPatientType(self):
        return self._patientType
    
    def getLatestGlucoseReading(self):
        return self._glucoseLevelData[-1]
    
    def getLatestInsulinIntake(self):
        return self._insulinInjectioData[-1]
    
    def getLatestCarbsIntake(self):
        return self._carbsLevelData[-1]
    
    def getPatientStatus(self): ####This just spamms the message in logs not just one
        glucoseLevel = self._glucoseLevelData[-1] if  self._glucoseLevelData else 120 #random value idk.I don't want the default to be that the patient is in Hyper/hypoglycemia
        insulinInjection = self._insulinInjectioData[-1] if  self._glucoseLevelData else 0
        currentState = "Patient is in Hyperglycemia!" if glucoseLevel > 180 else "Patient is in Hypoglycemia!" if glucoseLevel < 80 else None

        match (glucoseLevel, round(insulinInjection, 2)):
            case (glucose, insulin) if glucose >  180:
                currentState = "Patient is in Hyperglycemia!"
            case (glucose, insulin) if glucose <  80:
                currentState = "Patient is in Hypoglycemia!"
            case (glucose, insulin) if insulin > 0.03:
                currentState = f"[Info] Patient took {insulin} units of insulin."  ####DOUBLE CHECK UNITS
            
            


        if currentState != self._patientState:
            self._patientState = currentState
            return self._patientState
        