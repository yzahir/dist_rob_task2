import paho.mqtt.client as mqtt
import json
import time
from pipuck.pipuck import PiPuck
import math

pos = {}
all_pos = {}
robot_id = "7"  # This robot is the chaser
runner_id = "2"  # Target robot to chase

Broker = "192.168.178.56"  # Replace with your MQTT broker address
Port = 1883

pipuck = PiPuck(epuck_version=2)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("robot_pos/all")
    client.subscribe("robot/+")

def on_message(client, userdata, msg):
    global pos, all_pos
    try:
        data = json.loads(msg.payload.decode())
        if msg.topic.startswith("robot/"):
            robot_msg = json.loads(msg.payload.decode())
            print(f"Received message: {robot_msg}")
            pipuck.set_leds_colour("magenta")
            time.sleep(0.1)
            pipuck.set_leds_colour("off")
            return
        all_pos = data
        if robot_id in data:
            pos = data[robot_id]
    except json.JSONDecodeError:
        print(f"Invalid JSON: {msg.payload}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(Broker, Port, 240)
client.loop_start()

TURN_SPEED = 200
FORWARD_SPEED = 500

try:
    print("Chaser started.")
    while True:
        if not pos or runner_id not in all_pos:
            time.sleep(0.1)
            continue

        my_x, my_y = pos["position"]
        my_angle = pos["angle"]

        runner_data = all_pos[runner_id]
        runner_x, runner_y = runner_data["position"]

        dx = runner_x - my_x
        dy = runner_y - my_y

        angle_to_runner = math.degrees(math.atan2(dy, dx))
        angle_diff = (angle_to_runner - my_angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360  # Normalize to [-180, 180]

        distance = math.sqrt(dx**2 + dy**2)

        # Avoid edges of workspace (basic bounding box logic)
        if my_x < 0.3 or my_x > 1.8 or my_y < 0.3 or my_y > 0.8:
            pipuck.epuck.set_motor_speeds(-TURN_SPEED, TURN_SPEED)
            time.sleep(0.3)
            pipuck.epuck.set_motor_speeds(FORWARD_SPEED, FORWARD_SPEED)
            time.sleep(0.8)
            continue

        # Rotate to face runner
        if abs(angle_diff) > 5:
            if angle_diff > 0:
                pipuck.epuck.set_motor_speeds(-TURN_SPEED, TURN_SPEED)  # turn left
            else:
                pipuck.epuck.set_motor_speeds(TURN_SPEED, -TURN_SPEED)  # turn right
            time.sleep(abs(angle_diff) / 90.0)  # Estimate: 90° per second
            pipuck.epuck.set_motor_speeds(0, 0)
        else:
            # Drive forward
            pipuck.epuck.set_motor_speeds(FORWARD_SPEED, FORWARD_SPEED)
            time.sleep(0.5)
            pipuck.epuck.set_motor_speeds(0, 0)

        if distance < 0.2:
            print(f"Runner {runner_id} caught by {robot_id}")
            client.publish(f"robot/{robot_id}", "caught")
            pipuck.set_leds_colour("magenta")
            time.sleep(0.2)
            pipuck.set_leds_colour("off")

except KeyboardInterrupt:
    print("Chaser interrupted by user.")
finally:
    pipuck.epuck.set_motor_speeds(0, 0)
    client.loop_stop()
    print("Chaser stopped.")
