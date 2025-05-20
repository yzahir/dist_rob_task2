import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import random
import math

pos = {}
all_pos = {}
robot_id = "40" 
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
    last_pub_time = time.time()
    publish_interval = 3 # 3 seconds
    for _ in range(1000):
        for rbt_id, robot_data in all_pos.items():
            robot_angle = robot_data.get("angle", 0)
            if rbt_id == runner_id:
                x, y = pos["position"]
                runner_x, runner_y = robot_data["position"]
                my_angle = pos["angle"]
                dx = runner_x-x
                dy = runner_y-y
                d_angle = math.degrees(math.atan2(dy, dx))
                angle_diff = (d_angle - my_angle + 180) % 360 - 180
                if angle_diff < 5:
                    if angle_diff > 0:
                        pipuck.epuck.set_motor_speeds(-TURN_SPEED, TURN_SPEED)
                    else:
                        pipuck.epuck.set_motor_speeds(TURN_SPEED, -TURN_SPEED)
                    time.sleep(TURN_SPEED/angle_diff)
                    pipuck.epuck.set_motor_speeds(0, 0)

                else:
                    if "position" in pos:
                        current_pos = pos["position"]
                        if(current_pos[0]<0.3 or  current_pos[0]>1.8 or current_pos[1]>0.8 or current_pos[1]<0.3):
                            pipuck.epuck.set_motor_speeds(-TURN_SPEED, TURN_SPEED)
                            time.sleep(0.3)
                            pipuck.epuck.set_motor_speeds(Forward_SPEED,Forward_SPEED)
                            time.sleep(0.8)
                            continue
                    pipuck.epuck.set_motor_speeds(Forward_SPEED,Forward_SPEED)
                    time.sleep(math.sqrt(dx**2 + dy**2)/Forward_SPEED)

                    if (runner_x-x)**2 + (runner_y-y)**2 < 0.2:
                        print(f"robot {rbt_id} is 20 cm away")
                        str = f"robot_pos/{rbt_id}"
                        client.publish(str, "caught")
                        pipuck.set_leds_colour("magenta")
                        time.sleep(0.1)
                        pipuck.set_leds_colour("off")

                        #continue
                                    
except KeyboardInterrupt:
    print("Interrupt detected!!")
finally:
    pipuck.epuck.set_motor_speeds(0,0)


	
    
# Stop the MQTT client loop
pipuck.epuck.set_motor_speeds(0,0)
client.loop_stop()  
