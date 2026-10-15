from asyncio import events
from dataclasses import field
import random                   # Need this to find the distributions
import sys                      # Need this to ???


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
    """Draw the interarrival times for the customers which are exponentially distributed."""
    global interarrivalList, interarrivalIndex
    ia = interarrivalList[interarrivalIndex]
    interarrivalIndex += 1
    return ia

def generateService1(): 
    """Draw the service times at the first server which are exponentially distributed."""
    global service1List, service1Index
    st1 = service1List[service1Index]
    service1Index += 1
    return st1

def generateService2():
    """The service times at the second server are exponentially distributed."""
    global service2List, service2Index
    st2 = service2List[service2Index]
    service2Index += 1
    return st2

# ---------------------------------------------------------------------------
# FUTURE EVENT LIST (FEL)
# addEvent() adds an event as a tuple (eventType, eventTime)to FEL
# deleteEvent() deletes the processed event based on index
# findEarliestEvent() returns the index of the tuple in FEL with 
#   the lowest eventTime  
# ---------------------------------------------------------------------------

def addEvent(eventType, eventTime):
    global fel
    event = (eventType, eventTime)
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
#   increases number of people in system by 1, and
#   schedules a new arrival event.
#   if there is one person in the system or the first server is idle, then
#       fill server 1 with the person in the queue, 
#       add a departure event from server 1, and 
#       update server 1 to busy
#   however if previous criteria not met and instead second server is idle,
#       then fill server 2 with the person in the queue, 
#       add a departure event from server 2, and 
#       update server 2 to busy
# def handleDeparture1() 
#   decreases number of people in system by 1, and
#   if there is still at least 2 people in the system, then
#       fill server 1 with the person in the queue, 
#       add a departure event from server 1, and 
#       update server 1 to busy
# def handleDeparture2()
#   decreases number of people in system by 1, and
#   if there is still at least 2 people in the system, then
#       then fill server 2 with the person in the queue, 
#       add a departure event from server 2, and 
#       update server 2 to busy
# def handleEnd() just adds to the statistics and stops the simuation
# ---------------------------------------------------------------------------

def handleArrival(eventTime):
    global inSystem, time, noArrivals, totalTimeSpent, s1Status, s2Status, totalTimeServer1Busy, totalTimeBothBusy
    noArrivals += 1                                         #STATISTIC: Increases number of arrivals by 1
    totalTimeSpent += inSystem * (eventTime - time)         #STATISTIC: Adds to totalTimeSpent by multiplying number of people in the system by time delta
    inSystem += 1                                           #STATISTIC: Increases number of people in the system by 1
    ia = generateInterarrival()
    addEvent("a", eventTime + ia)
    if s1Status == 1:
        totalTimeServer1Busy += (eventTime - time)          #STATISTIC: If just s1 busy, dds time delta to totalTimeServer1Busy
    if s1Status == 1 and s2Status == 1:
        totalTimeBothBusy += (eventTime - time)             #STATISTIC: If both busy, adds time delta to totalTimeBothBusy
    if inSystem == 1 or s1Status == 0: 
        st1 = generateService1()
        addEvent("d1", eventTime + st1)
        s1Status = 1
    elif s2Status == 0:
        st2 = generateService2()
        addEvent("d2", eventTime + st2)
        s2Status = 1
    time = eventTime 

def handleDeparture1(eventTime):
    global inSystem, time, totalTimeSpent, totalTimeBothBusy, totalTimeServer1Busy, s1Status, s2Status
    totalTimeSpent += inSystem * (eventTime - time)         #STATISTIC: Adds to totalTimeSpent by multiplying number of people in the system by time delta
    inSystem -= 1                                           #STATISTIC: Reduces number of people in the system by 1
    if s1Status == 1:
        totalTimeServer1Busy += (eventTime - time)          #STATISTIC: If just s1 busy, dds time delta to totalTimeServer1Busy
    if s1Status == 1 and s2Status == 1:
        totalTimeBothBusy += (eventTime - time)             #STATISTIC: If both busy, adds time delta to totalTimeBothBusy
    s1Status = 0                                            
    if inSystem > 1:
        st1 = generateService1()
        addEvent("d1", eventTime + st1)
        s1Status = 1
    time = eventTime

def handleDeparture2(eventTime):
    global inSystem, time, totalTimeSpent, totalTimeBothBusy, totalTimeServer1Busy, s1Status, s2Status
    totalTimeSpent += inSystem * (eventTime - time)
    inSystem -= 1
    if s1Status == 1:
        totalTimeServer1Busy += (eventTime - time)          #STATISTIC: If just s1 busy, dds time delta to totalTimeServer1Busy
    if s1Status == 1 and s2Status == 1:
        totalTimeBothBusy += (eventTime - time)             #STATISTIC: If both busy, adds time delta to totalTimeBothBusy
    s2Status = 0
    if inSystem > 1:
        st2 = generateService2()
        addEvent("d2", eventTime + st2)
        s2Status = 1
    time = eventTime

def handleEnd(eventTime):
    global time, totalTimeSpent, totalTimeBothBusy, totalTimeServer1Busy
    totalTimeSpent += inSystem * (eventTime - time)
    if s1Status == 1:
        totalTimeServer1Busy += (eventTime - time)          #STATISTIC: If just s1 busy, dds time delta to totalTimeServer1Busy
    if s1Status == 1 and s2Status == 1:
        totalTimeBothBusy += (eventTime - time)             #STATISTIC: If both busy, adds time delta to totalTimeBothBusy
    time = eventTime

# ---------------------------------------------------------------------------
# INITITIALIZATION
# System starts empty at time 0
# ---------------------------------------------------------------------------

fel = list()
# can use random.seed() to fix the set of random numbers used in calculations.
# interarrivalList = 0.5     
# meanService1 = 0.8         
# meanService2 = 0.9  
interarrivalList = [1.3, 1.1, 0.6, 1.5, 2.2, 1.1, 0.5, 0.7, 0.1, 1.4, 1.2, 1.4, 1.4, 1.2, 2.1]
service1List = [2.1, 1.3, 0.9, 1.4, 1.2, 2.1, 2.2]         
service2List = [2.2, 1.6, 1.1, 1.7, 2.1, 1.3, 0.9]    
interarrivalIndex = 0
service1Index = 0   
service2Index = 0 
time = 0 
inSystem = 0
s1Status = 0
s2Status = 0
noArrivals = 0
totalTimeSpent = 0
totalTimeServer1Busy = 0
totalTimeBothBusy = 0 
totalTime = 10

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
    if earliestType == "a":
        handleArrival(earliestTime)
    elif earliestType == "d1":
        handleDeparture1(earliestTime)
    elif earliestType == "d2":
        handleDeparture2(earliestTime)
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

print("total time first server is busy " + str(totalTimeServer1Busy))
print("proportion of time that the first server is busy " + str(totalTimeServer1Busy / totalTime))

print("total time both servers are busy " + str(totalTimeBothBusy))
print("proportion of time that the both servers are busy " + str(totalTimeBothBusy / totalTime))

print("total time by arrivals " + str(totalTimeSpent))
print("no arrivals " + str(noArrivals))
print("avg time arriving customer spends in system " + str(totalTimeSpent / noArrivals))