import numpy as np
from scipy.spatial.distance import euclidean
import os
import xml.etree.ElementTree as ET 
from xml.dom import minidom

from os.path import isfile, join
from fastdtw import fastdtw

source_dir = "/Users/jdhurwitz/Documents/coding/GPS_comparison/data/"

class GPS_Comparison:
	def __init__(self):
		#declare empty dict to use as hash for type -> tuple(AW, SS)
		self.datasets = {
		'run': ([],[]),
		'walk': ([],[]),
		'bike': ([], [])
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

	def parseAndStore(self, type, filepath):
		#Identify if the file is AW or SS, then parse accordingly and append to a the 
		#set that mmatches type

		files_in_dir = [f for f in os.listdir(filepath) if isfile(join(filepath, f)) and f != '.DS_Store']
		for file in files_in_dir:
			#build xml tree
#			print(file)
			lookup_dir = source_dir + type + '/' + file
			xmldoc = minidom.parse(lookup_dir)

			data_samples = xmldoc.getElementsByTagName("trkpt")
   
			list_to_append = []
			#determine if apple
			if file[0:2] == 'aw':
				for sample in data_samples:
					list_to_append.append(self.extractLatLon(sample))

				self.datasets[type][0].append(list_to_append)

			#determine if SS
			elif file[0:2] == 'ss':
				for sample in data_samples:
					list_to_append.append(self.extractLatLon(sample))	

				self.datasets[type][1].append(list_to_append)

	def importData(self, dir=source_dir):
		#find both AW and SS data in directory
		for folder in os.listdir(source_dir):
			#check if DS_Store
			if folder is '.DS_Store':
				continue
			elif folder == 'run': 
				r_dir = source_dir + 'run'
				self.parseAndStore(type='run', filepath=r_dir)
			elif folder  == 'walk':
				w_dir = source_dir + 'walk'
				self.parseAndStore(type='walk', filepath=w_dir)
			elif folder  == 'bike':
				b_dir = source_dir + 'bike'
				self.parseAndStore(type='bike', filepath=b_dir)




	def applyDtw(self, series1, series2):
		#apply dynamic time warping to create similarity metric between two datasets
		distance, path = fastdtw(series1, series2, dist=euclidean)
		return distance, path

	def runAllDtw(self):
		#go through all dataset types in dataset dict
		for key in self.datasets:
			#check to see if size of series for ss and aw are equal
			if len(self.datasets[key][0]) == len(self.datasets[key][1]):
				print("match")
			else:
				print("mismatch")

			num_series = len(self.datasets[key][0])
			for i in range(num_series):
				#get aw and ss series
				aw_series = self.datasets[key][0][i]
				ss_series = self.datasets[key][1][i]

				distance, path = self.applyDtw(aw_series, ss_series)
				self.dtwOutputs[key].append(distance)


if __name__ == "__main__":
	c = GPS_Comparison()

	c.importData()
	c.runAllDtw()

#	print(len(c.datasets['run']))
	print(c.dtwOutputs)




