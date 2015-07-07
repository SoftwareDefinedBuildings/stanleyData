import os
import sys
import matplotlib.pyplot as pyplot
from pylab import *
import matplotlib.dates as mdates
import numpy
import json
from timeseries import *
import datetime

'''
START OF GLOBAL DATA
'''

'''
Global data 
1 -> transition
2 -> cold day
3 -> hot day
4 -> weekends
5 -> weekdays
'''

periods = { 	1 : [ 	( datetime.datetime( 2015, 5, 28, 9 , 0, 0 )   , datetime.datetime( 2015, 5, 28, 10 , 30, 0 ) ) ] ,
		2 : [ 	( datetime.datetime( 2015, 5, 28, 11 , 0 , 0 ) , datetime.datetime( 2015, 5, 29, 9, 0 , 0 ) ) ] ,
		3 : [ 	( datetime.datetime( 2015, 5, 29, 11 , 0 , 0 ) , datetime.datetime( 2015, 5, 30, 9, 0 , 0 ) ) ] ,
		4 : [ 	( datetime.datetime( 2015, 6, 6 , 0 , 0 , 0 )  , datetime.datetime( 2015, 6 , 8 , 0 , 0, 0 ) ) , 
			( datetime.datetime( 2015, 6, 13 , 0 , 0 , 0 ) , datetime.datetime( 2015, 6 , 15 , 0 , 0, 0 ) ) ,
			( datetime.datetime( 2015, 6, 20, 0 , 0 , 0 )  , datetime.datetime( 2015, 6, 22, 0, 0, 0 )  ) ] ,
		5 : [	( datetime.datetime( 2015, 6, 1 , 0 , 0 , 0 )  , datetime.datetime( 2015, 6 , 6 , 0 , 0, 0 ) ) ,
			( datetime.datetime( 2015, 6, 8 , 0 , 0 , 0 )  , datetime.datetime( 2015, 6 , 13 , 0 , 0, 0 ) ) ,
			( datetime.datetime( 2015, 6, 15, 0, 0, 0 )    , datetime.datetime( 2015, 6, 20 , 0, 0, 0 ) ) ]
	}

def getAHUGroundTruth(filename):
	ahumapping = {}
	lines = open(filename).readlines()
	for line in lines:
	    room = line.strip().split(",")[0].strip()
	    ahu = int(line.strip().split(",")[-1].strip())
	    ahumapping[room] = ahu

	return ahumapping


def readMetadata(filename):
	inf = open(filename)	
	metadata = json.load(inf)
	return metadata


'''
END OF GLOBAL DATA
'''


def calcStats(room, dataDir , metadata):

	if "reheat_valve_position" not in metadata[room]:
		return

	reheatPointName = metadata[room]["reheat_valve_position"]
	reheatTs = Timeseries( dataDir + "/" + reheatPointName , reheatPointName, 15 )  
	reheatTs.addAllPeriods( periods )
	reheat_means = {}
	for i in [ 2 , 3 ]:
		mean = reheatTs.getMean( i )[0]
		reheat_means[i] = mean
		
	if "supply_air_velocity" not in metadata[room]:
		return

	flowPointName = metadata[room]["supply_air_velocity"]
	flowTs = Timeseries( dataDir + "/" + flowPointName , flowPointName, 15 )  
	flowTs.addAllPeriods( periods )
	flow_means = {}
	for i in [ 2 , 3 ]:
		mean = flowTs.getMean( i )[0] 
		flow_means[i] = mean
	
	return 	(reheat_means[2] - reheat_means[3] , flow_means[2] - flow_means[3] )

def runExp( ahumapping, metadata, dataDir, outputfilename ):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	scatterPoints = { 1 : [] , 2 : [] , 3 : [] , 4 : [] , 5 : [] }
	colors = { 1 : 'b' , 2 : 'k' , 3 : 'r' , 4 : 'g' , 5 : 'y' }

	count = 0
	for room in metadata:
		count += 1
		try:
			print >> sys.stderr, "Doing room : ", room , "(%d/%d)" % (count,len(metadata))
			ret = calcStats( room , dataDir , metadata )
			if ret == None:
				continue
			(x1, y1) = ret
			scatterPoints[ahumapping[room]].append((x1, y1 ))

		except:
			raise
			print "Something wrong with room : ", room
			continue

	for i in range(1,6):
		xs = [ a for (a,b) in scatterPoints[i] ]
		ys = [ b for (a,b) in scatterPoints[i] ]
		ax.scatter( xs, ys, c=colors[i] , label = 'ahu-' + str(i))

	ax.set_xlabel("Reheat diff")	
	ax.set_ylabel("Flow diff")	
	plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
	plt.savefig(outputfilename + ".png", dpi=300 )


def init():
	if len(sys.argv) < 4:
		print "Usage python [file.py] < metadata_file > < ahumapping_file > <datadir> <outputplotname>"
		print "e.g python [file.py] room_metadata ahumapping-full data scatter-plot"
		exit()
	metadataFile = sys.argv[1]
	ahumappingFile = sys.argv[2]
	dataDir = sys.argv[3]
	outputFile = sys.argv[4] 
	metadata = readMetadata( metadataFile )
	ahumapping = getAHUGroundTruth( ahumappingFile )
	runExp( ahumapping, metadata, dataDir, outputFile )

if __name__ == "__main__":
	init()
	
