import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import random
import math

pos = {}
all_pos = {}
robot_id = "35" 
runner_id = "2"

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
        global pos, all_pos

        data = json.loads(msg.payload.decode())
        if msg.topic.startswith("robot/"):
            robot_msg = json.loads(msg.payload.decode())
            print(f"received message: {robot_msg}")
            pipuck.set_leds_colour("magenta")
            time.sleep(0.1)
            pipuck.set_leds_colour("off")
            return
        all_pos = data
        if robot_id in data:
            pos = data[robot_id]
        print(pos)
    except json.JSONDecodeError:
        print(f'invalid json: {msg.payload}')

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(Broker, Port, 60)

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
    while True:
        if runner_id in all_pos and robot_id in all_pos:
            my_data = all_pos[robot_id]
            runner_data = all_pos[runner_id]

            x, y = my_data["position"]
            my_angle = my_data.get("angle", 0)

            runner_x, runner_y = runner_data["position"]
            dx = runner_x - x
            dy = runner_y - y

            desired_angle = math.degrees(math.atan2(dy, dx))
            angle_diff = (desired_angle - my_angle + 180) % 360 - 180

            # Rotate if misaligned
            if abs(angle_diff) > 10:
                if angle_diff > 0:
                    pipuck.epuck.set_motor_speeds(-TURN_SPEED, TURN_SPEED)
                else:
                    pipuck.epuck.set_motor_speeds(TURN_SPEED, -TURN_SPEED)
                time.sleep(abs(angle_diff) / 90.0)
                pipuck.epuck.set_motor_speeds(0, 0)

            # Avoid boundaries
            if x < 0.3 or x > 1.8 or y < 0.3 or y > 0.8:
                pipuck.epuck.set_motor_speeds(-TURN_SPEED, TURN_SPEED)
                time.sleep(0.3)
                pipuck.epuck.set_motor_speeds(Forward_SPEED, Forward_SPEED)
                time.sleep(0.8)
                continue

            # Move forward
            distance = math.sqrt(dx**2 + dy**2)
            pipuck.epuck.set_motor_speeds(Forward_SPEED, Forward_SPEED)
            time.sleep(min(distance / 0.1, 1.0))
            pipuck.epuck.set_motor_speeds(0, 0)

            # Catch logic
            if distance < 0.2:
                print(f"robot {robot_id} is 20 cm from runner {runner_id}")
                client.publish(f"robot/{robot_id}", "caught")
                pipuck.set_leds_colour("magenta")
                time.sleep(0.1)
                pipuck.set_leds_colour("off")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Interrupt detected!!")
finally:
    pipuck.epuck.set_motor_speeds(0, 0)
    client.loop_stop()



	
    
# Stop the MQTT client loop
pipuck.epuck.set_motor_speeds(0,0)
client.loop_stop()  
