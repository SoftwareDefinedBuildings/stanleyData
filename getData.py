import os
import sys
from smap.archiver.client import SmapClient
from smap.contrib import dtutil
import re
import json

inf = open("room_metadata")
roomMetadata = json.load(inf)

c = SmapClient("http://new.openbms.org/backend")

outputDir = "data"
if len(sys.argv) < 2:
	print "No output directory provided. Using default <data>"
else:
	outputDir = sys.argv[1].strip()

if os.path.exists(outputDir):
	if not os.path.isdir(outputDir):
		print "File with the same name exists. Delete it first"
		exit()
else:
	os.makedirs(outputDir)

startDate = "05/27/2015"
endDate = "07/04/2015"

numRooms = len(roomMetadata)
count = 0
for room in roomMetadata:
	count += 1
	print "Pulling in data for room : ", room  , "(%d/%d)" % (count, numRooms )
	for sensor in roomMetadata[room]: 
		data = c.query("select data in ('%s','%s') where Metadata/Name='%s'" % 
			(startDate, endDate, roomMetadata[room][sensor]) )

		outf = open(outputDir + "/" + roomMetadata[room][sensor], "w")
		if len(data) == 0:
			continue
		for reading in data[0]["Readings"]:
			outf.write( str(int(reading[0])).strip() + "," + str(reading[1]).strip() + "\n" )

		outf.close()



