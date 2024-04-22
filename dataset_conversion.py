#!/usr/bin/python2
#-*- coding: utf-8 -*-

#  The MIT License (MIT)
#
#  Copyright (c) 2014 Federal Office of Topography swisstopo, Wabern, CH and Aaron Schmocker
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#

# WGS84 <-> LV03 converter based on the scripts of swisstopo written for python2.7
# Aaron Schmocker [aaron@duckpond.ch]
# vim: tabstop=4 shiftwidth=4 softtabstop=4 expandtab

# Source: http://www.swisstopo.admin.ch/internet/swisstopo/en/home/topics/survey/sys/refsys/projections.html (see PDFs under "Documentation")
# Updated 9 dec 2014
# Please validate your results with NAVREF on-line service: http://www.swisstopo.admin.ch/internet/swisstopo/en/home/apps/calc/navref.html (difference ~ 1-2m)

import pandas as pd
import csv
import math
from pyproj import Geod


class GPSConverter(object):
	'''
	GPS Converter class which is able to perform convertions between the
	CH1903 and WGS84 system.
	'''

	# Convert CH y/x/h to WGS height
	def CHtoWGSheight(self, y, x, h):
		# Axiliary values (% Bern)
		y_aux = (y - 600000) / 1000000
		x_aux = (x - 200000) / 1000000
		h = (h + 49.55) - (12.60 * y_aux) - (22.64 * x_aux)
		return h

	# Convert CH y/x to WGS lat
	def CHtoWGSlat(self, y, x):
		# Axiliary values (% Bern)
		y_aux = (y - 600000) / 1000000
		x_aux = (x - 200000) / 1000000
		lat = (16.9023892 + (3.238272 * x_aux)) + \
			  - (0.270978 * pow(y_aux, 2)) + \
			  - (0.002528 * pow(x_aux, 2)) + \
			  - (0.0447 * pow(y_aux, 2) * x_aux) + \
			  - (0.0140 * pow(x_aux, 3))
		# Unit 10000" to 1" and convert seconds to degrees (dec)
		lat = (lat * 100) / 36
		return lat

	# Convert CH y/x to WGS long
	def CHtoWGSlng(self, y, x):
		# Axiliary values (% Bern)
		y_aux = (y - 600000) / 1000000
		x_aux = (x - 200000) / 1000000
		lng = (2.6779094 + (4.728982 * y_aux) + \
			   + (0.791484 * y_aux * x_aux) + \
			   + (0.1306 * y_aux * pow(x_aux, 2))) + \
			  - (0.0436 * pow(y_aux, 3))
		# Unit 10000" to 1" and convert seconds to degrees (dec)
		lng = (lng * 100) / 36
		return lng

	# Convert decimal angle (° dec) to sexagesimal angle (dd.mmss,ss)
	def DecToSexAngle(self, dec):
		degree = int(math.floor(dec))
		minute = int(math.floor((dec - degree) * 60))
		second = (((dec - degree) * 60) - minute) * 60
		return degree + (float(minute) / 100) + (second / 10000)

	# Convert sexagesimal angle (dd.mmss,ss) to seconds
	def SexAngleToSeconds(self, dms):
		degree = 0
		minute = 0
		second = 0
		degree = math.floor(dms)
		minute = math.floor((dms - degree) * 100)
		second = (((dms - degree) * 100) - minute) * 100
		return second + (minute * 60) + (degree * 3600)

	# Convert sexagesimal angle (dd.mmss) to decimal angle (degrees)
	def SexToDecAngle(self, dms):
		degree = 0
		minute = 0
		second = 0
		degree = math.floor(dms)
		minute = math.floor((dms - degree) * 100)
		second = (((dms - degree) * 100) - minute) * 100
		return degree + (minute / 60) + (second / 3600)

	# Convert WGS lat/long (° dec) and height to CH h
	def WGStoCHh(self, lat, lng, h):
		lat = self.DecToSexAngle(lat)
		lng = self.DecToSexAngle(lng)
		lat = self.SexAngleToSeconds(lat)
		lng = self.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000
		lng_aux = (lng - 26782.5) / 10000
		h = (h - 49.55) + (2.73 * lng_aux) + (6.94 * lat_aux)
		return h

	# Convert WGS lat/long (° dec) to CH x
	def WGStoCHx(self, lat, lng):
		lat = self.DecToSexAngle(lat)
		lng = self.DecToSexAngle(lng)
		lat = self.SexAngleToSeconds(lat)
		lng = self.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000
		lng_aux = (lng - 26782.5) / 10000
		x = ((200147.07 + (308807.95 * lat_aux) + \
			  + (3745.25 * pow(lng_aux, 2)) + \
			  + (76.63 * pow(lat_aux, 2))) + \
			 - (194.56 * pow(lng_aux, 2) * lat_aux)) + \
			+ (119.79 * pow(lat_aux, 3))
		return x

	# Convert WGS lat/long (° dec) to CH y
	def WGStoCHy(self, lat, lng):
		lat = self.DecToSexAngle(lat)
		lng = self.DecToSexAngle(lng)
		lat = self.SexAngleToSeconds(lat)
		lng = self.SexAngleToSeconds(lng)
		# Axiliary values (% Bern)
		lat_aux = (lat - 169028.66) / 10000
		lng_aux = (lng - 26782.5) / 10000
		y = (600072.37 + (211455.93 * lng_aux)) + \
			- (10938.51 * lng_aux * lat_aux) + \
			- (0.36 * lng_aux * pow(lat_aux, 2)) + \
			- (44.54 * pow(lng_aux, 3))
		return y

	def LV03toWGS84(self, east, north, height):
		'''
		Convert LV03 to WGS84 Return am array of double that contain lat, long,
		and height
		'''
		d = []
		d.append(self.CHtoWGSlat(east, north))
		d.append(self.CHtoWGSlng(east, north))
		d.append(self.CHtoWGSheight(east, north, height))
		return d

	def LV03toWGS84V2(self, east, north):
		'''
		ADDED FUNCTION BY JUSTINE SOMMERLATT
		2nd version of the LV03 to WSG84 conversion function
		Converts LV03 to WGS84 coordinates
		Returns an array of double that contain lat and long only
		'''
		d = []
		d.append(self.CHtoWGSlat(east, north))
		d.append(self.CHtoWGSlng(east, north))
		return d

	def WGS84toLV03(self, latitude, longitude, ellHeight):
		'''
		Convert WGS84 to LV03 Return an array of double that contaign east,
		north, and height
		'''
		d = []
		d.append(self.WGStoCHy(latitude, longitude))
		d.append(self.WGStoCHx(latitude, longitude))
		d.append(self.WGStoCHh(latitude, longitude, ellHeight))
		return d

