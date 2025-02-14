#!/usr/bin/with-contenv bashio

CONFIG_PATH=/data/options.json

export MQTT_HOST="$(bashio::config 'mqtt_host')"
export MQTT_PORT="$(bashio::config 'mqtt_port')"
export MQTT_USERNAME="$(bashio::config 'mqtt_username')"
export MQTT_PASSWORD="$(bashio::config 'mqtt_password')"
export TCS_USERNAME="$(bashio::config 'tcs_username')"
export TCS_PASSWORD="$(bashio::config 'tcs_password')"
export TCS_SERIAL="$(bashio::config 'tcs_serial')"
export TCS_TOKEN="$(bashio::config 'tcs_token')"

touch /data/tcsSession.json

python3 /main.py
