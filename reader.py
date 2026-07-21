import datetime
import json
import os

import paho.mqtt.client as mqtt
from psycopg import Error, connect

MQTT_HOST = os.environ.get("MQTT_HOST", "mosquitto.default.svc.cluster.local")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "rtl_433/#")

# Connection info (PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD) comes from the
# environment - psycopg.connect() with no arguments reads the standard libpq
# env vars automatically.


def insert_reading(unit, reading):
    try:
        with connect() as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(
                    "insert into recent_readings (unit,reading) values (%s,%s) "
                    "on conflict (unit) do update set reading=excluded.reading",
                    (unit, reading),
                )
    except Error as e:
        # loop_forever() must keep running, so log and move on instead of exiting
        print(e, flush=True)


def insert_all_reading(timestamp, model, id, channel, reading):
    try:
        with connect() as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(
                    "insert into all_readings (timestamp,model,id,channel,reading) "
                    "values (%s,%s,%s,%s,%s) on conflict do nothing",
                    (timestamp, model, id, channel, reading),
                )
    except Error as e:
        print(e, flush=True)


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected to {MQTT_HOST}:{MQTT_PORT} (rc={reason_code})", flush=True)
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    line = msg.payload.decode(errors="replace")
    print(f"{msg.topic} {line}", flush=True)

    try:
        d = json.loads(line)
    except json.JSONDecodeError as e:
        print("invalid json:", e, line, flush=True)
        return

    model = d.get("model", "")
    channel = d.get("channel", "")
    id = d.get("id", "")
    timestamp = d.get("timestamp", datetime.datetime.now().isoformat())

    if "id" not in d.keys():
        print("no id:", line)
        print("keys:", d.keys())
        for key in d.keys():
            print(ascii(key), key, '=="id":', key == "id")
            print([ord(x) for x in key])
    else:
        if "message_type" in d:
            if d["message_type"] == 49:
                unit = model + "-wind" + "[" + str(d["id"]) + "," + str(d["channel"]) + "]"
            else:
                unit = model + "-temp" + "[" + str(d["id"]) + "," + str(d["channel"]) + "]"
        elif "channel" in d:
            unit = model + "[" + str(d["id"]) + "," + str(d["channel"]) + "]"
        else:
            unit = model + "[" + str(d["id"]) + "]"
        insert_reading(unit, line)

    insert_all_reading(timestamp, model, id, channel, line)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_forever()
