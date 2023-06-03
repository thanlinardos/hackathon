import pandas as pd
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
from paths import *  # <-- comment this line
from clustering_utils import *
headers = ['timestamp','camera','sound','parking1','parking2']
# project_root = 'path//to//project//' # <-- uncomment this line with path to project folder
data = pd.read_csv(f'{project_root}MQTT\\data.csv',names=headers)

print(data.head())
start=0
stop=-1
x = data['timestamp']
no_people = data['camera']
dblevel = data['sound']
parking1 = data['parking1']   
parking2 = data['parking2']


def plot_initial():
    fig, axs = plt.subplots()
    axs.plot(x[start:stop], no_people[start:stop])
    axs.set_title('Camera')
    axs.set(xlabel='timestamp', ylabel='no_people')

    fig, axs = plt.subplots()
    axs.plot(x[start:stop], dblevel[start:stop], 'tab:orange')
    axs.set_title('SoundDBLevel')
    axs.set(xlabel='timestamp', ylabel='DB')

    fig, axs = plt.subplots()
    axs.plot(x[start:stop], parking1[start:stop], 'tab:green')
    axs.set_title('Parking 1')
    axs.set(xlabel='timestamp', ylabel='Active')

    fig, axs = plt.subplots()
    axs.plot(x[start:stop], parking2[start:stop], 'tab:red')
    axs.set_title('Parking 2')
    axs.set(xlabel='timestamp', ylabel='Active')
    plt.show()

def id_events(event_table, e_start, e_end, no_events,max_time_per_event):
    i=0
    while i<x.size:
        if(parking1[i]==1 or parking2[i]==1):
            e_start=i
            found = False
            for j in range(e_start,e_start+max_time_per_event):
                if(parking1[j]==0 and parking2[j]==0 and parking1[j-1]==0 and parking2[j-1]==0):
                    e_end = j
                    found = True
                    break
            if not found:
                print("warning: increase max_time_per_event")
                e_end = j
            event_table[no_events] = [e_start,e_end]
            no_events+=1
            i=j
        else:
            i+=1
    event_table = event_table[:no_events]
    return [event_table,no_events]
    

# Plot the initial data from the sensors:
# plot_initial()

# identify events:
# parameters
max_time_per_event = 60
min_time_between_events = 30

[event_table,no_events] = id_events(np.zeros(((int) (x.size / 2),2),dtype=np.uint32),0,0,0,max_time_per_event)
print(f"Number of events = {no_events}")

# Find all bus stops
drop_of_people_per_event = np.zeros(no_events,dtype=np.uint8)
bus_stop_data = np.zeros(no_events,dtype=[('event_id',np.uint32),('people_drop',np.uint8),('max_noise',np.float32),('event_starts',np.uint32)])
all_bus_count = 0
for i in range(no_events):
    drop_of_people_per_event[i] = no_people[event_table[i][0]-1] - no_people[event_table[i][1]-1]
    if drop_of_people_per_event[i]>7:
        bus_stop_data[all_bus_count] = (i,drop_of_people_per_event[i],dblevel[event_table[i][0]-1:event_table[i][1]].max(),event_table[i][0])
        all_bus_count+=1

bus_stop_data = bus_stop_data[:all_bus_count]

