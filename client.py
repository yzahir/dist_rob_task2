import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import random
import math

pos = {}
all_pos = {}
pi_puck_id = "16" 
runner_id = "2"
puck_pos_dict = {}
puck_dict = {}

# Define variables and callbacks
Broker = "192.168.178.56"  # Replace with your broker address
Port = 1883 # standard MQTT port

# Initialize the PiPuck
pipuck = PiPuck(epuck_version=2)

# function to handle connection
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("robot_pos/all")
    client.subscribe("robot/+")

# function to handle incoming messages
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        if msg.topic == "robot_pos/all":
            puck_pos_dict.update(data)

        if msg.topic == "robots/all":
            x_self, y_self, _ = get_position()
            for robot_id, robot_data in data.items():
                # if robot_id == pi_puck_id:
                #     continue  
                msg_x = robot_data.get("x")
                msg_y = robot_data.get("y")

                #dist = distance(x_self, y_self, msg_x, msg_y)
                #☻if dist <= max_range:
                puck_dict[robot_id] = robot_data

    except json.JSONDecodeError:
        print(f'invalid json: {msg.payload}')


        print(f'invalid json: {msg.payload}')


def get_position(id=pi_puck_id):
    global x, y

    data = puck_pos_dict.get(id)
    if data:
        pos = data.get('position')
        if pos:
            x = pos[0]
            y = pos[1]
            angle = data.get('angle')
            return x, y, angle
    else:
        print(f"No data for PiPuck ID: {id}")
    return None, None, None
# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(Broker, Port, 240)

client.loop_start() # Start listening loop in separate thread

# Initialize the PiPuck
#pipuck = PiPuck(epuck_version=2)

# Set the robot's speed, e.g. with
#pipuck.epuck.set_motor_speeds(1000,-1000)
#pipuck.set_led_colour(1, "magenta")
#pipuck.set_led_rgb(0, 1, 0, 0)
workspace_Lboarder = 50
workspace_RBoarder = 60
TURN_SPEED = 200
Forward_SPEED = 500
try:
    last_pub_time = time.time()
    publish_interval = 3 # 3 seconds
    for _ in range(1000):
        print(puck_pos_dict)

                        #continue
                                    
except KeyboardInterrupt:
    print("Interrupt detected!!")
finally:
    pipuck.epuck.set_motor_speeds(0,0)


	
    
# Stop the MQTT client loop
pipuck.epuck.set_motor_speeds(0,0)
client.loop_stop()  
