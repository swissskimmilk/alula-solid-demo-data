import struct 
import matplotlib.pyplot as plt

INFO_STRING_ID = 1
GNSS_ID = 2
BARO_ID = 3
SH2_ROT_ID = 4
SH2_ACCEL_ID = 5
UBX_ID = 6
SATS_ID = 7
TIME_ID = 8
SH2_GYRO_ID = 9
RESET_ID = 12
ACCEL_ID = 11
IDS = [INFO_STRING_ID, GNSS_ID, BARO_ID, SH2_ROT_ID, SH2_ACCEL_ID, UBX_ID, SATS_ID, TIME_ID, SH2_GYRO_ID, RESET_ID, ACCEL_ID]

CORRUPTION_STR = "*Corruption error*"
NO_MORE_DATA_STRING = "*No more data*"

PROCESS_ROCKET = False
PROCESS_ANTENNA = True
PLOT = True

IDDataTypes = {BARO_ID: [2, 2], ACCEL_ID: [2, 2, 2], SH2_GYRO_ID: [2, 2, 2], SH2_ROT_ID: [2, 2, 2], SH2_ACCEL_ID: [2, 2, 2], RESET_ID: [1], TIME_ID: [3], SATS_ID: [1], UBX_ID: [1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], GNSS_ID:[3, 3, 3, 3, 1]}
IDStrings = {BARO_ID: ["Pressure: ", " | Temperature: "], ACCEL_ID: ["X accel: ", " | Y accel: ", " | Z accel: "], SH2_GYRO_ID: ["Gyro X: ", " | Gyro Y: ", " | Gyro Z: "], SH2_ROT_ID: ["Yaw: ", " | Pitch: ", " | Roll: "], SH2_ACCEL_ID: ["NG accel X: ", " | NG accel Y: ", " | NG accel Z: "], RESET_ID: ["Reset: "], TIME_ID: ["Curr micros: "], SATS_ID: ["Num satellites: "], UBX_ID: ["", ":", ":", ":", " | Latitude: ", " | Longitude: ", " | Altitude: ", " | North vel: ", " | East val: ", " | Down vel: ", " | Groundspeed: ", " | Vert acc: ", " | HorAcc: ", " | SpeedAcc: "], GNSS_ID: ["Time: ", "| Latitude: ", " | Longitude: ", " | Altitude MSL: ", " | Fix type: "]};

if PROCESS_ROCKET:
    rData = open("Rocket Data 2.txt", 'rb').read()
    rUncomp = open("Rocket Uncompressed.txt", 'w')

if PROCESS_ANTENNA:
    aData = open("Antenna Data.txt", 'rb')
    aProcessed = open("Antenna Processed.txt", 'w')

graphDict = {'Temperature': [[], []], 'Pressure': [[], []], 'X accel': [[], []], 'Y accel': [[], []], 'Z accel': [[], []]}
firstTime = None
lastTime = None
currTime = None