print(f'All bus stops: {all_bus_count}')
print(f'Mean drop of people: {np.mean(bus_stop_data["people_drop"])}')
fig, axs = plt.subplots()
axs.plot(bus_stop_data["event_starts"], bus_stop_data["people_drop"], 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('Drop of people per bus_stop start time')
axs.set(xlabel='event_time_start', ylabel='Drop of people')

# use kmeans clustering to find number of bus lines:
possible_no_lines = np.arange(1,9)
people_drop_time_start_pair = np.zeros((all_bus_count,2),dtype=np.uint32)
people_drop_time_start_pair[:,0] = bus_stop_data['people_drop']
people_drop_time_start_pair[:,1] = bus_stop_data['event_starts']
wcss = check_cluster_multitudes(possible_no_lines,people_drop_time_start_pair)
no_bus_lines = find_elbow(wcss,possible_no_lines)
# Distinguish between the 2 bus lines (using mean drop of people)
# first dimension is each bus line, second is each stop of that line and 3rd are the columns: event_index,drop_of_people,max_noise,event_starts
bus_line_data = np.zeros((no_bus_lines,all_bus_count),dtype=[('event_id',np.uint32),('people_drop',np.uint8),('max_noise',np.float32),('event_starts',np.uint32)])

bus_1_count = 0
bus_2_count = 0

# for i in range(all_bus_count):
#     if(bus_stop_data["people_drop"][i]>np.mean(bus_stop_data["people_drop"])):
#         bus_line_data[0][bus_1_count] = bus_stop_data[i]
#         bus_1_count+=1
#     else:
#         bus_line_data[1][bus_2_count] = bus_stop_data[i]
#         bus_2_count+=1

# same using clustering again:
cntr,labels=find_centers(bus_stop_data['people_drop'].reshape(-1, 1),no_bus_lines)
print(f"cluster center for line 1: {cntr[0]} (people_drop)")
print(f"cluster center for line 2: {cntr[1]} (people_drop)")
for i in range(all_bus_count):
    if labels[i]==0:
        bus_line_data[0][bus_1_count] = bus_stop_data[i]
        bus_1_count+=1
    else:
        bus_line_data[1][bus_2_count] = bus_stop_data[i]
        bus_2_count+=1

print(f'Bus line 1 stops: {bus_1_count}')
time_between_bus_1_stops = np.diff(bus_line_data[0]["event_starts"][:bus_1_count-1])
period_1 = np.argmax(np.bincount(time_between_bus_1_stops))
print(f'Bus line 1 period: {period_1} ({period_1/60} mins)')
print(f'Bus line 2 stops: {bus_2_count}')
time_between_bus_2_stops = np.diff(bus_line_data[1]["event_starts"][:bus_2_count-1])
period_2 = np.argmax(np.bincount(time_between_bus_2_stops))
print(f'Bus line 2 period: {period_2} ({period_2/60} mins)')

# Correct 2 bus lines by using the periods we found:
bus_line_data = np.zeros((no_bus_lines,all_bus_count),dtype=[('event_id',np.uint32),('people_drop',np.uint8),('max_noise',np.float32),('event_starts',np.uint32)])

bus_1_count = 0
bus_2_count = 0
# initial times found from data:
t10 = 963
t20 = 3
t1 = t10
t2 = t20
prev_pass = -1
i=0
while(i<all_bus_count):
    pass_1 = bus_stop_data["event_starts"][i]%period_1<30
    pass_2 = bus_stop_data["event_starts"][i]%period_2<30
    if pass_1 and pass_2 and prev_pass<0:
        if bus_stop_data["people_drop"][i]<np.mean(bus_stop_data["people_drop"][i]):
            pass_1 = False
            prev_pass = 2
        else:
            pass_2 = False
            prev_pass = 1
    else:
        if prev_pass==1:
            pass_1 = False
            pass_2 = True
            prev_pass=-1
        if prev_pass==2:
            pass_2 = False
            pass_1 = True
            prev_pass = -1

    if pass_1:
        bus_line_data[0][bus_1_count] = bus_stop_data[i]
        bus_1_count+=1
    elif pass_2:
        bus_line_data[1][bus_2_count] = bus_stop_data[i]
        bus_2_count+=1
    i+=1
print('Corrected bus lines:')
print(f'Bus line 1 stops: {bus_1_count}')
time_between_bus_1_stops = np.diff(bus_line_data[0]["event_starts"][:bus_1_count-1])
period_1 = np.argmax(np.bincount(time_between_bus_1_stops))
print(f'Bus line 1 period: {period_1} ({period_1/60} mins)')
print(f'Mean bus line 1 people drop: {np.mean(bus_line_data[0]["people_drop"][:bus_1_count])}')

print(f'Bus line 2 stops: {bus_2_count}')
time_between_bus_2_stops = np.diff(bus_line_data[1]["event_starts"][:bus_2_count-1])
period_2 = np.argmax(np.bincount(time_between_bus_2_stops))
print(f'Bus line 2 period: {period_2} ({period_2/60} mins)')
print(f'Mean bus line 2 people drop: {np.mean(bus_line_data[1]["people_drop"][:bus_2_count])}')

fig, axs = plt.subplots()
axs.plot(bus_line_data[0]["event_starts"][:bus_1_count], bus_line_data[0]["people_drop"][:bus_1_count], 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('Bus Line 1')
axs.set(xlabel='event_time_start', ylabel='Drop of people')

fig, axs = plt.subplots()
axs.plot(bus_line_data[1]["event_starts"][:bus_2_count], bus_line_data[1]["people_drop"][:bus_2_count], 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('Bus Line 2')
axs.set(xlabel='event_time_start', ylabel='Drop of people')

event_no_1 = np.arange(1,bus_1_count-1)
event_no_2 = np.arange(1,bus_2_count-1)

fig, axs = plt.subplots()
axs.plot(event_no_1, time_between_bus_1_stops, 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('Time diff between bus_1 stops')
axs.set(xlabel='event_no', ylabel='Time diff from prev event')

fig, axs = plt.subplots()
axs.plot(event_no_2, time_between_bus_2_stops, 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('Time diff between bus_2 stops')
axs.set(xlabel='event_no', ylabel='Time diff from prev event')
# Timetable & delays:
timetable_1 = np.arange(t10,period_1*bus_1_count,period_1)
ty_1 = np.ones(timetable_1.size)
timetable_2 = np.arange(t20,period_2*bus_2_count,period_2)
ty_2 = np.ones(timetable_2.size)

# delays as fractions of the period
delays_1 = np.ones(bus_1_count-2,dtype=np.float32)
d_1_c=0
d_2_c=0
delays_2 = np.ones(bus_2_count-2,dtype=np.float32)
for i in range(bus_1_count-2):
    if time_between_bus_1_stops[i]>period_1+30:
        delays_1[i]=float(time_between_bus_1_stops[i])/float(period_1)
        d_1_c+=1
for i in range(bus_2_count-2):
    if time_between_bus_2_stops[i]>period_2+30:
        delays_2[i]=float(time_between_bus_2_stops[i])/float(period_2)
        d_2_c+=1
print(f'Delays for bus line 1: {d_1_c}')
print(f'Delays for bus line 2: {d_2_c}')
fig, axs = plt.subplots()
axs.plot(event_no_1, delays_1, 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('Timetable 1')
axs.set(xlabel='event_no', ylabel='Delay/period')
fig, axs = plt.subplots()
axs.plot(event_no_2, delays_2, 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('Timetable 2')
axs.set(xlabel='event_no', ylabel='Delay/period')

# fig, axs = plt.subplots()
# axs.plot(timetable_1, ty_1, 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
# axs.set_title('Ideal Timetable 1')
# axs.set(xlabel='arrival time for line 1', ylabel='Delay/period')
# fig, axs = plt.subplots()
# axs.plot(timetable_2, ty_2, 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
# axs.set_title('Ideal Timetable 2')
# axs.set(xlabel='arrival time for line 2', ylabel='Delay/period')

# Noise at bus stops -> noise for each bus -> find bus that doesnt stop
possible_no_noise_levels = np.arange(1,9)
noiselvl_time_start_pair = np.zeros((no_events,2),dtype=np.float32)
for i in range(no_events):
    noiselvl_time_start_pair[i][0] = dblevel[event_table[i][0]-1:event_table[i][1]].max()
    noiselvl_time_start_pair[i][1] = event_table[i][0]
wcss = check_cluster_multitudes(possible_no_noise_levels,noiselvl_time_start_pair)
no_noise_levels = find_elbow(wcss,possible_no_noise_levels)
print(f"noise_levels: {no_noise_levels}") # one noise level for cars and one for buses
cntr,labels=find_centers(noiselvl_time_start_pair[:,0].reshape(-1, 1),no_noise_levels)
print(f"cluster center for cars: {cntr[0]} [dB]")
print(f"cluster center for buses: {cntr[1]} [dB]")
bus_3_ind = np.zeros(no_events,dtype=np.uint32)
no_bus_3_passes=0
for i in range(no_events):
    if labels[i] == 1:
        if drop_of_people_per_event[i]<=2:
            bus_3_ind[no_bus_3_passes]=i
            no_bus_3_passes+=1
bus_3_pass = np.zeros((no_bus_3_passes,2),dtype=np.uint32)
for i in range(no_bus_3_passes):
    bus_3_pass[i][0]=bus_3_ind[i]
    bus_3_pass[i][1]=event_table[i][0]
print(f"No of bus 3 passes: {no_bus_3_passes}")
ones = np.ones(no_bus_3_passes,dtype=np.uint32)
time_between_bus_3_stops = np.diff(bus_3_pass[:,1][:no_bus_3_passes-1])
period_3 = np.argmax(np.bincount(time_between_bus_3_stops))
print(f'Bus line 3 period: {period_3} ({period_3/60} mins)')

fig, axs = plt.subplots()
axs.plot(bus_3_pass[:,1], ones, 'tab:red', linestyle='None',marker = ".", markersize = 5.0)
axs.set_title('3rd Bus passes')
axs.set(xlabel='event_time_start', ylabel='')

plt.show()
