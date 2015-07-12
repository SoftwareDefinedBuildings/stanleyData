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
		2 : [ 	( datetime.datetime( 2015, 6, 22, 0 , 0 , 0 ) , datetime.datetime( 2015, 6, 22, 22, 0 , 0 ) ) ] ,
		3 : [ 	( datetime.datetime( 2015, 6, 23, 0 , 0 , 0 ) , datetime.datetime( 2015, 6, 23, 22, 0 , 0 ) ) ] ,
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


def calcStats(room, dataDir , metadata , periodNum):

	if "reheat_valve_position" not in metadata[room] or "supply_air_velocity" not in metadata[room]:
		return

	reheatPointName = metadata[room]["reheat_valve_position"]
	reheatTs = Timeseries( dataDir + "/" + reheatPointName , reheatPointName, 15 , 11 * 60 * 60 )  
	reheatTs.addAllPeriods( periods )

	flowPointName = metadata[room]["supply_air_velocity"]
	flowTs = Timeseries( dataDir + "/" + flowPointName , flowPointName, 15 , 11 * 60 * 60 )  
	flowTs.addAllPeriods( periods )


	sensors = [ reheatTs, flowTs ]
	( centroids, stds ) = centoidAndCI( periodNum , sensors )

	return ( centroids, stds ) 

'''
	Input : period ( weekday, weekend , whatever )
		sensors : Array of Timeseries whose centroid you want to get [ reheat , flow ]
		
	Output : vector of centroids
	STA__101__ART, STA__101__RVP , STA_101___SVEL
	Array ( Timeseries(STA__101__ART) , Timeseries(STA__101__RVP) , Timeseries(STA_101___SVEL) )
'''

def centoidAndCI(periodNum, sensors):

	print sensors
	data = {}
	for sensor in sensors:
		data[sensor.name] = sensor.filterPeriod( periodNum )

	tuples = {}

	# Getting the list of all timestamps for a particular sensor
	timestamps = []
	for t in data[ sensors[0].name ]:
		timestamps.append(t)

	for t in timestamps:
		arr = []
		for sensor in sorted(data):
			if t in data[sensor]:
				arr.append(data[sensor][t])

		if len(arr) == len(sensors):
			tuples[t] = list(arr)

	days = {}
	for t in tuples:
		day = t.day
		if day not in days:
			days[day] = []
		days[day].append(tuples[t])

	centroids = [ numpy.mean(days[day] , axis=0) for day in days ]
	stds = [ numpy.std(days[day], axis=0) for day in days ]

	return ( centroids, stds )


def runExp( ahumapping, metadata, dataDir, outputfilename ):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	scatterPoints = { 1 : [] , 2 : [] , 3 : [] , 4 : [] , 5 : [] }
	colors = { 1 : 'b' , 2 : 'k' , 3 : 'r' , 4 : 'g' , 5 : 'y' }

	count = 0
	for room in metadata:
		if room != "100":
			continue
		count += 1
		try:
			print >> sys.stderr, "Doing room : ", room , "(%d/%d)" % (count,len(metadata))
			for period in [ 2, 3 , 5 ]:
				ret = calcStats( room , dataDir , metadata , period)
				if ret == None:
					continue
				(centroids , cis) = ret
				xvalues = numpy.zeros(len(centroids))
				yvalues = numpy.zeros(len(centroids))
				xerrs = numpy.zeros(len(centroids))
				yerrs = numpy.zeros(len(centroids))

				for i in range(len(centroids)):
					xvalues[i] = centroids[i][0]
					yvalues[i] = centroids[i][1]

					xerrs[i] = cis[i][0]
					yerrs[i] = cis[i][1]
					print "Day : ", i , "xvalue , yvalue , xerr, yerr " , xvalues[i], yvalues[i], xerrs[i], yerrs[i]	
					#ax.errorbar( xerr, yerr, xerr=[ [ xvalue - xerr ] , [ xvalue + xerr] ] , yerr=[ [ yvalue - yerr] , [yvalue + yerr] ], fmt ='--o')		
					if period==2:
						#ax.scatter(xvalues, yvalues, c='g', s=80)
						ax.errorbar( xvalues, yvalues, marker='o',c = 'g', xerr=2*xerrs, yerr=2*yerrs , linestyle='none' )
					if period==3:
						#ax.scatter(xvalues, yvalues, c='r', s=80)
						ax.errorbar( xvalues, yvalues, marker='o',c = 'r',  xerr=2*xerrs, yerr=2*yerrs , linestyle='none' )
					if period==5:
						#ax.scatter(xvalues, yvalues, c='b', s=20)
						ax.errorbar( xvalues, yvalues, marker='o',c = 'y',  xerr=2*xerrs, yerr=2*yerrs , linestyle='none')	
			#print xvalues, yvalues
				
			#ax.scatter( xvalues, yvalues )
			#ax.errorbar( xvalues, yvalues, xerr=[ xerrs, xvalues + xerrs ], yerr=[ yvalues - yerrs, yvalues + yerrs ] )	
			#ax.errorbar( xvalues, yvalues, marker='o', s=20, xerr=2*xerrs, yerr=2*yerrs ) 
			plt.show()
			break	
		except:
			raise
			print "Something wrong with room : ", room
			continue


def init():
	#if len(sys.argv) < 4:
	#	print "Usage python [file.py] < metadata_file > < ahumapping_file > <datadir> <outputplotname>"
	#		print "e.g python [file.py] room_metadata ahumapping-full data scatter-plot"
	#	exit()
	metadataFile = "room_metadata"
	ahumappingFile = "ahumapping-full"
	dataDir = "../data"
	outputFile = "scatter"
	metadata = readMetadata( metadataFile )
	ahumapping = getAHUGroundTruth( ahumappingFile )
	runExp( ahumapping, metadata, dataDir, outputFile )

if __name__ == "__main__":
	init()
		
