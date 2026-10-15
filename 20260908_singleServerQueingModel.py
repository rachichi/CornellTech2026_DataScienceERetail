
"""
Single-server queueing simulation (M/M/1 style).

Customers arrive one at a time, wait in a single queue if the server is busy,
get served, then leave. Interarrival and service times are exponential.

This is a discrete-event simulation: instead of ticking the clock in small
steps, we jump from event to event (arrival, departure, or end of run).
The future event list (fel) stores those upcoming events.

We estimate average time a customer spends in the system using the area
under the occupancy curve: integral of N(t) dt / number of arrivals,
where N(t) is how many people are in the system at time t.
"""

import random
import sys


# ---------------------------------------------------------------------------
# Random times
# random.expovariate(lambda) draws Exponential(rate = lambda).
# Mean of Exponential(rate) is 1/rate, so we pass 1/mean as the rate.
# ---------------------------------------------------------------------------

def generateInterarrival():
    """Draw the time until the next arrival."""
    global meanInterarrival
    ia = random.expovariate(1.0 / meanInterarrival)
    return ia


def generateService():
    """Draw how long the current customer will occupy the server."""
    global meanService
    st = random.expovariate(1.0 / meanService)
    return st


# ---------------------------------------------------------------------------
# Future event list (FEL)
# Each event is a tuple: (eventType, eventTime)
#   "a" = arrival, "d" = departure, "e" = end of simulation
# Events are NOT kept sorted; we scan the list to find the next one.
# ---------------------------------------------------------------------------

def addEvent(eventType, eventTime):
    """Schedule a future event by appending it to the FEL."""
    global fel
    event = (eventType, eventTime)
    fel.append(event)


def deleteEvent(index):
    """Remove the event we just processed so it is not handled twice."""
    global fel
    fel.pop(index)


def findEarliestEvent():
    """Return the index of the event with the smallest clock time."""
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
# Event handlers
#
# Before changing the state, we add
#     inSystem * (eventTime - time)
# to totalTimeSpent. That is a rectangle: occupancy times elapsed time,
# i.e. one piece of the integral of N(t). Then we update N and the clock.
# ---------------------------------------------------------------------------

def handleArrival(eventTime):
    """A customer arrives. Always schedule the next arrival.
    If the system was empty, this customer starts service immediately,
    so we also schedule their departure."""
    global inSystem, time, noArrivals, totalTimeSpent
    noArrivals += 1
    # Accumulate area under N(t) from last event until this arrival
    totalTimeSpent += inSystem * (eventTime - time)
    inSystem += 1  # one more person in the system
    ia = generateInterarrival()
    addEvent("a", eventTime + ia)  # next arrival is independent of this one
    if inSystem == 1:
        # Server was idle; this arrival begins service now
        st = generateService()
        addEvent("d", eventTime + st)
    time = eventTime # time is updated to the eventTime 


def handleDeparture(eventTime):
    """A customer finishes service and leaves.
    If anyone is still waiting, start the next service and schedule
    that person's departure."""
    global inSystem, time, totalTimeSpent
    totalTimeSpent += inSystem * (eventTime - time)
    inSystem -= 1  # one person leaves
    if inSystem > 0:
        # Queue was not empty; server takes the next customer immediately
        st = generateService()
        addEvent("d", eventTime + st)
    time = eventTime  # time is updated to the eventTime


def handleEnd(eventTime):
    """Simulation horizon is reached. Close out the last rectangle of N(t)."""
    global time, totalTimeSpent
    totalTimeSpent += inSystem * (eventTime - time)
    time = eventTime


# ---------------------------------------------------------------------------
# Initialization
# System starts empty at time 0. First arrival is scheduled, plus a
# terminal "end" event at time 480 (e.g. an 8-hour day in minutes).
# ---------------------------------------------------------------------------

fel = list()
meanInterarrival = 5  # E[interarrival] = 5 => arrival rate λ = 1/5
meanService = 1       # E[service] = 4 => service rate μ = 1/4 (traffic intensity ρ = 0.8). Closer these are is the longer each person would be in the system. 
time = 0              # simulation clock (last event time used for the integral)
inSystem = 0          # N(t): number of customers in queue + in service
noArrivals = 0        # count of arrival events processed
totalTimeSpent = 0    # running integral of N(t)

ia = generateInterarrival()
addEvent("a", ia)     # first customer arrives after a random delay
addEvent("e", 480)    # stop collecting statistics at t = 480
eventType = ""

# ---------------------------------------------------------------------------
# Main loop: always process the chronologically next event until "e"
# ---------------------------------------------------------------------------

while eventType != "e":
    earliestIndex = findEarliestEvent()
    earliestEvent = fel[earliestIndex]
    earliestType = earliestEvent[0]
    earliestTime = earliestEvent[1]
    if earliestType == "a":
        handleArrival(earliestTime)
    elif earliestType == "d":
        handleDeparture(earliestTime)
    elif earliestType == "e":
        handleEnd(earliestTime)
    else:
        print("cannot identify type of the event")
        sys.exit(1)
    eventType = earliestType
    deleteEvent(earliestIndex)

# totalTimeSpent / noArrivals ≈ average time a customer spends in the system
print("no arrivals " + str(noArrivals))
print("avg time in system " + str(totalTimeSpent / noArrivals))