def uncompressArray(bArray, file):
    currTime = None
    index = 0
    while index < len(bArray):
        id = bArray[index]
        index += 1

        if id == 0x0D or id == 0x0A:
            continue
        elif id not in range(1, 13):
            #print(" | Corruption error", end = '')
            file.write(CORRUPTION_STR)
            continue
        elif id == INFO_STRING_ID:
            sIndex = index
            while bArray[index] != 0x0D:
                index += 1
            try: 
                output = bArray[sIndex:index].decode()
            except: 
                #print(" | Corruption error", end='')
                file.write(CORRUPTION_STR)
                index += 1
                continue
            index += 2
            #print(output)
            file.write(output + "\n")
        # Had weird behavior with GPS, cause unknown, this ignores all GPS data other than the time which is correct 
        elif id == UBX_ID:
            for j in range(0, 3):
                #print(IDStrings[id][j], end="")
                file.write(IDStrings[id][j])
                value = bArray[index]
                index += 1
                #print(value, end="")
                file.write(str(value))
                if bArray[index] == 0x0D and bArray[index + 1] == 0x0A and (index + 2 >= len(bArray) or bArray[index + 2] in IDS):
                    #print(" | No more data", end='')
                    file.write(NO_MORE_DATA_STRING)
                    break
            while not (bArray[index] == 0x0D and bArray[index + 1] == 0x0A and (index + 2 >= len(bArray) or bArray[index + 2] in IDS)):
                index += 1
            file.write(' ')
        elif id == RESET_ID:
            #print("Reset")
            file.write("Reset")
        else: 
            for j in range(0, len(IDDataTypes[id])):
                if bArray[index] == 0x0D and bArray[index + 1] == 0x0A and (index + 2 >= len(bArray) or bArray[index + 2] in IDS):
                    #print(" | No more data", end='')
                    file.write(NO_MORE_DATA_STRING)
                    break
                # This is here as a janky solution to an issue on the rocket side of two ID being in sequence before a new line. Cause unknown 
                elif bArray[index + 1] == 0x0D and bArray[index + 2] == 0x0A and (index + 3 >= len(bArray) or bArray[index + 3] in IDS):
                    #print(" | No more data", end='')
                    file.write(NO_MORE_DATA_STRING)
                    index += 1
                    break
                else: 
                    # file.write(IDStrings[id][j])
                    file.write(IDStrings[id][j])
                    dataType = IDDataTypes[id][j]
                    if dataType == 1:
                        value = bArray[index]
                        index += 1
                    if dataType == 2: 
                        [value] = struct.unpack('f', bArray[index: index + 4])
                        index += 4
                    if dataType == 3:
                        value = int.from_bytes(bArray[index: index + 4], 'little', signed='True')
                        index += 4
                    #print(value, end="")
                    file.write(str(value))

                    if PLOT:
                        if id == TIME_ID:
                            currTime = value
                            global firstTime, lastTime
                            if firstTime == None:
                                firstTime = currTime
                            lastTime = currTime
                        elif currTime == None: 
                            print("Time invalid")
                        elif id == BARO_ID:
                            if j == 0: 
                                graphDict['Pressure'][0].append(currTime)
                                graphDict['Pressure'][1].append(value)
                            else: 
                                graphDict['Temperature'][0].append(currTime)
                                graphDict['Temperature'][1].append(value)
                        elif id == ACCEL_ID:
                            if j == 0: 
                                graphDict['X accel'][0].append(currTime)
                                graphDict['X accel'][1].append(value)
                            elif j == 1:
                                graphDict['Y accel'][0].append(currTime)
                                graphDict['Y accel'][1].append(value)
                            else:
                                graphDict['Z accel'][0].append(currTime)
                                graphDict['Z accel'][1].append(value)

            #print()
            file.write("\n")

if PROCESS_ROCKET:
    uncompressArray(bytearray(rData), rUncomp)
    rUncomp.close()

def breakApart(): 
    # Arbitrary start point before launch, and need to index ahead of that so the code can look back 
    rLines = aData.readlines()[367260:]
    for i in range(2, len(rLines)):
        # print(rLines[i])
        # Find rssi, which always begins each transmission. Also, must encode String to byte array since the file is read as binary 
        if rLines[i][0:4] == bytearray('rssi', encoding='utf8'):
            transmission = rLines[i - 1]
            # Gets raw transmission by going back several lines if neccessary, to account for new lines 
            backIndex = 2
            check = rLines[i - backIndex - 1]
            while bytearray('accel', encoding='utf8') not in check and bytearray('Num', encoding='utf8') not in check and bytearray('Latitude', encoding='utf8') not in check:
                print(transmission)
                transmission = bytearray(rLines[i - backIndex]) + transmission
                backIndex += 1
                check = rLines[i - backIndex - 1]
            # for byte in transmission:
            #     print(byte, end=' ')
            # print()
            uncompressArray(transmission, aProcessed)

if PROCESS_ANTENNA:
    breakApart()
    aData.close()
    aProcessed.close()

if PLOT:
    # plt.plot(graphDict['Pressure'][0], graphDict['Pressure'][1], 'bo')
    # plt.title('Pressure (rocket)')
    # plt.ylim(950, 800)

    plt.plot(graphDict['Z accel'][0], graphDict['Z accel'][1], 'bo')
    plt.title('Z accel (antenna)')
    plt.ylim(-250, 250)

    plt.xlim(-675184416, -550149756)
    # plt.xlim(firstTime, lastTime)
    plt.show()