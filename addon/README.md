# Home Assistant ADDON

Home assistant Addon to read sensor values and insert alarms of some Tecnoalarm centrali.

## Prerequisites

Copy the addon folder to `/homeassistant/addons/tecnoalarmTcs`.


### Installation

Install the addon as explained in https://developers.home-assistant.io/docs/add-ons/tutorial/.

Configure the addon with your parameters and then start the addon.

The first time, the login will be done with username and password. The next logins will be done with token and appid (stored from the first login).

This addon does not support multi factor authentication. 

## Home Assistant 

MQTT Sensors configuration:

```yaml
mqtt:
binary_sensor:
    - name: "Room window"
      unique_id: room_window
      state_topic: "tecnoalarm/zones/room_window"
      value_template: "{{ value_json.status }}"
      payload_off: "CLOSED"
      payload_on: "OPEN"
      availability_topic: "tecnoalarm/zones/room_window"
      availability_template: "{{ value_json.available }}"
      device_class: "window"
      device:
        identifiers: tecnoalarm
        name: Alarm
        manufacturer: TecnoAlarm
        model: TP10-42
    - name: "Room Door"
      unique_id: room_door
      state_topic: "tecnoalarm/zones/room_door"
      value_template: "{{ value_json.status }}"
      payload_off: "CLOSED"
      payload_on: "OPEN"
      availability_topic: "tecnoalarm/zones/room_door"
      availability_template: "{{ value_json.available }}"
      device_class: "door"
      device:
        identifiers: tecnoalarm
        name: Alarm
        manufacturer: TecnoAlarm
        model: TP10-42
  lock:                                                  
    - name: "Program Total"
      unique_id: program_total                                        
      state_topic: "tecnoalarm/programs/program_total"          
      command_topic: "tecnoalarm/programs/program_total/set"       
      value_template: "{{ value_json.status }}"          
      command_template: '{ "command": "{{ value }}" }'       
      optimistic: false                                  
      qos: 0                                               
      retain: false                                      
    - name: "Program Garage"
      unique_id: program_garage                                    
      state_topic: "tecnoalarm/programs/program_garage"          
      command_topic: "tecnoalarm/programs/program_garage/set"       
      value_template: "{{ value_json.status }}"          
      command_template: '{ "command": "{{ value }}" }'       
      optimistic: false                                  
      qos: 0                                               
      retain: false  
```
