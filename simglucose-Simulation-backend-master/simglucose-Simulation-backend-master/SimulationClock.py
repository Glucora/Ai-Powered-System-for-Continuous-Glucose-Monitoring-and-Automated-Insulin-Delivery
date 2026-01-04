import time
from datetime import datetime, timedelta

SIM_BASE_RATE = 1

class SimulationClock:
    def __init__(self, startTimestamp: int):
        self._simulationStartTime = startTimestamp
        self._realStartTime = time.time()
        self._currentSimulationTime = startTimestamp
        self._isRunning = False
        self._timestampData = []
        self._simulationRate = 1.0
    

     # When changing time rate the value appended is multiplied before appending....so at time second 2 at 4x speed it becomes 8 but when you decrease after 1 second 3*1x speed  becomes 3 second so we travel back in time
     # Congrats we Traveled back in time
    def updateClock(self):
        if not self._isRunning:
            self._isRunning = True
        
        elapsedTimeRealtime = time.time() - self._realStartTime 
        last_timestamp = self._timestampData[-1] if self._timestampData else 0
        self._currentSimulationTime = last_timestamp + (elapsedTimeRealtime*self._simulationRate)
        self._timestampData.append(self._currentSimulationTime)

    def setSimulationRate(self, simRate=SIM_BASE_RATE):
        self._simulationRate=simRate
        print(f"set sim rate to {self._simulationRate}")
        
    def setIsRunningState(self, state: bool):
        self._isRunning = state
    
    def getSimulationTime(self):
        return self._currentSimulationTime
    
    def getSimulationTimestampData(self):
        return self._timestampData
    
    def getSimulationRate(self):
        return self._simulationRate 