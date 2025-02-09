import time
import os
import json
import paho.mqtt.client as mqtt
from datetime import datetime as dt

from pytcs_tecnoalarm import TCSSession
from pytcs_tecnoalarm.api_models import ZoneStatusEnum

session_key = os.getenv("SESSION_KEY")
app_id = int(os.getenv("APPID"))
serial = os.getenv("SERIAL")
sleep = int(os.getenv("UPDATE_SLEEP_SECONDS"))

mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
mqtt_qos = int(os.getenv("MQTT_QOS", "0"))
mqtt_retain = os.getenv("MQTT_RETAIN", "true").lower() == "true"
programs_allow_enable = os.getenv("PROGRAMS_ALLOW_ENABLE", "false").lower() == "true"
multiple_tcs = os.getenv("MULTIPLE_TCS", "false").lower() == "true"

mqtt_topic_base = "tecnoalarm"
mqtt_topic_centrale = "centrale"
mqtt_topic_zone = "zones"
mqtt_topic_program = "programs"

def clean_name(str):
    return str.replace(" ", "_").replace(".", "_").replace("-", "_").lower()

def log(name, message):
    print(f"{dt.now()} [{name}] {message}")

def mqtt_on_message(client, userdata, message):
    log("MQTT", f"Messagge received: '{message.topic}': {message.payload.decode()}")
    program_name = message.topic.split("/")[-2]
    program_id = programs_ids.get(program_name, 'error')
    if programs_allow_enable:
        if program_id == 'error':
            log("pytcs", "ERROR program not found")
        else:
            payload = message.payload.decode().lower()
            if payload == 'on':
                log("pytcs", f"Enable program '{program_name}' (id={program_id})")
                s.enable_program(program_id)
            elif payload == 'off':
                log("pytcs", f"Disable program '{program_name}' (id={program_id})")
                s.disable_program(program_id)
            else:
                log("pytcs", "ERROR wrong payload")

if __name__ == "__main__":
    log("main", "START")
    s = TCSSession(session_key, app_id)

    log("pytcs", "get_centrali")
    s.get_centrali()
    centrale = s.centrali[serial]

    log("pytcs", "select_centrale")
    s.select_centrale(centrale.tp)

    log("MQTT", "Connect")
    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttClient.username_pw_set(mqtt_username, mqtt_password)
    mqttClient.connect(mqtt_host, mqtt_port, sleep + 60)

    if multiple_tcs:
        mqtt_topic_base += "/" + serial
        log("MQTT", "Support multiple tcs")

    if programs_allow_enable:
        log("MQTT", "Subscribe to messages")
        mqttClient.on_message = mqtt_on_message
        p = s.get_programs()
        programs_ids = {}
        for programstatus, programdata in zip(p.root, centrale.tp.status.programs):
           if len(programdata.zones) == 0:
               continue

           name = clean_name(programdata.description)
           topic = "{}/{}/{}/set".format(mqtt_topic_base, mqtt_topic_program, name)
           mqttClient.subscribe(topic)
           programs_ids[name] = programdata.idx

    topic = "{}/{}".format(mqtt_topic_base, mqtt_topic_centrale)
    message = centrale.tp.model_dump()
    message.pop("status", None)
    message = json.dumps(message)
    res = mqttClient.publish(topic, message, mqtt_qos, mqtt_retain)

    mqttClient.loop_start()

    while True:
        log("main", "----------------")
        log("pytcs", "get_zones")
        z = s.get_zones()
        for zone in z.root:
            if zone.status == ZoneStatusEnum.UNKNOWN or not zone.allocated:
                continue

            name = clean_name(zone.description)
            topic = "{}/{}/{}".format(mqtt_topic_base, mqtt_topic_zone, name)
            message = json.dumps(zone.__dict__)
            res = mqttClient.publish(topic, message, mqtt_qos, mqtt_retain)

        log("pytcs", "get_programs")
        p = s.get_programs()
        for programstatus, programdata in zip(p.root, centrale.tp.status.programs):
            if len(programdata.zones) == 0:
                continue

            name = clean_name(programdata.description)

            topic = "{}/{}/{}/info".format(mqtt_topic_base, mqtt_topic_program, name)
            message = json.dumps(programdata.__dict__)
            res = mqttClient.publish(topic, message, mqtt_qos, mqtt_retain)

            topic = "{}/{}/{}/status".format(mqtt_topic_base, mqtt_topic_program, name)
            message = json.dumps(programstatus.__dict__)
            res = mqttClient.publish(topic, message, mqtt_qos, mqtt_retain)

        time.sleep(sleep)

    mqttClient.disconnect()
    mqttClient.loop_stop()
