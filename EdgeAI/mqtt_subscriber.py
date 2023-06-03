# python3.6
import requests
import csv

from paho.mqtt import client as mqtt_client
from pymongo import MongoClient


context_port = 1034
broker = 'localhost'
port = 1883
topic = "data"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-team33333300001010101'
# url root for context broker:
url_root=f"http://{broker}:{context_port}"
data = []
device_ids = ["0","urn:ngsi-ld:Device:camera-483942:TEAM3","urn:ngsi-ld:SoundPressureLevel:id:NLPM:36024607:TEAM3","urn:ngsi-ld:ParkingSpot:than:linardos:0:TEAM3","urn:ngsi-ld:ParkingSpot:than:linardos:1:TEAM3"]
types = ["timestamp","Device","SoundPressureLevel","ParkingSpot","ParkingSpot"]
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client):
    def on_message(client, userdata, msg):
        data.append(msg.payload.decode().split(','))
        # print(f"len={len(data)}\n")
        print(f"Received `{data[-1]}` from `{msg.topic}` topic")
        if(len(data)>6000):
            client.disconnect()
    print(f"Subscribed to topic: {topic}")
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()
    

def update(i,value):
    type = types[i]
    id = device_ids[i]
    if type=="Device":
        url = f"{url_root}/ngsi-ld/v1/entities/{id}/attrs"
        obj = {"value": f"{value}"}
    elif type=="ParkingSpot":
        url = f"{url_root}/ngsi-ld/v1/entities/{id}/attrs"
        obj = {"status": f"{value}"}
    elif type=="SoundPressureLevel":
        url = f"{url_root}/ngsi-ld/v1/entities/{id}/attrs"
        obj = {"sounddB": f"{value}"}
    else:
        print("Invalid device type...")
        return
    x = requests.post(url, json = obj)
    resp = requests.get(f"{url_root}/ngsi-ld/v1/entities?id={id}&options=keyValues")
    print(resp)

def write_to_csv():
    f = open('C:\\Users\\thanl\\OneDrive\\Υπολογιστής\\hackathon\\MQTT\\data.csv', 'a', newline='')
    writer = csv.writer(f)
    for i in data:
        writer.writerow(i)
    f.close()

if __name__ == '__main__':
    print("Program start...")
    run()
    #update camera ->20
    update(1,24)
    # parking spot 0 -> 1 (occupied)
    update(3,1)

    write_to_csv()

    
