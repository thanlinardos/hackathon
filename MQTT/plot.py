import pandas as pd
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

headers = ['timestamp','camera','sound','parking1','parking2']

data = pd.read_csv('C:\\Users\\thanl\\OneDrive\\Υπολογιστής\\hackathon\\MQTT\\data.csv',names=headers)

print(data.head())
start=0
stop=2000
x = data['timestamp']
y1 = data['camera']
y2 = data['sound']
y3 = data['parking1']   
y4 = data['parking2']

fig, axs = plt.subplots(2, 2)
axs[0, 0].plot(x[start:stop], y1[start:stop])
axs[0, 0].set_title('Camera')
axs[0, 1].plot(x[start:stop], y2[start:stop], 'tab:orange')
axs[0, 1].set_title('SoundDBLevel')
axs[1, 0].plot(x[start:stop], y3[start:stop], 'tab:green')
axs[1, 0].set_title('Parking 1')
axs[1, 1].plot(x[start:stop], y4[start:stop], 'tab:red')
axs[1, 1].set_title('Parking 2')

for ax in axs.flat:
    ax.set(xlabel='x-label', ylabel='y-label')

plt.show()

# identify bus stops
dy1 = np.diff(y1) / np.diff(x)
fig, ax = plt.subplots()
ax.plot(x[start:stop], dy1[start:stop])
ax.set_title('Change in people in station')
plt.show()

bus_stop_times=[]
fake_bus_stops = []
bus_noise = []
bus_1 = []
bus_2 = []
for i in range(len(dy1)):
    neighboor_p_1 = y3[i-5:i+5]
    neighboor_p_2 = y4[i-5:i+5]
    neighboor_s = y2[i-5:i+5]
    if neighboor_p_1.max()==1 and neighboor_p_2.max()==1:
        if dy1[i]>3:
            bus_stop_times.append(x[i])
            if dy1[i]>=5:
                bus_1.append(x[i])
            else:
                bus_2.append(x[i])
        elif dy1[i]==0:
            if neighboor_s.max()>29:
                fake_bus_stops.append(x[i])
        bus_noise.append(neighboor_s.max())
bus_noise_level = np.mean(bus_noise)
# 30 MINS RESULTS:
print(f"bus_stop_times:{len(bus_stop_times)}")
print(f"fake_bus_stops:{len(fake_bus_stops)}")
print(f"bus_noise_level:{bus_noise_level}")
print("ffff")