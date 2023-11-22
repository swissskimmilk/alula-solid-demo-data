import struct 

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

IDDataTypes = {BARO_ID: [2, 2], ACCEL_ID: [2, 2, 2], SH2_GYRO_ID: [2, 2, 2], SH2_ROT_ID: [2, 2, 2], SH2_ACCEL_ID: [2, 2, 2], RESET_ID: [1], TIME_ID: [3], SATS_ID: [1], UBX_ID: [1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], GNSS_ID:[3, 3, 3, 3, 1]}
IDStrings = {BARO_ID: ["Pressure: ", " | Temperature: "], ACCEL_ID: ["X accel: ", " | Y accel: ", " | Z accel: "], SH2_GYRO_ID: ["Gyro X: ", " | Gyro Y: ", " | Gyro Z: "], SH2_ROT_ID: ["Yaw: ", " | Pitch: ", " | Roll: "], SH2_ACCEL_ID: ["NG accel X: ", " | NG accel Y: ", " | NG accel Z: "], RESET_ID: ["Reset: "], TIME_ID: ["Curr micros: "], SATS_ID: ["Num satellites: "], UBX_ID: ["", ":", ":", ":", " | Latitude: ", " | Longitude: ", " | Altitude: ", " | North vel: ", " | East val: ", " | Down vel: ", " | Groundspeed: ", " | Vert acc: ", " | HorAcc: ", " | SpeedAcc: "], GNSS_ID: ["Time: ", "| Latitude: ", " | Longitude: ", " | Altitude MSL: ", " | Fix type: "]};

rData = open("Rocket Data 2.txt", 'rb').read()
rUncomp = open("Rocket Uncompressed.txt", 'w')

antennaData = open("Antenna Data.txt", 'rb')
antennaProcessed = open("Antenna Processed.txt", 'w')


def uncompressArray(bArray):
    index = 0
    while index < len(bArray):
        id = bArray[index]
        #print(hex(index))
        index += 1
        if id == 0x0D or id == 0x0A:
            continue
        elif id not in range(1, 13):
            continue
            #print(" | Corruption error", end = '')
        elif id == INFO_STRING_ID:
            sIndex = index
            while bArray[index] != 0x0D:
                index += 1
            try: 
                output = bArray[sIndex:index].decode()
            except: 
                #print(" | Corruption error", end='')
                index += 1
                continue
            index += 2
            #print(output)
            rUncomp.write(output + "\n")
        elif id == UBX_ID:
            for j in range(0, 3):
                #print(IDStrings[id][j], end="")
                rUncomp.write(IDStrings[id][j])
                value = bArray[index]
                index += 1
                #print(value, end="")
                rUncomp.write(str(value))
            while not (bArray[index] == 0x0D and bArray[index + 1] == 0x0A and (index + 2 >= len(bArray) or bArray[index + 2] in [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12])):
                index += 1
        elif id == RESET_ID:
            #print("Reset")
            rUncomp.write("Reset")
        else: 
            for j in range(0, len(IDDataTypes[id])):
                if bArray[index] == 0x0D and bArray[index + 1] == 0x0A and (index + 2 >= len(bArray) or bArray[index + 2] in [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12]):
                    #print(" | No more data", end='')
                    rUncomp.write(" | No more data")
                    break
                elif bArray[index + 1] == 0x0D and index + 2 >= len(bArray) or bArray[index + 2] == 0x0A and (index + 3 >= len(bArray) or bArray[index + 3] in [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12]):
                    #print(" | No more data", end='')
                    rUncomp.write(" | No more data")
                    index += 1
                    break
                else: 
                    # rUncomp.write(IDStrings[id][j])
                    #print(IDStrings[id][j], end="")
                    rUncomp.write(IDStrings[id][j])
                    dataType = IDDataTypes[id][j]
                    if dataType == 1:
                        value = bArray[index]
                        index += 1
                    if dataType == 2: 
                        [value] = struct.unpack('f', bArray[index: index + 4])
                        index += 4
                    if dataType == 3:
                        value = int.from_bytes(bArray[index: index + 4], 'little')
                        index += 4
                    #print(value, end="")
                    rUncomp.write(str(value))
            #print()
            rUncomp.write("\n")

uncompressArray(bytearray(rData))

rssi = bytearray()
def breakApart(): 
    # 369259 = 371259 ish for some reason 
    rLines = antennaData.readlines()[369259:]
    for i in range(len(rLines)):
        print(rLines[i])
        if rLines[i][0:4] == bytearray('rssi', encoding='utf8'):
            arg = rLines[i - 1]
            
            for byte in arg:
                print(byte, end=' ')
            print()
            backIndex = 2
            check = rLines[i - backIndex - 1]
            while bytearray('accel', encoding='utf8') not in check and bytearray('Num', encoding='utf8') not in check and bytearray('Latitude', encoding='utf8') not in check:
                print(arg)
                arg = bytearray(rLines[i - backIndex]) + arg
                backIndex += 1
                check = rLines[i - backIndex - 1]

            
            for byte in arg:
                print(byte, end=' ')
            print()
            uncompressArray(arg)

# breakApart()
            





