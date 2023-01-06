# TransitRoutingPython
Public Transit Routing Algorithms implemented in Python. Reads timetable information from GTFS

## RAPTOR

Implemented is the RAPTOR algorithm, a route planning algorithm that calculates Pareto Optimal journeys in terms of arrival time and the number of transfers. RAPTOR can easily be extended to answer multicriteria problems. Range queries are also easy to calculate. RAPTOR works on the timetable and not on any graph. As a timetable, a GTFS directory (with all essential files) is read in and internally "suitably" stored.

Quick overview on how to use RAPTOR:

```Python
import raptor
import json # for this purpose
## loading
data = raptor.RAPTORData(PATH_TO_GTFS_DIR)
data.readGTFS()
data.saveToDisk(PATH_TO_SAVE_RAPTOR_OBJECTS)
# data.loadFromDisk(PATH_TO_SAVE_RAPTOR_OBJECTS")

## query
data.run(source, target, depTime) # source, target are the stop_id's inside the GTFS/stops.txt file, depTime in seconds
j = data.getAllJourneys()
print(json.dumps(j, indent=4)) # to pretty print
```
A result (here Erfurt, from 'Erfurt, Hugo-John-Straße' to 'Erfurt, Hauptbahnhof' departing at 10:00 could be:

```JSON
{
    "2": [
        {
            "DepartureTime": "10:23:00",
            "ArrivalTime": "10:25:00",
            "FromStop": "Erfurt, Hugo-John-Stra\u00dfe",
            "ToStop": "Erfurt, Grubenstra\u00dfe",
            "RouteId": "2866_3"
        },
        {
            "DepartureTime": "10:25:00",
            "ArrivalTime": "10:39:00",
            "FromStop": "Erfurt, Grubenstra\u00dfe",
            "ToStop": "Erfurt, Hauptbahnhof",
            "RouteId": "2843_0"
        }
    ],
    "3": [
        {
            "DepartureTime": "10:23:00",
            "ArrivalTime": "10:25:00",
            "FromStop": "Erfurt, Hugo-John-Stra\u00dfe",
            "ToStop": "Erfurt, Grubenstra\u00dfe",
            "RouteId": "2866_3"
        },
        {
            "DepartureTime": "10:25:00",
            "ArrivalTime": "10:27:00",
            "FromStop": "Erfurt, Grubenstra\u00dfe",
            "ToStop": "Erfurt, Salinenstra\u00dfe",
            "RouteId": "2843_0"
        },
        {
            "DepartureTime": "10:27:00",
            "ArrivalTime": "10:38:00",
            "FromStop": "Erfurt, Salinenstra\u00dfe",
            "ToStop": "Erfurt, Hauptbahnhof",
            "RouteId": "2867_3"
        }
    ]
}

```
