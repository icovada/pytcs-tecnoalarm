# MQTT script

This script exports data to MQTT and can be integrated with Home Assistant

## Prerequisites

Set up the `.env` file (as the `.env.example`) with all the required variables for the `pytcs` library and the MQTT broker.


### Docker Compose

A `docker-compose.yml` file is provided to start up the environment.

Build (only the first time): `docker compose build tecnoalarm`

Run: `docker compose up -d`

## Home Assistant 

MQTT window sensor and a (very basic) program configuration examples:

```yaml
mqtt:
  - binary_sensor:
      - name: "Room window"
        unique_id: room_window
        state_topic: "tecnoalarm/zones/room_window"
        value_template: "{{ 'ON' if value_json.status == 'OPEN' else 'OFF' }}"
        device_class: window
        device:
          identifiers: tecnoalarm
          name: Alarm
          manufacturer: TecnoAlarm
          model: TP10-42

  - alarm_control_panel:
      - name: "Program Total"
        unique_id: program_total
        state_topic: "tecnoalarm/programs/total/status"
        value_template: "{{ 'armed_away' if value_json.status != 0 else 'disarmed' }}"
        command_topic: "tecnoalarm/programs/total/set"
        supported_features:
        - arm_away
        code: !secret alarm_password
        payload_arm_away: "ON"
        payload_disarm: "OFF"
        device:
          identifiers: tecnoalarm
          name: Alarm
          manufacturer: TecnoAlarm
          model: TP10-42
```

In order to support more than one centrale, the variable `MULTIPLE_TCS` can be set to `True` and the topics will include the `serial` number as the example below:

```yaml
mqtt:
  - binary_sensor:
      - name: "Room window"
        unique_id: room_window
        state_topic: "tecnoalarm/<serial>/zones/room_window"
        value_template: "{{ 'ON' if value_json.status == 'OPEN' else 'OFF' }}"
        device_class: window
```