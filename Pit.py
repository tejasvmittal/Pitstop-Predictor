import analysis
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
import numpy as np
from sklearn.linear_model import LinearRegression, HuberRegressor



def tireDegradationPlot(car, data):
    """
    Plot the lap times vs session time to see the tire degradation over a stint.
    The laptimes list contains all the lap times of the car and has None where the
    car pitted or was in yellow flag.
    """

    laptimes = []
    session_times = []
    car_data = []
    for d in data:
        if d[0] == car: car_data.append(d)

    pitstops = []

    for d in range(1, len(car_data)):

        if (car_data[d][6] == "Yellow") or (car_data[d-1][6] == "Yellow") or (car_data[d][7] == "Pit") or (car_data[d-1][7] == "Pit"):
            laptimes.append(None)
            if car_data[d][7] == "Pit":
                hours, mins, sec = car_data[d][5].split(':')
                pitstops.append(int(hours) + int(mins)/60 + float(sec)/3600)
        else:
            mins, sec = car_data[d][4].split(':')
            laptimes.append(int(mins)*60+float(sec))
        hours, mins, sec = car_data[d][5].split(':')
        session_times.append(int(hours) + int(mins)/60 + float(sec)/3600)

    # plotting the linear model for each stint.
    i, j = 0, 1
    learners = []
    avg_laptimes_interval = []

    while (i <= j and j < len(laptimes)-1):
        if (laptimes[j] != None) and (laptimes[j+1] == None):
            lr = HuberRegressor() # could use simple linear equation for this. Dont know how
            lr.fit(np.array(session_times[i:j+1]).reshape(j-i+1, 1), laptimes[i:j+1])
            learners.append(lr)
            j+=1

        elif (laptimes[j] == None) and (laptimes[j+1] != None):
            j += 1
            i = j 
        
        else:
            j+=1
        
        # need to learn the last learner 
    if laptimes[i] != None and laptimes[j] != None:
        lr = LinearRegression()
        lr.fit(np.array(session_times[i:j+1]).reshape(j-i+1, 1), laptimes[i:j+1])
        learners.append(lr)

    l = 0

    for st in range(len(session_times)-1):
        if laptimes[st] == None:
            avg_laptimes_interval.append(None)
        
        else:
            reshaped_session_time = np.array(session_times[st]).reshape(1, 1)
            pred = learners[l].predict(reshaped_session_time)
            avg_laptimes_interval.append(pred[0])

            if laptimes[st+1] == None:
                l += 1


    if laptimes[-1] == None:
        avg_laptimes_interval.append(None)
    else:
        reshaped_session_time = np.array(session_times[-1]).reshape(1, 1)
        pred = learners[-1].predict(reshaped_session_time)
        avg_laptimes_interval.append(pred[0])

    avg_coeff = 0
    c = 0

    for lr in learners:
        if lr.coef_[0] > 0:
            avg_coeff += lr.coef_[0]
            c += 1

    avg_coeff /= c
    print(avg_coeff)

    for p in pitstops:
        plt.axvline(p, color="red", alpha=0.5)

    plt.plot(session_times, laptimes)
    plt.plot(session_times, avg_laptimes_interval, 'black', alpha=0.5)
    plt.xlabel("Session time")
    plt.ylabel("Lap times")
    plt.show()   






if __name__ == '__main__':
    ra = analysis.RaceAnalysis()
    tireDegradationPlot('93', ra.data)

