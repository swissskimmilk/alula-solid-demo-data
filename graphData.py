import re
import pandas as pd 
import matplotlib.pyplot as plt 
import math

EXPORT_DATA = False
EXPORT_LAUNCH = False
SEPARATE_FIGURES = True

# Structure: {'Title': [[indices], [values]]}
rawData = {'X accel': [[], []], 'Y accel': [[], []], 'Z accel': [[], []], 'Temperature': [[], []], 'Pressure': [[], []]}
# Structure: {index: micros}
masterTimes = {}
altitudeFunc1 = lambda temp0, press0: (lambda p: 3.28084 * ((temp0+273.15) * (1 - (p / 1013.25) ** (1 / ((9.812 * 28.97 / 1000) / ((6.5 / 1000) * 8.31432))))) / (6.5 / 1000) - 3.28084 * ((temp0+273.15) * (1 - (press0 / 1013.25) ** (1 / ((9.812 * 28.97 / 1000) / ((6.5 / 1000) * 8.31432))))) / (6.5 / 1000))
altitudeFunc2 = lambda temp0, press0: (lambda p: 3.28084*((8.314*(temp0+273.15)* math.log(p/1013.25))/(-9.812*0.02905)) - 3.28084*((8.314*(temp0+273.15)* math.log(press0/1013.25))/(-9.812*0.02905)))

# Processes the incoming file and stores the data in the rawData dictionary 
def getAllData(fileName):
    keys = rawData.keys()
    packets = open(fileName, 'r').read().split("\n\n")
    # Ignore the first index, the setup data 
    for i in range(1, len(packets[1:])):
        pairs = re.split("\n| \| ", packets[i])
        currTime = int(pairs[0].split(": ")[1])
        masterTimes[i] = currTime
        for pair in pairs:
            for key in keys:
                if pair.startswith(key):
                    rawData[key][0].append(i)
                    rawData[key][1].append(float(pair.split(": ")[1].strip("*No more data*")))
                    break

# Creates a dataframe out of the raw data dictionary, and adds the dpdt column 
def createDf():
    assert(masterTimes), "Must run getAllData first"
    df = pd.DataFrame({"Time": masterTimes.values()}, index=masterTimes.keys())
    series = {title: pd.Series(rawData[title][1], index=rawData[title][0], name=title) for title in rawData.keys()}
    for col in series.values():
        df = df.join(col)
    # Computes change in pressure over time, in seconds 
    dpdt = df['Pressure'].diff() / (df['Time'].diff() / 10e6)
    dpdt.name = "dpdt"
    df = df.join(dpdt)
    if EXPORT_DATA:
        df.to_excel('data.xlsx', index=True)
    return removeOutliers(df)

# This should be improved like a lot, it just removed excessively large values right now 
def removeOutliers(df): 
    for key in rawData.keys():
        df[key] = df[key].apply(lambda x: None if abs(x) > 1e6 else x)
    return df

# Find the launch and return a new data frame with only the launch data 
def findLaunch():
    df = createDf()
    pressureMean = df.loc[:, 'Pressure'].mean()
    startIndex = df.loc[(df['dpdt'] < -20) & (df['Z accel'] > 20)].index[0] - 50
    windowDf = df.loc[startIndex + 100:]
    endIndex = windowDf.loc[(abs(windowDf['dpdt']) < 1) & (windowDf['Pressure'] > pressureMean * 0.995)].index[0] + 300
    launchDf = df.loc[startIndex:endIndex]
    if EXPORT_LAUNCH:
        launchDf.to_excel('launchData.xlsx', index=True)
    return launchDf, df

# Plots all of the data from findLaunch
def plotAll():
    launchDf, df = findLaunch()
    startIndex = launchDf.index[0]
    startTime = launchDf.iloc[0]['Time']
    # This will break if there is an overflow during the plotting but I don't care
    newIndices = launchDf['Time'].apply(lambda x: (x - startTime) / 1e6)
    launchDf = launchDf.set_index(newIndices)

    if not SEPARATE_FIGURES:
        fig, axes = plt.subplots(nrows=2, ncols=3)
        keys = list(rawData.keys())
        for i in range(len(keys)):
            launchDf[keys[i]].plot(style='b.', markersize=3, ax=axes[i // 3, i % 3], title=keys[i] + " (rocket)", xlabel="Seconds")
            # plt.title(keys[i] + " (rocket)")
            plt.xlabel("Seconds")
        plt.tight_layout()
    else:
        keys = list(rawData.keys())
        for i in range(len(keys)):
            launchDf[keys[i]].plot(style='b.', markersize=3, title=keys[i] + " (rocket)", xlabel="Seconds")
            plt.xlabel("Seconds")
            plt.show()  

    # To plot the alitude 
    # pressureMean = df.loc[:, 'Pressure'].mean()
    # tempMean = df.loc[:, 'Temperature'].mean()
    pressure0 = df.loc[startIndex - 50: startIndex, 'Pressure'].mean()
    temp0 = df.loc[startIndex - 50: startIndex, 'Temperature'].mean()
    altitude = launchDf['Pressure'].apply(altitudeFunc1(temp0, pressure0))
    # altitude = launchDf['Pressure'].apply(altitudeFunc2(temp0, pressure0))
    altitude.name = "Altitude"

    launchDf = launchDf.join(altitude)
    # The None is a JANKY FIX FOR BAD DATA GET RID OF IT LATER
    apogee = launchDf.loc[(launchDf['dpdt'] == None) | (abs(launchDf['dpdt']) < 10)]["Altitude"].max()

    if not SEPARATE_FIGURES:
        launchDf["Altitude"].plot(style='b.', markersize=3, ax=axes[1, 2])
    else:
        launchDf["Altitude"].plot(style='b.', markersize=3)
    plt.title("Altitude (" + str(round(apogee, 2)) + " ft apogee)")
    plt.xlabel("Seconds")
    plt.show()

getAllData("Rocket Uncompressed.txt")
plotAll()

# if PLOT:
#     # plt.plot(graphDict['Pressure'][0], graphDict['Pressure'][1], 'bo')
#     # plt.title('Pressure (rocket)')
#     # plt.ylim(950, 800)

#     plt.plot(graphDict['Z accel'][0], graphDict['Z accel'][1], 'bo')
#     plt.title('Z accel (antenna)')
#     plt.ylim(-250, 250)

#     plt.xlim(-675184416, -550149756)
#     # plt.xlim(firstTime, lastTime)
#     plt.show()