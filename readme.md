[Hackathon Iot Project Scenario](Presentation.pdf)

Reads data from sensors through a context broker using mqtt (+has ability to push through it with post requests to a mongo db ).
Then the data.scv file is used to identify events where a vehicle activates the sensors. Kmeans clustering is used to distinguish between the different bus lines that come to the given stop and drop off people. After that the period for each bus is found and we get the timetable, delays and the average noise level(again with kmeans to distinguish between buses and cars). 
Below are the initial sensors' data and the timetables for bus lines 1 and 2 respectively

![Figure_1](https://github.com/thanlinardos/hackathon/assets/58235288/5dc91560-19fe-463c-b391-d29909e818d2)

![timetable1](https://github.com/thanlinardos/hackathon/assets/58235288/d6bba3c6-57ed-475c-b0d7-856ceb6794ac)

![timetable2](https://github.com/thanlinardos/hackathon/assets/58235288/dcaa561e-bed4-415b-b1d9-2cb3d64de887)
