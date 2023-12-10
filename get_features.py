import analysis 
import numpy as np
import pandas as pd


class Features:
    def __init__(self, data, all_cars):
        self.data = data
        self.X = []
        self.Y = []
        self.all_cars = all_cars[:10]
        self.filterGTDdata()
        self.helper()
        # make data for all GTD cars first then use only top 10 to train the model.


    def filterGTDdata(self):
        temp = []
        for d in self.data:
            if d[1] == "GTD" and (d[0] in self.all_cars):
                temp.append(d)
        self.data = temp 


    def getRaceProgress(self):
        race_progress = []        
        for d in self.data:
            seconds = d[5]
            race_progress.append(seconds / 90000)
        return race_progress    
    

    def getTireAge(self):
        # assuming a new tire set every pit stop
        # ** many times consecutive pit stops are made very close to each other **
        tire_age = []
        most_recent_tire_time = {}
        for c in self.all_cars:
            most_recent_tire_time[c] = 0
        for d in self.data:
            mins, sec = d[4].split(':')
            seconds = (int(mins)*60) + (float(sec))
            if d[7] == "Track":
                if d[6] == "Yellow":
                    tire_age.append(most_recent_tire_time[d[0]] + (seconds / 90000)*0.75)
                    most_recent_tire_time[d[0]] += (seconds / 90000)*0.75
                else:
                    tire_age.append(most_recent_tire_time[d[0]] + (seconds / 90000))
                    most_recent_tire_time[d[0]] += seconds / 90000

            else:
                tire_age.append(0)
                most_recent_tire_time[d[0]] = 0
        return tire_age             
        

    def getYellowFlag(self):
        yellow_flags = []
        for d in self.data:
            if d[6] == "Yellow":
                yellow_flags.append(True)
            else:
                yellow_flags.append(False)
        return yellow_flags
    

    def getDriverDuration(self):
        driver_duration = []
        driver_change_time = {}
        for c in self.all_cars:            
            driver_change_time[c] = [None, 0]

        for d in self.data:
            seconds = d[5]
            if d[7] == "Track":
                if d[2] != driver_change_time[d[0]][0]:
                    # driver was changed in the pit
                    driver_change_time[d[0]] = [d[2], seconds]

            driver_duration.append((seconds-driver_change_time[d[0]][1]) / 90000)
        return driver_duration
    

    def getPosition(self):
        positions = []
        leading_cars = [None]
        current_lap = '0'
        for d in self.data:
            if d[3] != current_lap:
                leading_cars.append(d[0])
                current_lap = d[3]
        for d in self.data:
            if d[0] == leading_cars[int(d[3])]:
                positions.append('leader')
            else:
                positions.append('pursuer')
        return positions
    

    def getCloseAhead(self):
        close_ahead = []
        all_pursuers = [None]
        car_and_pursuer_gaps = {}
        MAX_GAP = 2

        for d in range(len(self.data)-1):

            if self.data[d][3] == self.data[d+1][3]:
                car_and_pursuer_gaps[self.data[d][0]] = (self.data[d+1][5]-self.data[d][5])
            else:
                car_and_pursuer_gaps[self.data[d][0]] = 5 # Random value higher than 2.
                all_pursuers.append(car_and_pursuer_gaps)
                car_and_pursuer_gaps = {}

        car_and_pursuer_gaps[self.data[-1][0]] = 5        
        all_pursuers.append(car_and_pursuer_gaps)

        for d in self.data:
            if (d[0] in all_pursuers[int(d[3])]) and all_pursuers[int(d[3])][d[0]] < MAX_GAP:
                close_ahead.append(True)
            else:
                close_ahead.append(False)    
        return close_ahead
    

    def getPursuerTireChange(self):
        pursuer_tire_change = []
        car_tire_change = {} 
        for c in self.all_cars:
            car_tire_change[c] = False
        
        for d in range(len(self.data)-1):
            if self.data[d][3] == self.data[d+1][3]:
                pursuer_tire_change.append(car_tire_change[self.data[d+1][0]])
                if self.data[d+1][7] == "Pit":
                    car_tire_change[self.data[d+1][0]] = True
                else:
                    car_tire_change[self.data[d+1][0]] = False
            else:
                pursuer_tire_change.append(False) # There is no pursuer behind / last car.
        pursuer_tire_change.append(False)

        return pursuer_tire_change
    

    def getRemainingPitStops(self):
        MAX_STOPS = 25
        completed_stops = {}
        remaining_stops = []
        for c in self.all_cars:
            completed_stops[c] = 0
        for d in self.data:
            if d[7] == "Pit":
                completed_stops[d[0]] += 1
            remaining_stops.append(MAX_STOPS-completed_stops[d[0]])
        return remaining_stops        


    def helper(self):
        for d in self.data:
            hours, mins, secs = d[5].split(':')
            seconds = int(hours)*60*60 + int(mins)*60 + float(secs)
            d[5] = seconds
        self.data.sort(key = lambda x: (x[3], x[5]))


    def makeData(self):
        df = pd.DataFrame((self.getRaceProgress(), self.getTireAge(), self.getDriverDuration(),
                                   self.getRemainingPitStops(), self.getYellowFlag(), self.getPosition(),
                                   self.getCloseAhead(), self.getPursuerTireChange()))
        columns = ["Race Progress", "Tire age", "Driver duration", "Remaing pit stops",
                                    "Yellow flag", "Position", "Is close ahead", "Pursuer tire change"]
        df = df.transpose()
        df.columns = columns
        return df


if __name__ == "__main__":
    ra = analysis.RaceAnalysis()
    features = Features(ra.data, ra.gtd_positions)
    print(features.makeData())

