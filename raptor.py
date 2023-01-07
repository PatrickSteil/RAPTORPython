#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import csv
import bisect
import pickle
from datetime import timedelta

## dirty hack
class KeyifyList(object):
	def __init__(self, inner, key):
		self.inner = inner
		self.key = key

	def __len__(self):
		return len(self.inner)

	def __getitem__(self, k):
		return self.key(self.inner[k])

def stringHHMMSSToSeconds(time):
	[h, m, s] = time.split(":")
	return (int(h) * 60 + int(m)) * 60 + int(s)

def secondsToHHMMSSString(sec):
	if (sec == float("inf")):
		return "inf"
	return str(timedelta(seconds=sec))

# advanced classes to look up things faster

class IndexedSet(object):
	def __init__(self, size):
		super(IndexedSet, self).__init__()
		self.size = size

		self.clear()

	def isEmpty(self):
		return (len(self.elements) == 0)

	def clear(self):
		self.visited = [False for _ in range(self.size)]
		self.elements = []

	def insert(self, element):
		if (not self.visited[element]):
			self.visited[element] = True
			self.elements.append(element)

	def getElements(self):
		return self.elements

	def contains(self, element):
		return self.visited[element]
		

class IndexedHash(IndexedSet):
	def __init__(self, size):
		IndexedSet.__init__(self, size)
		self.elements = {}
		self.clear()

	def clear(self):
		self.visited = [False for _ in range(self.size)]
		self.elements = {}

	def insert(self, element, addElement):
		if (not self.visited[element]):
			self.visited[element] = True
			self.elements[element] = addElement

	def getAdditionalElement(self, element):
		return self.elements[element]

	def setAdditionalElement(self, element, addElement):
		if (not self.visited[element]):
			self.elements[element] = addElement

	def getElements(self):
		return list(zip(self.elements.keys(), self.elements.values()))


# just classes to have an overview

class Transfer(object):
	def __init__(self, fromStopId, toStopId, duration):
		super(Transfer, self).__init__()
		self.fromStopId = fromStopId
		self.toStopId = toStopId
		self.duration = duration

	def __str__(self):
		return "From: " +  str(self.fromStopId) + ";To: " + str(self.toStopId) + ";Duration: " + str(self.duration)

class StopEvent(object):
	def __init__(self, depTime, arrTime):
		super(StopEvent, self).__init__()
		self.depTime = depTime
		self.arrTime = arrTime

class EarliestArrivalLabel(object):
	def __init__(self, arrTime = float("inf"), parentDepTime = float("inf"), parent = -1, usesRoute = False, routeId = None):
		super(EarliestArrivalLabel, self).__init__()
		self.arrTime = arrTime
		self.parentDepTime = parentDepTime
		self.parent = parent
		self.usesRoute = usesRoute
		self.routeId = routeId

	def __str__(self):
		return "ArrTime: " + secondsToHHMMSSString(self.arrTime) + ";ParentDepTime: " + secondsToHHMMSSString(self.parentDepTime) + ";Parent: " + str(self.parent) + ";UsesRoute: " + str(self.usesRoute) + ";RouteId: " + str(self.routeId)

class DepartureLabel(object):
	def __init__(self, depTime, stop):
		super(DepartureLabel, self).__init__()
		self.depTime = depTime
		self.stop = stop
		

