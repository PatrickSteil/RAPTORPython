from scipy import spatial
import csv
import geopy.distance

coords = []
stop_ids = []

avgMPerS = 1.3

dataset = "data/s_re"

def getWalkingDist(coordsA, coordsB):
	return geopy.distance.geodesic(coordsA, coordsB).m


with open(dataset + "/stops.txt", "r", encoding='utf-8-sig') as csvFile:
	reader = csv.reader(csvFile, skipinitialspace=True)
	stopIdIndex = -1
	latIndex = -1
	lonIndex = -1

	for line in reader:
		if (stopIdIndex == -1):
			stopIdIndex = line.index("stop_id")
			latIndex = line.index("stop_lat")
			lonIndex = line.index("stop_lon")
		else:
			stop_ids.append(line[stopIdIndex])
			coords.append([float(line[latIndex]), float(line[lonIndex])])

kd_tree = spatial.KDTree(coords)

transfers = []

with open(dataset + "/transfers.txt", "w", encoding='utf-8-sig') as csvFile:
	writer = csv.writer(csvFile, skipinitialspace=True)
	writer.writerow(["from_stop_id", "to_stop_id", "transfer_type", "min_transfer_time"])

	for [a, b] in list(kd_tree.query_pairs(r=0.02)):
		time = int(getWalkingDist(coords[a], coords[b]) / avgMPerS)
		writer.writerows([stop_ids[a], stop_ids[b], 2, time])
		writer.writerows([stop_ids[b], stop_ids[a], 2, time])
