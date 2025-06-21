import logging
import time
import os
import json
import paho.mqtt.client as mqtt

from pytcs_tecnoalarm import TCSSession
from pytcs_tecnoalarm.api_models import ZoneStatusEnum
from logger import get_logger

debug = os.getenv("DEBUG", "true").lower() == "true"
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

LOGGER = get_logger("")
LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)

def clean_name(str):
    return str.replace(" ", "_").replace(".", "_").replace("-", "_").lower()

def mqtt_on_message(client, userdata, message):
    LOGGER.info("(MQTT) Messagge received: '%s': %s", message.topic, message.payload.decode())
    try:
        program_name = message.topic.split("/")[-2]
        program_id = programs_ids.get(program_name, 'error')
        if programs_allow_enable:
            if program_id == 'error':
                LOGGER.error("(pytcs) Program not found")
            else:
                payload = message.payload.decode().lower()
                if payload == 'on':
                    LOGGER.info("(pytcs) Enable program '%s' (id=%d)", program_name, program_id)
                    s.enable_program(program_id)
                elif payload == 'off':
                    LOGGER.info("(pytcs) Disable program '%s' (id=%d)", program_name, program_id)
                    s.disable_program(program_id)
                else:
                    LOGGER.error("(pytcs) Wrong payload")
    except Exception as e:
        LOGGER.exception(e)

if __name__ == "__main__":
    LOGGER.info("START")
    s = TCSSession(session_key, app_id)

    LOGGER.debug("(pytcs) get_centrali")
    s.get_centrali()
    centrale = s.centrali[serial]

    LOGGER.debug("(pytcs) select_centrale")
    s.select_centrale(centrale.tp)

    LOGGER.info("(MQTT) Connect")
    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttClient.username_pw_set(mqtt_username, mqtt_password)
    mqttClient.connect(mqtt_host, mqtt_port, sleep + 60)

    if multiple_tcs:
        mqtt_topic_base += "/" + serial
        LOGGER.info("(MQTT) Support multiple tcs")

    if programs_allow_enable:
        LOGGER.info("(MQTT) Subscribe to messages")
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
        LOGGER.debug("----------------")
        LOGGER.debug("(pytcs) get_zones")
        z = s.get_zones()
        for zone in z.root:
            if zone.status == ZoneStatusEnum.UNKNOWN or not zone.allocated:
                continue

            name = clean_name(zone.description)
            topic = "{}/{}/{}".format(mqtt_topic_base, mqtt_topic_zone, name)
            message = json.dumps(zone.__dict__)
            res = mqttClient.publish(topic, message, mqtt_qos, mqtt_retain)

        LOGGER.debug("(pytcs) get_programs")
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
