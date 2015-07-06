import os
import sys
from smap.archiver.client import SmapClient
from smap.contrib import dtutil
import re
import json

c = SmapClient("http://new.openbms.org/backend", key="NAXk19YY45TTiXlajiQGQ8KTp283oHfp2Uly")
rooms = c.query("select distinct Metadata/room-id where Metadata/site='STA'")
metadata = {}
count = 0
numRooms = len(rooms)
for room in rooms:
	count += 1
	print "Building Metadata for room : %s (%d/%d)" % (room, count, numRooms )
	metadata[room] = {}
	sensors = c.query("select * where Metadata/room-id='" + str(room) + "' and Metadata/site='STA'")
	for i in range(len(sensors)):
		if "Name" not in sensors[i]["Metadata"]:
			continue
		pointName = sensors[i]["Metadata"]["Name"]
		roomMetadata = sensors[i]["Metadata"]
			
		if "room_temp" in roomMetadata:
			metadata[room]["room_temp"] = pointName
		if "supply_air_velocity" in roomMetadata or "supply_air_volume" in roomMetadata:
			metadata[room]["supply_air_velocity"] = pointName
		if "reheat_valve_position" in roomMetadata:
			metadata[room]["reheat_valve_position"] = pointName



outf = open("room_metadata", "w")
json.dump(metadata, outf)

