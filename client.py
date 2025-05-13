import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import random

pos = {}

# Define variables and callbacks
Broker = "192.168.178.56"  # Replace with your broker address
Port = 1883 # standard MQTT port
# function to handle connection
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("robot_pos/all")

# function to handle incoming messages
def on_message(client, userdata, msg):
    try:
        global pos
        data = json.loads(msg.payload.decode())
        if "35" in data:
            pos = data["35"]
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
    for _ in range(1000):
        # TODO: Do your stuff here
        speed = random.randint(300,1000)
        turn_speed = random.randint(100, 300)
        duration = random.randint(1,10)
        direction = random.choice(["left", "right"])
        start_time = time.time()
        
        pipuck.epuck.set_motor_speeds(speed,speed)
        if "position" in pos:
            current_pos = pos["position"]
            avoid_turn = 500
            if(current_pos[0]<0.2 or  current_pos[0]>1.9 or current_pos[1]>0.9 or current_pos[1]<0.2):
                pipuck.epuck.set_motor_speeds(-avoid_turn, avoid_turn)
                time.sleep(0.2)
        time.sleep(duration)
        if direction == "left":
            pipuck.epuck.set_motor_speeds(-turn_speed, turn_speed)
        else:
            pipuck.epuck.set_motor_speeds(turn_speed, -turn_speed)
        time.sleep(duration/10.0)

except KeyboardInterrupt:
    print("Interrupt detected!!")
finally:
    pipuck.epuck.set_motor_speeds(0,0)


	
    
# Stop the MQTT client loop
pipuck.epuck.set_motor_speeds(0,0)
client.loop_stop()  
