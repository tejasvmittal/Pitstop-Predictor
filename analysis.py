import csv 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
import numpy as np

# extend the hard variables to include information about every car in gtd.
# Top 17 cars in gtd actually finished the race at the end of 24 hrs.

class RaceAnalysis:
    def __init__(self, path="./Daytona_24hrs_GTD_replay.csv"):
        self.path = path 
        self.header, self.data = self.read_data(path)
        self.fixSessionTimes()

        self.gtd_positions = ['27','44','70','66','12','93','78','1','16','023','77','19','57','80','32','91','96','83','21','42','92','75','47']


        self.gtd_pitduration = ["0:39:28.571", "0:39:51.859", "0:46:15.857", "0:44:24.062", "0:39:42.707", "0:49:53.106", "0:46:14.322", "0:45:51.709", "0:42:34.255",  "0:48:59.103",
                                "0:40:43.077", "0:56:06.089", "0:38:06.233", "1:04:47.233", "1:16:13.802", "1:21:39.975", "1:39:12.790", "2:35:50.771", "2:23:42.874",
                                "1:21:07.333", "0:16:09.746", "3:39:29.159", "0:16:52.192"] #pit durations


    def read_data(self, path):
        """
        Read the CSV file and return the header (column names) and the data
        Path: ./CSV and Replay/WeatherTech Championship Daytona Race.csv"""
        try:
            file = open(path)
            reader = csv.reader(file)
            header = next(reader)
            data = []
            for row in reader:
                data.append(row)
            return header, data
        except(FileNotFoundError):
            print("Wrong file path or the file is missing")
        

    def cars_that_finished(self, class_):
        """
        Given the class of car, return a list of cars that raced till the end.
        class_ can be "GTP", "LMP2", "LMP3", "GTD", "GTDPRO"
        """
        result = []
        for i in range(len(self.data)-1, 0, -1):
            if self.data[i][1] == class_:
                result.append(self.data[i][0])
                if len(result) > 1 and (result[0] == result[-1]):
                    break
        result.pop() # remove the repeated car from the end.
        return result

        

    def avgStint(self, class_):
        """
        Plot a graph using matplotlib with x axis showing the finishing positions of the car
        and y-axis shows the average pit interval in terms of laps for a car.
        """

        car_list = self.cars_that_finished(class_)
        average_intervals = []

        for car in car_list:
            average_interval_car = []
            c=0
            in_pit = False
            for i in range(1, len(self.data)):
                if self.data[i][0] == car and self.data[i][7] == "Pit" and in_pit == False:
                    average_interval_car.append(int(self.data[i][3])-c)
                    in_pit = True
                elif self.data[i][0] == car and self.data[i][7] == "Track" and in_pit == True:
                    in_pit = False
                    c = int(self.data[i][3])
            average_intervals.append(sum(average_interval_car)/len(average_interval_car))

        return average_intervals



    def totalPitstops(self):
        """
        Plot a graph with finishing position of cars in a given class
        on the x-axis and the total number of pit stops during the race 
        on the y-axis.

        Note: Only cars that finished the entire race are considered.
        Check the function self.cars_that_finished()
        """

        total_pits_all = []
        car_list = self.gtd_positions[:10]

        for car in car_list:
            pits = 0
            in_pit = False 
            for data in self.data:
                if in_pit == False and data[0] == car and data[7] == "Pit":
                    pits += 1
                    in_pit = True
                elif in_pit == True and data[0] == car and data[7] == "Track":
                    in_pit = False
            total_pits_all.append(pits)
        
        return total_pits_all


    def GreenYellowPitRatio(self, class_):
        """
        Plot a graph where the x-axis occupies the finishing 
        positions of cars in the given class, and the y-axis
        displays the ratio of pit stops in yellow flags to 
        pit stops in green flags.
        """

        pit_ratios = []
        car_list = self.cars_that_finished(class_)
        for car in car_list:
            yellow = 0
            green = 0
            in_pit = False
            for data in self.data:
                if in_pit == False and data[0] == car and data[7] == "Pit" and data[6] == "Green":
                    green += 1
                    in_pit = True
                elif in_pit == False and data[0] == car and data[7] == "Pit" and data[6] == "Yellow":
                    yellow += 1
                    in_pit = True
                elif in_pit == True and data[0] == car and data[7] == "Track":
                    in_pit = False
            pit_ratios.append(yellow/green if green != 0 else 1)
        
        return pit_ratios


    def plotAvgStint_vs_pos(self):
        stint = self.avgStint("GTD")[:10]
        finish_pos = self.gtd_positions[:10]

        plt.scatter(finish_pos, stint)
        plt.xlabel("Finishing positions")
        plt.ylabel("Average stint btwn pits (# of laps)")
        plt.show()


    def Plot3dScatter(self, class_):
        """
        Plots a 3D graph with x-axis displaying the total pitstops, 
        y-axis displaying ratio between yellow and green flag pit stops
        and lastly z-axis displaying the average stint in laps"""
        car_list = self.cars_that_finished(class_)
        car_pos = [self.finishing_pos[class_][c] for c in car_list]
        average_stint = self.stint_duration_vs_pos(class_)
        pit_ratio = self.GreenYellowPitRatio_vs_pos(class_)
        total_pits = self.numberofpits_vs_pos(class_)

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(total_pits, pit_ratio, average_stint)
        ax.set_xlabel("Total pitstops")
        ax.set_ylabel("Ratio of pits yellow flag vs green flag")
        ax.set_zlabel("Average stint (# of laps)")
        # ax.title("Plot for class: "+str(class_))
        for i in range(len(car_list)):
            ax.text(total_pits[i], pit_ratio[i], average_stint[i], str(car_pos[i]))

        plt.show()


    def avgLapTimes(self):

        self.changeLaptimesToSeconds()
        car_list = self.gtd_positions[:10]
        # for the lap times calculate in green flag and avoid the lap after pitting.
        avg_laptimes = []
        car_pos = [self.gtd_positions.index(c)+1 for c in car_list]

        for car in car_list:
            car_laptimes = []
            for d in range(1, len(self.data)):
                if self.data[d][0] == car and self.data[d-1][6] == "Green" and self.data[d][6] == "Green" and self.data[d][7] == "Track" and self.data[d-1][7] == "Track":
                    car_laptimes.append(self.data[d][4])
            avg_laptimes.append(sum(car_laptimes)/len(car_laptimes))
        
        # plt.scatter(total_pits, avg_laptimes)
        # plt.xlabel("Total pitstops")
        # plt.ylabel("Avg lap times (Green flag)")
        # plt.title("Plot for class: GTD")
        # for i in range(len(car_list)):
        #     plt.annotate(str(car_pos[i]), (total_pits[i], avg_laptimes[i]))
        # plt.show()
        return avg_laptimes
    

    def changeLaptimesToSeconds(self):

        for data in self.data:
            if type(data[4]) is not str:
                return
            min, second = data[4].split(':')
            data[4] = int(min)*60 + float(second)

    def fixSessionTimes(self):
        hour = 0
        self.data[0][5] = '0:'+self.data[0][5]
        for i in range(1, len(self.data)):
            try:
                if int(self.data[i-1][5].split(':')[1]) > int(self.data[i][5].split(':')[0]):
                    hour += 1
                self.data[i][5] = str(hour)+':'+self.data[i][5]
            except:
                print(i+1)



    def plotAvgLaptime_vs_pitDuration(self):
        car_list = self.gtd_positions[:10]
        car_pos = [self.gtd_positions.index(c)+1 for c in car_list]
        avg_laptimes = self.avgLapTimes()
        pit_durations = self.gtd_pitduration[:10]
        for i in range(len(pit_durations)):
            hours, min, second = pit_durations[i].split(':')
            pit_durations[i] = int(hours)*60 + int(min) + float(second)/60
        
        plt.scatter(pit_durations, avg_laptimes)
        plt.xlabel("Pit stop duration (minutes)")
        plt.ylabel("Average lap times (seconds)")
        plt.title("Plot for GTD")
        for i in range(len(car_list)):
            plt.annotate(str(self.gtd_positions[i]), (pit_durations[i], avg_laptimes[i]))
        plt.show()        



    def totalPitduration(self, class_):
        """
        Return total pit duration for every car that finished
        in the given class.
        """
        car_list = self.cars_that_finished(class_)
        pit_durations = []
        avg_lap_times = self.avgLapTimes(class_)
        for car in car_list:
            in_pit = False 
            avg_laptime_stack = [avg_lap_times[car_list.index(car)]]
            car_pit_duration = []
            laptimes_after_last_pit = 0
            c = 0
            # collect avg lap time from the previous pit stop to the next
            for d in range(1, len(self.data)-1):
                # always use the top value on the stack for calculating pit duration
                if self.data[d][0] == car and self.data[d][7] == "Pit" and in_pit == False and self.data[d+1][7] == "Track":
                    # record the pit duration
                    if c != 0:
                        avg_laptime_stack.append(laptimes_after_last_pit/c)
                        c=0
                        laptimes_after_last_pit = 0
                    car_pit_duration.append(self.data[d][4]+self.data[d+1][4]-(2*avg_laptime_stack[-1]))
                
                # elif self.data[d][0] == car and self.data[d][]


    def carPits(self, car, laprange):
        # get the laps on which car pitted between the given lap range.

        pit = []
        for data in self.data:
            if data[0] == car and (laprange[0] <= int(data[3]) <= laprange[1]) and data[7] == "Pit":
                pit.append(int(data[3]))
        return pit
    

    def carGap2(self, car1, car2, laprange):
        """
        Filter data out for each of the two cars in seperate variables and
        compare their session times for the same lap and the difference between
        that is their gap. 
        """
        data1 = []
        data2 = []
        for data in self.data:
            if data[0] == car1 and (laprange[0] <= int(data[3]) <= laprange[1]):
                data1.append(data)

            if data[0] == car2 and (laprange[0] <= int(data[3]) <= laprange[1]):
                data2.append(data)
 
        car_gap = []
        i=0
        j=0
        while (i < len(data1) and j < len(data2)):
            hour1,min1,sec1 = data1[i][5].split(':')
            hour2,min2,sec2 = data2[j][5].split(':')
            if data1[i][3] == data2[j][3]:
                gap = (int(hour1)-int(hour2))*60*60 + (int(min1)-int(min2))*60 + (float(sec1)-float(sec2))               
                i+=1
                j+=1
            elif data1[i][3] > data2[j][3]:
                gap = car_gap[-1]
                j+=1
            else:
                gap = car_gap[-1]
                i+=1

            car_gap.append(gap)
        i,j=0,0
        is_yellow = False 
        yellow_flags = []
        yellow_start, yellow_end = 0,0
        pit1 = self.carPits(car1, laprange)
        pit2 = self.carPits(car2, laprange)

        while (i < len(data1) and j < len(data2)):

            if data1[i][3] == data2[j][3]:
                if (data1[i][6] == "Yellow" or data2[j][6] == "Yellow") and is_yellow == False:
                    is_yellow = True 
                    yellow_start = data1[i][3]
                elif (data1[i][6] == "Green" or data2[j][6] == "Green") and is_yellow == True:
                    is_yellow = False 
                    yellow_end = data1[i][3]
                    yellow_flags.append([yellow_start, yellow_end])
                i+=1
                j+=1

            elif data1[i][3] > data2[j][3]:
                j+=1 
            else:
                i+=1

        if yellow_start > yellow_end:
            yellow_flags.append([yellow_start, laprange[1]])


        for flag in yellow_flags:
            plt.axvspan(int(flag[0]), int(flag[1]), facecolor='yellow', alpha=0.5)


        for p1 in pit1:
            plt.axvline(int(p1), color="red", alpha=0.5)
        for p2 in pit2:
            plt.axvline(int(p2), color="black", alpha=0.5)

        patches = [mpatches.Patch(color='red', label='#'+car1+' pits'), mpatches.Patch(color='black', label='#'+car2+' pits'), mpatches.Patch(color='yellow', label='Yellow flag')]
        plt.plot([i for i in range(laprange[0], laprange[1]+1)], car_gap)
        plt.xlabel("Laps")
        plt.ylabel("Gap(seconds)")
        plt.title("Gap to #"+car2+" from #"+car1)
        plt.legend(handles=patches)
        plt.show()
        # return car_gap


    def carGapn(self, laprange, *cars):
        car_gaps = []
        yellow_durations = []
        pits = [self.carPits(c, laprange) for c in cars]

        colors = ['black', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

        for car in cars:
            car_gaps.append(self.carGap2(cars[0], car, laprange))
        # leaving out the yellow flag for now 
        for j in range(len(car_gaps)):
            plt.plot([i for i in range(laprange[0], laprange[1]+1)], car_gaps[j], color=colors[j], label=cars[j])

        for j in range(len(pits)):
            for p in pits[j]:
                plt.axvline(p, color=colors[j], alpha=0.5)

        plt.xlabel("Laps")
        plt.ylabel("Gap(seconds)")
        plt.legend()
        plt.title("Car gaps from #"+cars[0])
        plt.show()

    def avgPitDuration(self):
        total_pits = self.totalPitstops()
        average_pit_duration = [] # in seconds
        for i in range(10):
            hours, mins, sec = self.gtd_pitduration[i].split(':')
            pit_duration_sec = int(hours)*60*60 + int(mins)*60 + float(sec)
            average_pit_duration.append(pit_duration_sec/total_pits[i])
        
        return average_pit_duration


    def gapAfterPitting(self, target_car, opp_car, lap):
        # 1) calculate gap from every other car first
        # 2) Print out the before pitting gap
        # 3) Find the difference in gap time and print out the gap after pitting.
        pos = self.gtd_positions.index(target_car)

        car_gap = self.carGap2(target_car, opp_car, [lap, lap])
        print("Gap before pitting:", car_gap[0])
        print("Gap after pitting:", car_gap[0]-self.avgPitDuration()[pos])      

                    

if __name__ == '__main__':
    ra = RaceAnalysis()
    # ra.carGap('44', '27', (400, 600))
    # ra.carGapn([200,400], '27', '44', '70', '12', '66')
    # ra.tireDegradationPlot('70')
    ra.carGap2('27', '70', (1, 700))
    print(ra.data[5350])
    
    
    
    

