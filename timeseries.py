import sys
import os
from datetime import datetime
from datetime import timedelta
import numpy 
import pandas as pd

class Timeseries:
	series = {}
	name = None
	bucket = 15
	periods = {}
	def __init__(self, fileName, name, bucketSize , offset=0):
		
		lines = open(fileName).readlines()
		data = {}
		for line in lines:
			parts = line.strip().split(',')
			t = datetime.fromtimestamp(float(parts[0].strip()) - offset ) 
			v = float(parts[1].strip())
			data[t] = v
		self.bucket = bucketSize
		self.original_ts = pd.Series(data)
		self.resampled_ts = self.resample( self.bucket )
		
	def resample(self, bucket):
		newts = self.original_ts.resample(str(bucket) + 'min', how=numpy.mean)
		resampled_ts = newts.interpolate()
		return resampled_ts
	
	def addPeriod(self, index, startDate, endDate):
		if index not in self.periods:
			self.periods[index] = []
		self.periods[index].append( (startDate, endDate ) )

	def addAllPeriods( self, periods ):
		self.periods = periods.copy()

	def getBucket(self):
		return self.bucket
	
	def setBucket(self,bucket):
		self.bucket = bucket
		self.resampled_ts = self.resample( self.bucket )

	'''
	Returns a dict with required values
	'''

	def filterPeriod( self, periodNum ) :
		returnData = {}
		indices = self.resampled_ts.index
		for i in range(len(self.periods[periodNum])):
			startTime = self.periods[periodNum][i][0]
			endTime = self.periods[periodNum][i][1]
			result = {}
			for j in range(len(indices)):
				t = indices[j].to_datetime()
				if t < startTime or t > endTime:
					continue
				result[t] = self.resampled_ts[j]

			returnData.update(result)

		return returnData

	'''
	Returns mean, std for each day over a period
	'''

	def getPerDayMean( self, periodNum ):
		data = self.filterPeriod( periodNum )
		valuesByDay = {}
		for t in data:
			if t.day not in valuesByDay:
				valuesByDay[t.day] = []
			valuesByDay[t.day].append(data[t])

		resultsByDay = {}
		for day in valuesByDay:
			''' 
			Put a check in place to see whether you have a full day of data
			'''
			if len(valuesByDay[day]) != ( 24 * 60 ) / self.bucket :
				print "length of series only : ", len(valuesByDay[day])
				continue
			resultsByDay[day] = ( numpy.mean(valuesByDay[day]) , numpy.std(valuesByDay[day]) )

		return resultsByDay
	'''
	Returns overall mean and std over period 
	'''
	def getMean( self, periodNum ):
		data = self.filterPeriod( periodNum )
		values = [ data[t] for t in data ]
		return ( numpy.mean(values) , numpy.std(values) )

