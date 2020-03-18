import numpy as np
from scipy.spatial.distance import euclidean
import os
import xml.etree.ElementTree as ET 
from xml.dom import minidom

from os.path import isfile, join
from fastdtw import fastdtw
import json

source_dir = "/Users/jdhurwitz/Documents/coding/GPS_comparison/data/"

class exercise:
	def __init__(self, eetype, date, filename):
		self.etype = eetype
		self.date = date
		self.latLonSamples = []
		self.deviceUsed = ""
		self.filename = filename

	def updateetype(self, eetype):
		self.etype = eetype

	def updateDate(self, date):
		self.date = date

	def addTuple(self, latlonTuple):
		self.latLonSamples.append(latlonTuple)



class GPS_Comparison:
	def __init__(self):
		#declare empty dict to use as hash for etype -> tuple(AW, SS)
		self.datasets = {
		'run': [[], []],
		'walk': [[], []],
		'bike': [[], []]
		}

		self.dtwOutputs = { #store dtw distance outputs in this hash. 
		'run': [],
		'walk': [],
		'bike': []
		}
	def extractLatLon(self, sample):
		lat = sample.attributes['lat'].value
		lon = sample.attributes['lon'].value
		return (lat, lon)

	def parseAndStore(self, etype, filepath):
		#Identify if the file is AW or SS, then parse accordingly and append to a the 
		#set that mmatches etype

		files_in_dir = [f for f in os.listdir(filepath) if isfile(join(filepath, f)) and f != '.DS_Store']
		for file in files_in_dir:
			#build xml tree
#			print(file)
			event_date = file[3:9] #pull the date of the filename
			lookup_dir = source_dir + etype + '/' + file
			xmldoc = minidom.parse(lookup_dir)

			e = exercise(etype, event_date, file)

			data_samples = xmldoc.getElementsByTagName("trkpt")


			#determine if apple
			if file[0:2] == 'aw':
				e.deviceUsed = "AW S5"
				for sample in data_samples:
					e.addTuple(self.extractLatLon(sample))
				self.datasets[etype][0].append(e)

			#determine if SS
			elif file[0:2] == 'ss':
				e.deviceUsed = "Active 2"
				for sample in data_samples:
					e.addTuple(self.extractLatLon(sample))
				self.datasets[etype][1].append(e)


			#dirty hard coding for garmin edge
			elif file[0:2] == 'ed': #garmin edge
				e.deviceUsed = "Garmin Edge 1030"
				for sample in data_samples:
					e.addTuple(self.extractLatLon(sample))
				self.datasets[etype][0].append(e)

			#dirty hard coding to compare garmin to garmin
			elif file[0:2] == 'fn': #garmin fenix 5
				e.deviceUsed = "Garmin Fenix 5"
				for sample in data_samples:
					e.addTuple(self.extractLatLon(sample))
				self.datasets[etype][1].append(e)


	def importData(self, dir=source_dir):
		#find both AW and SS data in directory
		for folder in os.listdir(source_dir):
			#check if DS_Store
			if folder is '.DS_Store':
				continue
			elif folder == 'run': 
				r_dir = source_dir + 'run'
				self.parseAndStore(etype='run', filepath=r_dir)
			elif folder  == 'walk':
				w_dir = source_dir + 'walk'
				self.parseAndStore(etype='walk', filepath=w_dir)
			elif folder  == 'bike':
				b_dir = source_dir + 'bike'
				self.parseAndStore(etype='bike', filepath=b_dir)

	def findExerciseByDate(self, exerciseList, date):
		for e in exerciseList:
			if e.date == date:
				return e



	def applyDtw(self, series1, series2):
		#apply dynamic time warping to create similarity metric between two datasets
		distance, path = fastdtw(series1, series2, dist=euclidean)
		return distance, path


	def runAllDtw(self):
		#go through all dataset etypes in dataset dict

		for key in self.datasets:
			#check to see if size of series for ss and aw are equal
			if len(self.datasets[key][0]) == len(self.datasets[key][1]):
				print("match")
			else:
				print("mismatch")

			num_series = len(self.datasets[key][0])
			for i in range(num_series):
				first_dataset = self.datasets[key][0][i]
				second_dataset = self.findExerciseByDate(self.datasets[key][1], first_dataset.date)

				date = first_dataset.date

				aw_series = first_dataset.latLonSamples
				ss_series = second_dataset.latLonSamples

				distance, path = self.applyDtw(aw_series, ss_series)

				result_tuple = (date, distance)
				self.dtwOutputs[key].append(result_tuple)


	def printOutputs(self, lineByline=False):
		if lineByline:
			print(json.dumps(self.dtwOutputs, indent=4))
		else:
			print(self.dtwOutputs)


if __name__ == "__main__":
	c = GPS_Comparison()

	c.importData()
	c.runAllDtw()

	c.printOutputs(lineByline=True)




