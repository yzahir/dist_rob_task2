import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import math

# Setup
pi_puck_id = "16"
runner_id = "2"
Broker = "192.168.178.56"
Port = 1883

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

    except json.JSONDecodeError:
        print(f"Invalid JSON: {msg.payload}")

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

        x, y, angle = get_position()
        if x is not None:
            print(f"[{pi_puck_id}] Position: ({x:.2f}, {y:.2f}), Angle: {angle:.2f}")
        
        if time.time() - last_pub_time > publish_interval:
            last_pub_time = time.time()
            # Example behavior: Blink LED to show activity
            pipuck.set_led_rgb(0, 1, 0, 0)  # red
            time.sleep(0.1)
            pipuck.set_led_rgb(0, 0, 0, 0)  # off

except KeyboardInterrupt:
    print("Interrupt detected. Stopping robot.")
finally:
    pipuck.epuck.set_motor_speeds(0, 0)
    client.loop_stop()
