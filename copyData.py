rData = open("Rocket Data.txt", 'rb')
rOut = open("Rocket Data 2.txt", 'wb')

rLines = rData.readlines()
for line in rLines[1696:]:
    rOut.write(line)
rData.close()
rOut.close()