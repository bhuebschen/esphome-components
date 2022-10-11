# ayufan's + GrumpyMeow's esphome custom components

This repository contains a collection of my custom components
for [ESPHome](https://esphome.io/).

## 1. Usage

Use latest [ESPHome](https://esphome.io/) (at least v1.18.0)
with external components and add this to your `.yaml` definition:

```yaml
external_components:
  - source: github://bhuebschen/esphome-components
```

## 2. Components

### 2.1. `inode_ble`

A component to support [iNode.pl](https://inode.pl/) devices
(energy meters and magnetometers).

#### 2.1.1. Example

```yaml
# the BT window is configured to be a small portion
# of interval to have a lot of time to handle WiFi
esp32_ble_tracker:
  scan_parameters:
    active: false
    interval: 288ms
    window: 144ms

# monitor RSSI and Power, Energy, and Battery Levels
# the `constant` defines a how many pulses are per unit
# ex.: 1500 pulses/kWh
# all sensors of inode_ble:
# - avg_w
# - avg_dm3
# - avg_raw
# - total_kwh
# - total_dm3
# - total_raw
# - battery_level
# - light_level
sensor:
  - platform: ble_rssi
    mac_address: 00:0b:57:36:df:51
    name: "Emeter RSSI"
    icon: mdi:wifi
    expire_after: 10min

  - platform: inode_ble
    mac_address: 00:0b:57:36:df:51
    constant: 1500
    avg_w:
      name: 'Emeter Power'
      expire_after: 10min
    total_kwh:
      name: 'Emeter Energy'
      expire_after: 10min
    battery_level:
      name: 'Emeter Battery Level'
      expire_after: 10min
```

### 2.2. `eq3_v2`

A component to support [eQ-3 Radiator Thermostat Model N](https://www.eq-3.com/products/homematic/detail/radiator-thermostat-model-n.html),
and maybe also other ones.

This uses custom `esp32_ble_clients` implementation to support
Bluetooth on ESP32.

#### 2.2.1. Stability

This is quite challenging to ensure that BT works well with WiFi.
Ideally it is preferred to run only `eq3_v2` component
on a single device, with all basic services. Usage of complex services,
or complex logic can cause stability issues.

I also noticed that extensive logging (like in `VERBOSE` mode)
during the BT connection cases WiFi to loose beacons,
and results in disconnect.

#### 2.2.2. Example

```yaml
# time is required by `eq3_v2` to send
# an accurate time spec when requesting
# current state
time:
  - platform: sntp
    id: sntp_time

# refresh component state every 30mins,
# and announce it to Home Assistant MQTT
climate:
  - platform: eq3_v2
    id: office_eq3
    name: Office EQ3
    mac_address: 00:1A:22:12:5B:34
    update_interval: 30min
    valve: # optional, allows to see valve state in %
      name: Office EQ3 Valve State
      expire_after: 61min

# allow to force refresh component state
switch:
  - platform: template
    name: "Refresh Office EQ3"
    lambda: "return false;"
    turn_on_action:
      - component.update: office_eq3
```

### 2.3. `tplink_plug`

This plugin allows to emulate TPLink HS100/HS110 type of plug
using LAN protocol with ESPHome. Especially useful where you
want to use existing software that supports these type of plugs,
but not others.

```yaml
tplink_plug:
  plugs:
    voltage: my_voltage
    current: my_current
    total: my_total
    state: relay

# Example config for Gosund SP111

sensor:
  - id: my_daily_total
    platform: total_daily_energy
    name: "MK3S+ Daily Energy"
    power_id: my_power

  - platform: hlw8012
    sel_pin:
      number: GPIO12
      inverted: true
    cf_pin: GPIO05
    cf1_pin: GPIO04
    current:
      id: my_current
      name: "MK3S+ Current"
      expire_after: 1min
    voltage:
      id: my_voltage
      name: "MK3S+ Voltage"
      expire_after: 1min
    power:
      id: my_power
      name: "MK3S+ Power"
      expire_after: 1min
      filters:
        - multiply: 0.5
    energy:
      id: my_total
      name: "MK3S+ Energy"
      expire_after: 1min
      filters:
        - multiply: 0.5
    change_mode_every: 3
    update_interval: 15s
    voltage_divider: 748
    current_resistor: 0.0012

    # {"PowerSetCal":10085}
    # {"VoltageSetCal":1581}
    # {"CurrentSetCal":3555}

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO13
      mode: INPUT
      inverted: true
    name: "MK3S+ Button"
    on_press:
      - switch.toggle: relay

switch:
  - platform: gpio
    id: relay
    name: "MK3S+ Switch"
    pin: GPIO15
    restore_mode: RESTORE_DEFAULT_OFF
    icon: mdi:power-socket-eu
    on_turn_on:
      - output.turn_on: led
    on_turn_off:
      - output.turn_off: led

status_led:
  pin:
    number: GPIO00
    inverted: true

output:
  - platform: gpio
    pin: GPIO02
    inverted: true
    id: led
```

### 2.4. `memory`

Simple component that periodically prints free memory of node.

```yaml
memory:
```

### 2.5. `esp32_camera_web_server` (upstreamed)

_This component was removed as it is part of upstream esphome starting with version 2021.11: https://esphome.io/components/esp32_camera_web_server.html_

Simple component to expose `esp32_camera` via HTTP snapshot and stream interface:

- http://esphome:8080/
- http://esphome:8081/

```yaml
esp32_camera_web_server:
  # define only what is needed
  # only a single stream is supported at a given time
  - port: 8080
    mode: stream
  - port: 8081
    mode: snapshot

esp32_camera:
  name: My Camera
  external_clock:
    pin: GPIO0
    frequency: 20MHz
  i2c_pins:
    sda: GPIO26
    scl: GPIO27
  data_pins: [GPIO5, GPIO18, GPIO19, GPIO21, GPIO36, GPIO39, GPIO34, GPIO35]
  vsync_pin: GPIO25
  href_pin: GPIO23
  pixel_clock_pin: GPIO22
  power_down_pin: GPIO32
  resolution: 1600x1200
  jpeg_quality: 12
```
### 2.6 Comet Blue
Basic component to:
* get the current temperature
* set the target temperature
This component doesn't support scheduling as I do this through Home Assistant by changing the target temperature.

#### 2.6.1 Example configuration
```yaml
wifi:
  ssid: "..."
  password: "..."
  power_save_mode: none

debug:

# Enable logging
logger:
  level: DEBUG

# Enable Home Assistant API
api:

ota:

time:
  - platform: sntp
    id: sntp_time

climate:
  - platform: cometblue
    pin: 0000
    id: trv_cb1
    name: Radiator 1
    mac_address: 01:23:45:56:78:90
    update_interval: 5min
    temperature_offset: 0
    window_open_sensitivity: 4
    window_open_minutes: 10

switch:
  - platform: template
    name: "Refresh Radiator 1"
    lambda: "return false;"
    turn_on_action:
      - component.update: trv_cb1

```


### 2.7. `e131`

A component to support [E1.31](https://www.doityourselfchristmas.com/wiki/index.php?title=E1.31_(Streaming-ACN)_Protocol). This allows to control addressable LEDs over WiFi, by pushing data right into LEDs.

The most popular application to push data would be: [JINX](http://www.live-leds.de/jinx-v1-3-with-resizable-mainwindow-real-dmx-and-sacne1-31/).

#### 2.7.1 Example configuration
```yaml
e131_custom:
  method: multicast # Register E1.31 to Multicast group
  # method: unicast # Listen only on port

light:
  - platform: neopixelbus
    pin: D4
    method: ESP8266_UART1
    num_leds: 189
    name: LEDs
    effects:
      - e131:
          universe: 1
          channels: RGB
          # channels: RGBW: to support additional W-channel
```

There are three modes of operation:

- `MONO`: this supports 1 channel per LED (luminance), up-to 512 LEDs per universe
- `RGB`: this supports 3 channels per LED (RGB), up-to 170 LEDs (3*170 = 510 bytes) per universe
- `RGBW`: this supports 4 channels per LED (RGBW), up-to 128 LEDs (4*128 = 512 bytes) per universe

If there's more LEDs than allowed per-universe, additional universe will be used.
In the above example of 189 LEDs, first 170 LEDs will be assigned to 1 universe,
the rest of 19 LEDs will be automatically assigned to 2 universe.

It is possible to enable multiple light platforms to listen to the same universe concurrently,
allowing to replicate the behaviour on multiple strips.

Sometimes it might be advised to improved of connection. By default `multicast` is used,
but in some circumstances it might be advised to connect directly via IP to the esp-node.

### 2.8. `adalight`

A component to support [Adalight](https://learn.adafruit.com/adalight-diy-ambient-tv-lighting). This allows to control addressable LEDs over UART, by pushing data right into LEDs.

The most useful to use [Prismatik](https://github.com/psieg/Lightpack) to create an immersive effect on PC.

#### 2.8.1 Example configuration
```yaml
adalight:

uart:
  - id: adalight_uart
    tx_pin: TX
    rx_pin: RX
    baud_rate: 115200

light:
  - platform: neopixelbus
    pin: D4
    method: ESP8266_UART1
    num_leds: 189
    name: LEDs
    effects:
      - adalight:
          uart_id: adalight_uart
```

### 2.9. `WLED`

A component to support [WLED](https://github.com/Aircoookie/WLED/wiki/UDP-Realtime-Control). This allows to control addressable LEDs over WiFi/UDP, by pushing data right into LEDs.

The most useful to use [Prismatik](https://github.com/psieg/Lightpack) to create an immersive effect on PC.

#### 2.9.1 Example configuration
```yaml
wled:

light:
  - platform: neopixelbus
    pin: D4
    method: ESP8266_UART1
    num_leds: 189
    name: LEDs
    effects:
      - wled:
          # port: 21324 # optional port to allow usage of multiple LED strips
```

## 3. Author & License

Kamil Trzciński, MIT, 2019-2021
