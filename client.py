import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import random

pos = {}
all_pos = {}
robot_id = "40" 

# Define variables and callbacks
Broker = "192.168.178.56"  # Replace with your broker address
Port = 1883 # standard MQTT port
# function to handle connection
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("robot_pos/all")
    client.subscribe(f"robot/{robot_id}")

# function to handle incoming messages
def on_message(client, userdata, msg):
    try:
        global pos, all_pos

        data = json.loads(msg.payload.decode())
        if msg.topic == "robot/+":
            robot_msg = json.loads(msg.payload.decode())
            pipuck.set_leds_colour("magenta")
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
pipuck = PiPuck(epuck_version=2)

# Set the robot's speed, e.g. with
#pipuck.epuck.set_motor_speeds(1000,-1000)
pipuck.set_led_colour(1, "magenta")
#pipuck.set_led_rgb(0, 1, 0, 0)
workspace_Lboarder = 50
workspace_RBoarder = 60
try:
    last_pub_time = time.time()
    publish_interval = 3 # 3 seconds
    for _ in range(1000):
        
        speed = random.randint(300,1000)
        turn_speed = random.randint(100, 300)
        duration = random.randint(1,10)
        direction = random.choice(["left", "right"])
        start_time = time.time()
        #pipuck.epuck.set_motor_speeds(speed,speed)
        if "position" in pos:
            current_pos = pos["position"]
            avoid_turn = 500
            if(current_pos[0]<0.3 or  current_pos[0]>1.8 or current_pos[1]>0.8 or current_pos[1]<0.3):
                pipuck.epuck.set_motor_speeds(-avoid_turn, avoid_turn)
                time.sleep(0.3)
                pipuck.epuck.set_motor_speeds(speed,speed)
                time.sleep(0.8)
                continue
        pipuck.epuck.set_motor_speeds(speed,speed)
        time.sleep(duration/10.0)
        if direction == "left":
            pipuck.epuck.set_motor_speeds(-turn_speed, turn_speed)
        else:
            pipuck.epuck.set_motor_speeds(turn_speed, -turn_speed)
        time.sleep(duration/10.0)

        if time.time() - last_pub_time> publish_interval:
            # read the position of all  robots, check if the robot in 50 cm radius and send a message to the one in the inerval
            #x = pos[0]
            #y = pos[1]
            for rbt_id, robot_pos in all_pos.items():
                if rbt_id == robot_id:
                    x = robot_pos["position"][0]
                    y = robot_pos["position"][1]
                if (robot_pos["position"][0]-current_pos[0])**2 + (robot_pos["position"][1]-current_pos[1])**2 < 0.5:
                    print(f"robot {rbt_id} is 50 cm away")
                    str = f"robot_pos/{rbt_id}"
                    client.publish(str, "Hello")
                    last_pub_time = time.time()
                    continue
                                    

except KeyboardInterrupt:
    print("Interrupt detected!!")
finally:
    pipuck.epuck.set_motor_speeds(0,0)


	
    
# Stop the MQTT client loop
pipuck.epuck.set_motor_speeds(0,0)
client.loop_stop()  
