import re
import pandas as pd 
import matplotlib.pyplot as plt 

EXPORT_DATA = False
EXPORT_LAUNCH = False

# Structure: {'Title': [[indices], [values]]}
rawData = {'Temperature': [[], []], 'Pressure': [[], []], 'X accel': [[], []], 'Y accel': [[], []], 'Z accel': [[], []]}
masterTimes = {}
firstTime = None
lastTime = None

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

# This should be improved like a lot 
def removeOutliers(df): 
    print(df.dtypes)
    for key in rawData.keys():
        df[key] = df[key].apply(lambda x: None if abs(x) > 1e6 else x)
    print(df.dtypes)
    return df

def findLaunch():
    df = createDf()
    pressureMean = df.loc[:, 'Pressure'].mean()
    startIndex = df.loc[(df['dpdt'] < -20) & (df['Z accel'] > 20)].index[0] - 50
    windowDf = df.loc[startIndex + 100:]
    endIndex = windowDf.loc[(abs(windowDf['dpdt']) < 1) & (windowDf['Pressure'] > pressureMean * 0.995)].index[0] + 50
    launchDf = df.loc[startIndex:endIndex]
    if EXPORT_LAUNCH:
        launchDf.to_excel('launchData.xlsx', index=True)
    return launchDf

def plotAll():
    df = findLaunch()
    startTime = df.iloc[0]['Time']
    # This will break if there is an overflow during the plotting but I don't care
    newIndices = df['Time'].apply(lambda x: (x - startTime) / 1e6)
    df = df.set_index(newIndices)
    for key in rawData.keys():
        df[key].plot(style='b.')
        plt.title(key + " (rocket)")
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