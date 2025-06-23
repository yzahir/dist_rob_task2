import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import math
import random

# Setup
pi_puck_id = "16"
runner_id = "2"
Broker = "192.168.178.56"
Port = 1883

max_range = 0.5  # Maximum range to consider other robots

# Global storage
puck_pos_dict = {}
puck_dict = {}

# Init PiPuck
pipuck = PiPuck(epuck_version=2)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("robot_pos/all")

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

                dist = distance(x_self, y_self, msg_x, msg_y)
                if dist <= max_range:
                    puck_dict[robot_id] = robot_data

    except json.JSONDecodeError:
        print(f'invalid json: {msg.payload}')


        print(f'invalid json: {msg.payload}')

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def publish_data(packet):
    client.publish("robots/all", json.dumps(packet))
    
# Position getter
def get_position(id=pi_puck_id):
    data = puck_pos_dict.get(id)
    if data:
        pos = data.get('position')
        if pos:
            x, y = pos[0], pos[1]
            angle = data.get('angle')
            return x, y, angle
    print(f"No data for PiPuck ID: {id}")
    return None, None, None

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(Broker, Port, 60)
client.loop_start()

# Constants
workspace_LBorder = 50
workspace_RBorder = 60
TURN_SPEED = 200
FORWARD_SPEED = 500

# Main loop
try:
    publish_interval = 3
    last_pub_time = time.time()

    for _ in range(1000):
        time.sleep(0.1)  # reduce CPU load
        print(f'puck_dict: {puck_dict}')
        x, y, angle = get_position()
        if x is not None and y is not None:
            publish_data({
                pi_puck_id: {
                    "x": x,
                    "y": y,
                    "angle": angle,
                    "sensors": {
                        "temperature": random.randint(0,50),
                        "humidity": random.randint(0,100),
                        "light": random.randint(0,100)
                    },
                    "target_found": False
                }
            })
        else:
            print("Position data not available.")

except KeyboardInterrupt:
    print("Interrupt detected. Stopping robot.")
finally:
    pipuck.epuck.set_motor_speeds(0, 0)
    client.loop_stop()
