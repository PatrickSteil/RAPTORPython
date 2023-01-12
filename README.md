# RAPTOR in Python
RAPTIOR implemented in Python - reads timetable information from a GTFS directory.

Implemented is the RAPTOR algorithm [https://www.microsoft.com/en-us/research/wp-content/uploads/2012/01/raptor_alenex.pdf], a route planning algorithm that calculates Pareto Optimal journeys in terms of arrival time and the number of transfers. RAPTOR can easily be extended to answer multicriteria problems. Range queries are also easy to calculate. RAPTOR works on the timetable and not on any graph. As a timetable, a GTFS directory (with all essential files) is read in and internally "suitably" stored.

Quick overview on how to use RAPTOR:

```Python
import raptor
import json # for this purpose
## loading
data = raptor.RAPTORData(PATH_TO_GTFS_DIR)
data.readGTFS()
data.saveToDisk(PATH_TO_SAVE_RAPTOR_OBJECTS)
# data.loadFromDisk(PATH_TO_SAVE_RAPTOR_OBJECTS") # if you want to laod the previously computed timetable information

## query
data.run(source, target, depTime) # source, target are the stop_id's inside the GTFS/stops.txt file, depTime in seconds
j = data.getAllJourneys()
print(json.dumps(j, indent=4)) # to pretty print
```
A result (here from "Erfurt, Hugo-John-Straße" to "Erfurt, Hauptbahnhof" departing at 10:00) could be:

```JSON
{
    "2": [
        {
            "DepartureTime": "10:23:00",
            "ArrivalTime": "10:25:00",
            "FromStop": "Erfurt, Hugo-John-Straße",
            "ToStop": "Erfurt, Grubenstraße",
            "RouteId": "2866_3"
        },
        {
            "DepartureTime": "10:25:00",
            "ArrivalTime": "10:39:00",
            "FromStop": "Erfurt, Grubenstraße",
            "ToStop": "Erfurt, Hauptbahnhof",
            "RouteId": "2843_0"
        }
    ],
    "3": [
        {
            "DepartureTime": "10:23:00",
            "ArrivalTime": "10:25:00",
            "FromStop": "Erfurt, Hugo-John-Straße",
            "ToStop": "Erfurt, Grubenstraße",
            "RouteId": "2866_3"
        },
        {
            "DepartureTime": "10:25:00",
            "ArrivalTime": "10:27:00",
            "FromStop": "Erfurt, Grubenstraße",
            "ToStop": "Erfurt, Salinenstraße",
            "RouteId": "2843_0"
        },
        {
            "DepartureTime": "10:27:00",
            "ArrivalTime": "10:38:00",
            "FromStop": "Erfurt, Salinenstraße",
            "ToStop": "Erfurt, Hauptbahnhof",
            "RouteId": "2867_3"
        }
    ]
}

```
Also, you can run range queries (aka rRAPTOR) using `data.run(source, target, earliestDepTime, latestDepTime)`.
