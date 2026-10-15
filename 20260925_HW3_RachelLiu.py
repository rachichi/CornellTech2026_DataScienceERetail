# ---------------------------------------------------------------------------
# PROMPT
# Write a computer program that simulates the system for a day. Turn in your
# commented computer program. Make sure that your computer program computes the statistics
# of interest. (Hint: Note that the customers travel between each origin-destination pair with
# equal probability. To sample the origin (or destination) of a customer, you can use the Python
# routine random.randint(a, b).)
# ---------------------------------------------------------------------------

from asyncio import events
from dataclasses import field
import random                  
import sys                      

# ---------------------------------------------------------------------------
# DISTRIBUTIONS
# generateInterarrival() generates the interarrival times (ia) 
#   which are exponentially distributed with mean 0.5 (initialized later)
# generateService1() generates the service times for server 1 (st1)
#   which are exponentially distributed with mean 0.8
# generateService2() generates the service times for server 2 (st2)
#   which are exponentially distributed with mean 0.9
# ---------------------------------------------------------------------------

def generateInterarrival():
    """Draw the interarrival times for the customers."""
    global meanInterarrival
    ia = random.expovariate(1.0 / meanInterarrival)
    # global interarrivalList, interarrivalIndex
    # ia = interarrivalList[interarrivalIndex]
    # interarrivalIndex += 1
    return ia

def generatePickDrop():
    """Draw the pickup and dropoff locations for a customer."""
    global districts
    pickupIndex = random.randint(0, 2)
    dropoffIndex = random.randint(0, 2)
    pickup = districts[pickupIndex]
    dropoff = districts[dropoffIndex]
    # global pickdropList, pickdropIndex
    # pd = pickdropList[pickdropIndex]
    # pickdropIndex += 1
    return (pickup,dropoff)

def getTravelTime(pickup, dropoff):
    "Get travel time based off the matrix provided in HW3"
    global travelTime
    return travelTime[pickup][dropoff]

# ---------------------------------------------------------------------------
# FUTURE EVENT LIST (FEL)
# addEvent() adds an event as (eventType, eventTime, location)to FEL
#   location is only used by dropoff events.
# deleteEvent() deletes the processed event based on index
# findEarliestEvent() returns the index of the tuple in FEL with 
#   the lowest eventTime  
# ---------------------------------------------------------------------------

def addEvent(eventType, eventTime, location=None):
    global fel
    event = (eventType, eventTime, location)
    fel.append(event)

def deleteEvent(index):
    global fel
    fel.pop(index)

def findEarliestEvent():
    global fel
    earliestTime = 1e30
    earliestIndex = -1
    for i in range(len(fel)):
        event = fel[i]
        eventTime = event[1]
        if eventTime < earliestTime:
            earliestTime = eventTime
            earliestIndex = i
    return earliestIndex

# ---------------------------------------------------------------------------
# EVENT HANDLERS
# def handleArrival() 
#   [STAT] increase passengers by 1
#   [STAT] update idleTime to {idle cars * (eventTime - time)}
#   sample interarrival time, and
#   schedules a new arrival event
#   sample pickup and dropoff 
#   if there is at least one car at the pickup location, then
#       decrease the number of cars at the pickup location by 1, and 
#       schedule drop off event at the dropoff location
#   however if previous criteria not met 
#       [STAT] increase lost by 1
# def handleDropOff() 
#   [STAT] update idleTime to {idle cars * (eventTime - time)}
#   increase the number of cars at the dropoff location by 1
# def handleEnd() 
#   [STAT] update idleTime to {idle cars * (eventTime - time)}
#   adds to the statistics and stops the simuation
# ---------------------------------------------------------------------------

