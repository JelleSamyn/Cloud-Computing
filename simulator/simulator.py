import time
import json
import random
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 1883
JOYSTICK_TOPIC = "controller/joystick"
BUTTONS_TOPIC = "controller/buttons"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}", flush=True)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected from MQTT Broker with result code {rc}", flush=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Attempt to connect with backoff
connected = False
retry_delay = 2
while not connected:
    try:
        print(f"Connecting to MQTT Broker at {BROKER}:{PORT}...", flush=True)
        client.connect(BROKER, PORT, 60)
        connected = True
    except Exception as e:
        print(f"Connection failed ({e}). Retrying in {retry_delay}s...", flush=True)
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 60)

client.loop_start()

print("Simulator running. Publishing data...", flush=True)
try:
    while True:
        # Joystick data: normally [-100, 100], 5% chance of out of bounds anomaly
        if random.random() < 0.05:
            x = random.choice([-150, -120, 120, 150])
            y = random.choice([-150, -120, 120, 150])
            print(f"[Telemetry ANOMALY] Generated out-of-bounds coords: x={x}, y={y}", flush=True)
        else:
            x = random.randint(-100, 100)
            y = random.randint(-100, 100)
            
        joystick_payload = {
            "x": x,
            "y": y
        }
        client.publish(JOYSTICK_TOPIC, json.dumps(joystick_payload))
        
        # Buttons data: A and B button states
        buttons_payload = {
            "button_a": random.choice([True, False]),
            "button_b": random.choice([True, False])
        }
        client.publish(BUTTONS_TOPIC, json.dumps(buttons_payload))
        
        time.sleep(5)
except KeyboardInterrupt:
    print("Simulator stopping...", flush=True)
finally:
    client.loop_stop()
    client.disconnect()
