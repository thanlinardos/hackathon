[Hackathon Iot Project Scenario](Presentation.pdf)
Reads data from sensors through a context broker using mqtt (+has ability to push through it with post requests to a mongo db ). Then the data.scv file is used to identify events where a vehicle activates the sensors. Kmeans clustering is used to distinguish between the different bus lines that come to the given stop and drop off people. After that the period for each bus is found and we get the timetable, delays and the average noise level(again with kmeans to distinguish between buses and cars).