# Now the main file
class RAPTORData(object):
	def __init__(self, directoryName):
		super(RAPTORData, self).__init__()
		self.directoryName = directoryName
		self.rounds = []
		self.earliestArrival = []
		self.resultJourney = []
		self.source = 0
		self.target = 0
		self.depTime = 0
		self.earliestDepTime = 0
		self.latestDepTime = 0
		self.stopsUpdatedByRoute = None
		self.stopsUpdatedByTransfer = None
		self.stopsReached = None

		## route contains routeId (from gtfs)
		self.routes = []

		## stopSequenceOfRoute[i] is a list of stops (sorted by stop sequence)
		self.stopSequenceOfRoute = []

		## stopEventsOfTrip[i] contains a list of StopEvents
		self.stopEventsOfTrip = []

		## route id of trip
		self.trips = []

		## first trip of route
		self.firstTripOfRoute = []

		## transfers, sorted by fromVertex
		self.transfers = []

		## stops, list of stopId (the gtfs stop id)
		self.stops = []
		self.stopNames = []
		self.routesOperatingAtStops = []

		self.collectedDepTimes = []

		self.stopMap = {}
		self.tripMap = {}
		self.tripOriginalRoute = {}
		self.routeMap = {}

	def numberOfRoutes(self):
		return len(self.stopSequenceOfRoute)

	def numberOfStops(self):
		return len(self.stops)

	def saveToDisk(self, filename):
		with open(filename + '.routes', 'wb') as file:
			pickle.dump(self.routes, file)
		with open(filename + '.stops', 'wb') as file:
			pickle.dump(self.stops, file)
		with open(filename + '.routesOperatingAtStops', 'wb') as file:
			pickle.dump(self.routesOperatingAtStops, file)
		with open(filename + '.stopNames', 'wb') as file:
			pickle.dump(self.stopNames, file)
		with open(filename + '.transfers', 'wb') as file:
			pickle.dump(self.transfers, file)
		with open(filename + '.routes', 'wb') as file:
			pickle.dump(self.routes, file)
		with open(filename + '.trips', 'wb') as file:
			pickle.dump(self.trips, file)
		with open(filename + '.stopMap', 'wb') as file:
			pickle.dump(self.stopMap, file)
		with open(filename + '.tripMap', 'wb') as file:
			pickle.dump(self.tripMap, file)
		with open(filename + '.stopEventsOfTrip', 'wb') as file:
			pickle.dump(self.stopEventsOfTrip, file)
		with open(filename + '.stopSequenceOfRoute', 'wb') as file:
			pickle.dump(self.stopSequenceOfRoute, file)
		with open(filename + '.firstTripOfRoute', 'wb') as file:
			pickle.dump(self.firstTripOfRoute, file)

	def loadFromDisk(self, filename):
		with open(filename + '.routes', 'rb') as file:
			self.routes = pickle.load(file)
		with open(filename + '.stops', 'rb') as file:
			self.stops = pickle.load(file)
		with open(filename + '.routesOperatingAtStops', 'rb') as file:
			self.routesOperatingAtStops = pickle.load(file)
		with open(filename + '.stopNames', 'rb') as file:
			self.stopNames = pickle.load(file)
		with open(filename + '.transfers', 'rb') as file:
			self.transfers = pickle.load(file)
		with open(filename + '.routes', 'rb') as file:
			self.routes = pickle.load(file)
		with open(filename + '.trips', 'rb') as file:
			self.trips = pickle.load(file)
		with open(filename + '.stopMap', 'rb') as file:
			self.stopMap = pickle.load(file)
		with open(filename + '.tripMap', 'rb') as file:
			self.tripMap = pickle.load(file)
		with open(filename + '.stopEventsOfTrip', 'rb') as file:
			self.stopEventsOfTrip = pickle.load(file)
		with open(filename + '.stopSequenceOfRoute', 'rb') as file:
			self.stopSequenceOfRoute = pickle.load(file)
		with open(filename + '.firstTripOfRoute', 'rb') as file:
			self.firstTripOfRoute = pickle.load(file)
	
	def readGTFS(self):
		self.__readStops()
		self.__readRoutes()
		self.__readTrips()
		self.__readTransfers()
		self.__readStopTimes()


	def __readStops(self):
		with open(self.directoryName + "/stops.txt", "r", encoding="utf-8") as csvFile:
			reader = csv.reader(csvFile, skipinitialspace=True)
			
			stopIdIndex = -1
			stopNameIndex = -1
			currentIndex = 0

			for line in reader:
				if (stopIdIndex == -1):
					stopIdIndex = line.index("stop_id")
					stopNameIndex = line.index("stop_name")
				else:
					self.stopMap[line[stopIdIndex]] = currentIndex
					self.stops.append(line[stopIdIndex])
					self.stopNames.append(line[stopNameIndex])
					self.routesOperatingAtStops.append([])
					currentIndex += 1

	def __readTransfers(self):
		with open(self.directoryName + "/transfers.txt", "r", encoding="utf-8") as csvFile:
			reader = csv.reader(csvFile, skipinitialspace=True)
			
			fromStopIdIndex = -1
			toStopIdIndex = -1
			durationIndex = -1
			transferTypeIndex = -1

			for line in reader:
				if (fromStopIdIndex == -1):
					fromStopIdIndex = line.index("from_stop_id")
					toStopIdIndex = line.index("to_stop_id")
					durationIndex = line.index("min_transfer_time")
					transferTypeIndex = line.index("transfer_type")
				else:
					if (int(line[transferTypeIndex]) == 2):
						self.transfers.append(Transfer(self.stopMap[line[fromStopIdIndex]], self.stopMap[line[toStopIdIndex]], int(line[durationIndex])))

		self.transfers.append(Transfer(float("inf"), float("inf"), float("inf")))

		self.transfers.sort(key=lambda x: x.fromStopId)

	def __readRoutes(self):
		with open(self.directoryName + "/routes.txt", "r", encoding="utf-8") as csvFile:
			reader = csv.reader(csvFile, skipinitialspace=True)
			
			routeIdIndex = -1

			currentIndex = 0

			for line in reader:
				if (routeIdIndex == -1):
					routeIdIndex = line.index("route_id")
				else:
					self.routes.append(line[routeIdIndex])
					self.routeMap[line[routeIdIndex]] = currentIndex

					currentIndex += 1

	def __readTrips(self):
		with open(self.directoryName + "/trips.txt", "r", encoding="utf-8") as csvFile:
			reader = csv.reader(csvFile, skipinitialspace=True)

			routeIdIndex = -1
			tripIdIndex = -1
			
			for line in reader:
				if (routeIdIndex == -1):
					routeIdIndex = line.index("route_id")
					tripIdIndex = line.index("trip_id")
				else:
					self.tripOriginalRoute[line[tripIdIndex]] = self.routeMap[line[routeIdIndex]]

	def __readStopTimes(self):
		## we need that map to map trips with same stopsequence 
		stopSequenceMap = {}

		with open(self.directoryName + "/stop_times.txt", "r", encoding="utf-8") as csvFile:
			reader = csv.reader(csvFile, skipinitialspace=True)
			
			tripIdIndex = -1
			stopIdIndex = -1
			arrTimeIndex = -1
			depTimeIndex = -1

			lastTripId = ""

			currentTripIndex = 0

			currentStopSeq = []

			for line in reader:
				if (tripIdIndex == -1):
					tripIdIndex = line.index("trip_id")
					stopIdIndex = line.index("stop_id")
				else:
					currentTrip = line[tripIdIndex]
					currentStopId = line[stopIdIndex]

					if (lastTripId == currentTrip):
						# same trip => add to stopSequence
						currentStopSeq.append(self.stopMap[currentStopId])
					else:
						# edge case for the beginning
						if (lastTripId == ""):
							lastTripId = currentTrip
						else:
							# if the stopsequence is already in the map, add trip to the new "route"
							if (tuple(currentStopSeq) in stopSequenceMap.keys()):
								stopSequenceMap[tuple(currentStopSeq)].append(lastTripId)
							else:
								stopSequenceMap[tuple(currentStopSeq)] = [lastTripId]
							# clear
							currentStopSeq = []
							lastTripId = currentTrip
							currentTripIndex += 1
			# add last stopSequence
			if (tuple(currentStopSeq) in stopSequenceMap.keys()):
				stopSequenceMap[tuple(currentStopSeq)].append(lastTripId)
			else:
				stopSequenceMap[tuple(currentStopSeq)] = [lastTripId]
			
			## now that we collected all the "same" trips into routes, we need to add the route ids
			self.trips = [0 for _ in range(currentTripIndex+1)]
			self.firstTripOfRoute = [0 for _ in range(len(list(stopSequenceMap.keys()))+1)]

			routeId = 0
			tripIndex = 0
			newRouteIds = []
			for key in stopSequenceMap:
				self.firstTripOfRoute[routeId] = tripIndex
				stopSeq = list(key)
				for i, stop in enumerate(stopSeq):
					self.routesOperatingAtStops[stop].append((routeId, i))
				newRouteIds.append(self.routes[self.tripOriginalRoute[stopSequenceMap[key][0]]])
				for tripId in stopSequenceMap[key]:
					self.trips[tripIndex] = routeId
					self.tripMap[tripId] = tripIndex 
					tripIndex += 1
				self.stopSequenceOfRoute.append(stopSeq)
				routeId += 1
			# sentinel
			self.firstTripOfRoute[routeId] = tripIndex
			self.routes = newRouteIds[:]

		with open(self.directoryName + "/stop_times.txt", "r", encoding="utf-8") as csvFile:
			reader = csv.reader(csvFile, skipinitialspace=True)

			self.stopEventsOfTrip = [[] for _ in range(currentTripIndex+1)]

			tripIdIndex = -1
			arrTimeIndex = -1
			depTimeIndex = -1

			for line in reader:
				if (tripIdIndex == -1):
					tripIdIndex = line.index("trip_id")
					arrTimeIndex = line.index("arrival_time")
					depTimeIndex = line.index("departure_time")
				else:
					currentTrip = line[tripIdIndex]
					currentArrTime = line[arrTimeIndex]
					currentDepTime = line[depTimeIndex]

					self.stopEventsOfTrip[self.tripMap[currentTrip]].append(StopEvent(stringHHMMSSToSeconds(currentDepTime), stringHHMMSSToSeconds(currentArrTime)))

		for route in range(self.numberOfRoutes()):
			# sort all trips of route by depTime and then arrTime
			lowerTrip = self.getFirstTripOfRoute(route)
			upperTrip = self.getLastTripOfRoute(route)
			copy = self.stopEventsOfTrip[lowerTrip:upperTrip][:]
			copy.sort(key=lambda x: (x[0].depTime, x[0].arrTime))
			self.stopEventsOfTrip[lowerTrip:upperTrip] = copy[:]

	## Helper
	def getFirstTripOfRoute(self, route):
		return self.firstTripOfRoute[route]

	def lengthOfRoute(self, route):
		return len(self.stopSequenceOfRoute[route])

	def getLastTripOfRoute(self, route):
		return self.firstTripOfRoute[route+1]

	def firstTransferOfStop(self, stop):
		return bisect.bisect_left(KeyifyList(self.transfers, lambda x: x.fromStopId), stop)

	def lastTransferOfStop(self, stop):
		return bisect.bisect_right(KeyifyList(self.transfers, lambda x: x.fromStopId), stop)

	def routesContainingStop(self, stop):
		return self.routesOperatingAtStops[stop]

	## Query stuff
	def clear(self):
		self.earliestArrival = [float("inf") for _ in self.stops]
		self.rounds = [[EarliestArrivalLabel() for _ in self.stops]]
		self.stopsUpdated = IndexedSet(self.numberOfStops())
		self.stopsReached = IndexedSet(self.numberOfStops())
		self.routesServingUpdatedStops = IndexedHash(self.numberOfRoutes())

	def startNewRound(self):
		self.rounds.append([EarliestArrivalLabel() for _ in self.stops])

	def currentRound(self):
		return self.rounds[-1]

	def previousRound(self):
		return self.rounds[-2]

	def relaxTransfers(self):
		self.routesServingUpdatedStops.clear()
		stopsUpdatedElements = self.stopsUpdated.getElements()[:]
		for stop in stopsUpdatedElements:
			for trans in self.transfers[self.firstTransferOfStop(stop):self.lastTransferOfStop(stop)]:
				if (self.updateArrivalTime(trans.toStopId, self.currentRound()[stop].arrTime + trans.duration)):
					self.stopsReached.insert(trans.toStopId)
					self.currentRound()[trans.toStopId].parent = stop
					self.currentRound()[trans.toStopId].usesRoute = False
					self.currentRound()[trans.toStopId].parentDepTime = self.currentRound()[stop].arrTime
					self.currentRound()[trans.toStopId].routeId = trans

	def collectRoutesServingUpdatedStops(self):
		for stop in self.stopsUpdated.getElements():
			arrivalTime = self.previousRound()[stop].arrTime
			for (route, stopIndex) in self.routesContainingStop(stop):
				if (stopIndex + 1 == self.lengthOfRoute(route)):
					continue
				if (self.stopEventsOfTrip[self.getLastTripOfRoute(route)-1][stopIndex].depTime < arrivalTime):
					continue
				if (self.routesServingUpdatedStops.contains(route)):
					self.routesServingUpdatedStops.setAdditionalElement(route, min(self.routesServingUpdatedStops.getAdditionalElement(route), stopIndex))
				else:
					self.routesServingUpdatedStops.insert(route, stopIndex)

	def updateArrivalTime(self, stopId, time):
		if (self.earliestArrival[self.target] <= time):
			return False
		if (self.earliestArrival[stopId] <= time):
			return False
		self.earliestArrival[stopId] = time
		self.currentRound()[stopId].arrTime = time
		self.stopsUpdated.insert(stopId)
		return True

	def initialize(self, rangeQuery=False):
		self.clear()
		if (rangeQuery):
			self.updateArrivalTime(self.source, self.sourceDepTime)
			self.currentRound()[self.source].parentDepTime = self.sourceDepTime
		else:
			self.updateArrivalTime(self.source, self.depTime)
			self.currentRound()[self.source].parentDepTime = self.depTime
		self.currentRound()[self.source].parent = self.source
		self.currentRound()[self.source].usesRoute = False
		self.currentRound()[self.source].routeId = None

	def run(self, sourceGTFSId, targetGTFSId, depTime):
		self.source = self.stopMap[sourceGTFSId]
		self.target = self.stopMap[targetGTFSId]
		self.depTime = depTime
		
		self.initialize()
		
		k = 0
		maxRounds = 16
		while (k < maxRounds and not self.stopsUpdated.isEmpty()):
			self.relaxTransfers()

			self.startNewRound()
			# collect all routes
			self.collectRoutesServingUpdatedStops()

			# scan all route collected earlier
			self.scanRoutes()
			k += 1

	def scanRoutes(self):
		self.stopsUpdated.clear()
		for (route, index) in self.routesServingUpdatedStops.getElements():
			firstTrip = self.getFirstTripOfRoute(route)
			trip = self.getLastTripOfRoute(route) - 1

			currentStopIndex = index
			parentIndex = index
			stop = self.stopSequenceOfRoute[route][currentStopIndex]

			# loop over the stops
			while (currentStopIndex < self.lengthOfRoute(route) - 1):
				# find trip to "hop on"
				while (trip > firstTrip and self.stopEventsOfTrip[(trip-1)][currentStopIndex].depTime >= self.previousRound()[stop].arrTime):
					trip -= 1
					parentIndex = currentStopIndex
				
				currentStopIndex += 1
				stop = self.stopSequenceOfRoute[route][currentStopIndex]

				if (self.updateArrivalTime(stop, self.stopEventsOfTrip[trip][currentStopIndex].arrTime)):
					self.stopsReached.insert(stop)
					self.currentRound()[stop].parent = self.stopSequenceOfRoute[route][parentIndex]
					self.currentRound()[stop].usesRoute = True
					self.currentRound()[stop].parentDepTime = self.stopEventsOfTrip[trip][parentIndex].depTime
					self.currentRound()[stop].routeId = route

				currentStopIndex += 1


	def getResult(self):
		result = []
		bestArrTime = float("inf")
		for i in range(len(self.rounds)):
			if (self.rounds[i][self.target].arrTime < bestArrTime):
				bestArrTime = self.rounds[i][self.target].arrTime
				result.append([i, self.rounds[i][self.target]])
		return result

	def getAllJourneys(self):
		journeys = {}
		for i in range(len(self.rounds)):
			if (self.rounds[i][self.target].arrTime == float("inf")):
				continue
			journeys[i] = self.getJourney(i, self.target)
		return journeys

	def transformEAToJourney(self, ea, currentStop):
		j = {
			"DepartureTime": secondsToHHMMSSString(ea.parentDepTime),
			"ArrivalTime": secondsToHHMMSSString(ea.arrTime),
			"FromStop": str(self.stopNames[ea.parent]),
			"ToStop": str(self.stopNames[currentStop])
		}
		if (ea.usesRoute):
			j["RouteId"] = self.routes[ea.routeId]
		return j

	def getJourney(self, roundIndex, stop):
		if (self.rounds[roundIndex][stop].arrTime == float("inf")):
			return []

		currentStop = stop
		ea = self.rounds[roundIndex][currentStop]

		journey = []
		journey.append(self.transformEAToJourney(ea, currentStop))
		currentStop = ea.parent

		while (currentStop != self.source and roundIndex > 0):
			if (currentStop == -1):
				break
			if (ea.usesRoute):
				roundIndex -= 1
			ea = self.rounds[roundIndex][currentStop]
			journey.append(self.transformEAToJourney(ea, currentStop))
			currentStop = ea.parent
		return journey[::-1]

	## range query

	def findDurationOfTransfer(self, fromStopId, toStopId):
		for transfer in self.transfers[self.firstTransferOfStop(fromStopId):self.lastTransferOfStop(toStopId)]:
			if (transfer.toStopId == toStopId):
				return transfer.duration
		return float("inf")

	def addDepartureLabel(self, stop, depTime):
		self.currentRound()[stop].depTime = depTime
		self.currentRound()[stop].parent = self.source
		self.currentRound()[stop].usesRoute = False
		self.currentRound()[stop].parentDepTime = self.sourceDepTime
		self.currentRound()[stop].routeId = None

	def run(self, sourceGTFSId, targetGTFSId, earliestDepTime, latestDepTime):
		self.source = self.stopMap[sourceGTFSId]
		self.target = self.stopMap[targetGTFSId]
		self.earliestDepTime = earliestDepTime
		self.latestDepTime = latestDepTime

		self.sourceDepTime = 0
		self.resultJourney = []

		self.collectDepartureTimes()
		
		maxRounds = 16
		i = 0
		while (i < len(self.collectedDepTimes)):
			self.sourceDepTime = self.collectedDepTimes[i].depTime
			self.initialize(True)

			self.stopsReached.clear()

			transferTime = self.findDurationOfTransfer(self.source, self.collectedDepTimes[i].stop)
			if (self.collectedDepTimes[i].stop == self.source):
				transferTime = 0
			self.addDepartureLabel(self.collectedDepTimes[i].stop, self.collectedDepTimes[i].depTime + transferTime)

			while (i+1 < len(self.collectedDepTimes) and self.collectedDepTimes[i].depTime == self.collectedDepTimes[i+1].depTime):
				transferTime = self.findDurationOfTransfer(self.source, self.collectedDepTimes[i].stop)
				if (self.collectedDepTimes[i].stop == self.source):
					transferTime = 0
				self.addDepartureLabel(self.collectedDepTimes[i].stop, self.collectedDepTimes[i].depTime + transferTime)
				i += 1
			i += 1

			k = 0
			while (k < maxRounds and not self.stopsUpdated.isEmpty()):
				self.relaxTransfers()

				self.startNewRound()

				# collect all routes
				self.collectRoutesServingUpdatedStops()

				# scan all route collected earlier
				self.scanRoutes()
				k += 1

			if (self.stopsReached.contains(self.target)):
				self.resultJourney.append(self.getAllJourneys())
		return self.resultJourney
			

	def collectDepartureTimes(self):
		self.collectedDepTimes = []

		for route in range(self.numberOfRoutes()):
			for trip in self.stopEventsOfTrip[self.getFirstTripOfRoute(route):self.getLastTripOfRoute(route)]:
				for stopSeq, stop in enumerate(self.stopSequenceOfRoute[route]):
					if (stopSeq + 1 == len(self.stopSequenceOfRoute[route])):
						continue
					if (trip[stopSeq].depTime < self.earliestDepTime or trip[stopSeq].depTime > self.latestDepTime):
						continue
					transferTime = self.findDurationOfTransfer(stop, self.source)
					if (stop == self.source or transferTime < float("inf")):
						# find all depTime in range [self.earliestDepTime, self.latestDepTime]
						self.collectedDepTimes.append(DepartureLabel(trip[stopSeq].depTime, stop))
		self.collectedDepTimes.sort(key=lambda x : x.depTime, reverse=True)
