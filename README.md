# HA Arduino Dashboard Integration

> **Work in progress:** This integration is under active development and is not feature-complete. Expect changes and missing functionality.

Home Assistant companion integration for [ha-arduino-dashboard](https://github.com/Lamsand/ha-arduino-dashboard), by [Lamsand](https://github.com/Lamsand).

## Project goal

The long-term goal is for this integration to handle all MQTT communication behind the scenes for the Arduino dashboard. Home Assistant users should be able to configure their entities and apps in Home Assistant instead of having to manage the MQTT details themselves.

That goal is not reached yet. The integration currently supports only the apps listed below; the other apps in the Arduino dashboard are not integrated with Home Assistant yet.

## App support status

| Arduino dashboard app | Integration status |
| --- | --- |
| Basics | Included |
| Car | Included |
| Energy | Included |
| EVCC | Not integrated yet |
| Heat pump | Not integrated yet |
| Lights | Not integrated yet |
| Mower | Not integrated yet |
| Music | Not integrated yet |
| Ventilation | Not integrated yet |
| Waste | Not integrated yet |

“Included” means the app can currently be enabled and configured through this Home Assistant integration. It does not mean every possible feature of that Arduino app is supported.

## Requirements

- Home Assistant
- The MQTT integration configured and connected to an MQTT broker
- An Arduino running [ha-arduino-dashboard](https://github.com/Lamsand/ha-arduino-dashboard)

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Add `Lamsand/ha-arduino-dashboard-integration` as a custom repository with category **Integration**.
3. Install **HA Arduino Dashboard** and restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**.
5. Search for **HA Arduino Dashboard** and add it.

### Manual

1. Copy `custom_components/ha_arduino_dashboard` into the `custom_components` directory of your Home Assistant configuration.
2. Restart Home Assistant.
3. Add **HA Arduino Dashboard** from **Settings → Devices & services**.

## Configuration

Open the integration options and enable the apps you want to use. Entity selections are optional; select only the entities you want the integration to publish.

### Basics

The Basics app is always enabled and requires no configuration. It publishes the local time in `HH:MM` format to `home/time` at the start of every minute. It also publishes `5s` to `home/interval` every five seconds and `30s` every thirty seconds, aligned to the clock boundaries. At the 30-second boundaries, both values are published in sequence.

### Car

| Home Assistant option | MQTT topic |
| --- | --- |
| Battery / fuel | `car/battery` |
| Range | `car/cruisingRange` |
| Charging power | `car/chargingPower` |
| Target charge | `car/targetCharge` |

### Energy

| Home Assistant option | MQTT topic |
| --- | --- |
| PV production | `energy/currentProduction` |
| Smart meter | `energy/currentImport` |
| Total consumption | `energy/currentConsumption` |

Sensor values are published at startup and when they change. These messages are retained. Entities in `unknown` or `unavailable` state are skipped.

## Enabling and disabling apps

Car and Energy can be enabled or disabled independently. Basics is always enabled. A disabled configurable app does not publish MQTT messages, and its Home Assistant device entry is removed when the integration reloads.

## Checking MQTT messages

In Home Assistant, open **Settings → Devices & services → MQTT → Listen to a topic**. Subscribe to `energy/#` or `car/#` to inspect the integration's messages.

## Related projects

- Arduino dashboard: [Lamsand/ha-arduino-dashboard](https://github.com/Lamsand/ha-arduino-dashboard)
- Home Assistant integration: [Lamsand/ha-arduino-dashboard-integration](https://github.com/Lamsand/ha-arduino-dashboard-integration)
