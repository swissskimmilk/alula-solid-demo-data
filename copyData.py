# For shorting compresesed rocket data to relevant chunk 
# rData = open("Rocket Data.txt", 'rb')
# rOut = open("Rocket Data 2.txt", 'wb')

# rLines = rData.readlines()
# for line in rLines[1696:]:
#     rOut.write(line)
# rData.close()
# rOut.close()

# For shorting the uncompressed rocket data to relevant chunk 
rData = open("Rocket Uncompressed.txt", 'r')
rOut = open("Rocket Uncompressed 2.txt", 'w')

rLines = rData.readlines()
for line in rLines[1395860:]:
    rOut.write(line)
rData.close()
rOut.close()