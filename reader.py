import os

import paho.mqtt.client as mqtt

MQTT_HOST = os.environ.get("MQTT_HOST", "mosquitto.default.svc.cluster.local")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "rtl_433/#")


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected to {MQTT_HOST}:{MQTT_PORT} (rc={reason_code})", flush=True)
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    print(f"{msg.topic} {msg.payload.decode(errors='replace')}", flush=True)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_forever()