def handleArrival(eventTime):
    global N_DT, N_MT, N_UT, time, noArrivals, noLost, totalIdleTime
    noArrivals += 1                                                 #STATISTIC: increases number of arrivals by 1
    totalIdleTime += (N_DT + N_MT + N_UT) * (eventTime - time)      #STATISTIC: adds idle-car-minutes since last event
    ia = generateInterarrival()
    addEvent("a", eventTime + ia)
    pickup, dropoff = generatePickDrop()
    if pickup == "DT" and N_DT > 0:
        N_DT -= 1
        tt = getTravelTime(pickup, dropoff)
        addEvent("c", eventTime + tt, dropoff)
    elif pickup == "MT" and N_MT > 0:
        N_MT -= 1
        tt = getTravelTime(pickup, dropoff)
        addEvent("c", eventTime + tt, dropoff)
    elif pickup == "UT" and N_UT > 0:
        N_UT -= 1
        tt = getTravelTime(pickup, dropoff)
        addEvent("c", eventTime + tt, dropoff)
    else:
        noLost += 1                                                 #STATISTIC: increases number of lost passengers by 1
    time = eventTime

def handleDropOff(eventTime, location):
    global N_DT, N_MT, N_UT, time, totalIdleTime
    totalIdleTime += (N_DT + N_MT + N_UT) * (eventTime - time)      #STATISTIC: adds idle-car-minutes since last event
    if location == "DT":
        N_DT += 1
    elif location == "MT":
        N_MT += 1
    elif location == "UT":
        N_UT += 1
    time = eventTime

def handleEnd(eventTime):
    global time, totalIdleTime
    totalIdleTime += (N_DT + N_MT + N_UT) * (eventTime - time)      #STATISTIC: adds idle-car-minutes since last event
    time = eventTime

# ---------------------------------------------------------------------------
# INITITIALIZATION
# System starts empty at time 0 with both servers idle
# ---------------------------------------------------------------------------

fel = list()
meanInterarrival = 2

districts = ["DT", "MT", "UT"]
travelTime = {
    "DT": {"DT": 17, "MT": 10, "UT": 24},
    "MT": {"DT": 10, "MT": 12, "UT": 17},
    "UT": {"DT": 24, "MT": 17, "UT": 10}
}
interarrivalList = [1.5, 1.3, 1.5, 1.7, 1.5, 1.5, 3.0, 2.2, 3.0]
pickdropList = [("MT", "DT"), ("UT", "UT"), ("DT", "MT"), ("MT", "MT"), ("UT", "DT"), ("UT", "MT"), ("DT", "UT"), ("MT", "DT")]
interarrivalIndex = 0
pickdropIndex = 0

N_DT = 2
N_MT = 8
N_UT = 2
time = 0
noArrivals = 0
noLost = 0
totalIdleTime = 0
totalTime = 8*60            # 8 * 60 minutes in a day

ia = generateInterarrival()
addEvent("a", ia)           # first customer arrives after a random delay
addEvent("e", totalTime)    # stop collecting statistics at t = 10
eventType = ""

# ---------------------------------------------------------------------------
# MAIN LOOP
# Iterates through the future event list in order of next earliestEvent
#   until "e" is hit
# ---------------------------------------------------------------------------

while eventType != "e":
    earliestIndex = findEarliestEvent()
    earliestEvent = fel[earliestIndex]
    earliestType = earliestEvent[0]
    earliestTime = earliestEvent[1]
    earliestLocation = earliestEvent[2]
    if earliestType == "a":
        handleArrival(earliestTime)
    elif earliestType == "c":
        handleDropOff(earliestTime, earliestLocation)
    elif earliestType == "e":
        handleEnd(earliestTime)
    else:
        print("cannot identify type of the event")
        sys.exit(1)
    eventType = earliestType
    deleteEvent(earliestIndex)

# ---------------------------------------------------------------------------
# STATISTICS OF INTEREST
# 
# ---------------------------------------------------------------------------

# print("number of passengers lost to competitors " + str(noLost))
# print("number of total passengers " + str(noArrivals))
print("fraction of passengers lost to competitors " + str(noLost / noArrivals))

print("total idle time (summed over all cars) " + str(totalIdleTime))