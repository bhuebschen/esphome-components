import re
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_MAC_ADDRESS, PLATFORM_ESP32
from esphome.core import coroutine

ESP_PLATFORMS = [PLATFORM_ESP32]
CONFLICTS_WITH = ['esp32_ble_tracker', 'esp32_ble_beacon']