def wgs84_dist(lat1, lon1, lat2, lon2):
	"""
	Calculates distance based on WGS84 Geode
	 lat1, lon1 = origin
	 lat2, lon2 = destination
	"""

	if lat1 > 1000:
		print('[fs-utils] - ERROR: Wrong input. Needs to be decimal degrees ')

	g = Geod(ellps='WGS84')
	az12, az21, dist = g.inv(lat1, lon1, lat2, lon2)
	return dist

# Author : JUSTINE SOMMERLATT
# Code to convert the original dataforavalanchesizemodeldevelopment dataset (https://envidat.ch/#/metadata/avalanche-prediction-snowpack-simulations)
# into a usable one with WGS84 coordinates instead of LV03 coordinates
# define the nearest IMI station from each avalanche


if __name__ == "__main__":

	converter = GPSConverter()

	station_code = []
	station_lat = []
	station_lon = []

	# Open the IMIs dataset which contains all the IMI stations information (such as name and coordinates)
	with open('stations.csv', "r", encoding='utf-8-sig') as File0:
		reader = csv.reader(File0, delimiter=',')
		# Store the code and the coordinates of each station to enables making the comparison
		for count, line in enumerate(reader, 1):
			if count != 1:
				station_code.append(line[1])
				station_lat.append(line[5])
				station_lon.append(line[4])

	# Define the different lists that will be in the new dataset
	triggerDateTime = []
	coordX = []
	coordY = []
	startZoneElevation = []
	startZoneAspect = []
	fractureThicknessMean = []
	size = []
	lat = []
	lon = []
	# nearest IMIS id
	IMIScode = []
	# nearest IMIS latitude
	IMISlat = []
	# nearest IMIS longitude
	IMISlon = []

	# Open the original dataset with the avalanches
	with open('avalanches_thousand.csv', "r", encoding='utf-8-sig') as File:
		reader = csv.reader(File, delimiter=';')

		# Store all the data in the corresponding lists
		for count, line in enumerate(reader, 1):
			if count != 1:
				print(line)
				triggerDateTime.append(line[0])
				coordX.append(line[1])
				coordY.append(line[2])
				startZoneElevation.append(line[3])
				startZoneAspect.append(line[4])
				fractureThicknessMean.append(line[5])
				size.append(line[6])
				# Convert the avalanche LV03 coordinates to WGS84
				lv03 = [line[2], line[1], line[3]]
				wgs84 = converter.LV03toWGS84V2(float(lv03[0]), float(lv03[1]))
				lat.append(wgs84[0])
				lon.append(wgs84[1])

				# Calculate the distances between each IMIS and the avalanche to define the nearest one
				nearest_IMIS = station_code[0]
				best_distance = wgs84_dist(wgs84[0], wgs84[1], station_lat[0], station_lon[0])
				best_lat = station_lat[0]
				best_lon = station_lon[0]
				# Calculate for each station
				for i in range(len(station_code)-1):
					distance = wgs84_dist(wgs84[0], wgs84[1], station_lat[i+1], station_lon[i+1])
					if distance < best_distance:
						best_distance = distance
						best_lat = station_lat[i+1]
						best_lon = station_lon[i+1]
						nearest_IMIS = station_code[i+1]

				# Keep only the nearest one
				IMIScode.append(nearest_IMIS)
				IMISlat.append(best_lat)
				IMISlon.append(best_lon)

	# Define all the columns for the new dataset
	col1 = "triggerDateTime"
	col2 = "coordX"
	col3 = "coordY"
	col4 = "startZoneElevation"
	col5 = "startZoneAspect"
	col6 = "fractureThicknessMean"
	col7 = "size"
	col8 = "lat"
	col9 = "lon"
	col10 = "IMIScode"
	col11 = "IMISlat"
	col12 = "IMISlon"
	# Write into a new Excel file
	data = pd.DataFrame({col1: triggerDateTime, col2: coordX, col3: coordY, col4: startZoneElevation, col5: startZoneAspect, col6: fractureThicknessMean, col7: size, col8: lat, col9: lon, col10: IMIScode, col11: IMISlat, col12: IMISlon})
	data.to_excel("dataset.xlsx", sheet_name="sheet1", index=False)