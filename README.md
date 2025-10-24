# Hatch Rest - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant custom integration for **Hatch Rest** (1st generation, Bluetooth-only) sleep light.

## Features

✨ **Auto-discovery via Bluetooth** - No manual configuration needed
🎨 **RGB color control** - Full color picker support
💡 **Brightness adjustment** - 0-100% brightness slider
🔌 **Local control** - No cloud dependency, pure Bluetooth LE
⚡ **Fast response** - Direct BLE communication

## Supported Devices

- ✅ **Hatch Rest (1st Gen)** - Bluetooth-only model
- ❌ Rest+ / Rest 2nd Gen - Use WiFi-based integrations instead

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the 3 dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/stgarrity/homeassistant-hatch-rest`
5. Category: `Integration`
6. Click "Add"
7. Find "Hatch Rest" in HACS and click "Download"
8. Restart Home Assistant
9. Go to **Settings** → **Devices & Services** → **Add Integration**
10. Search for "Hatch Rest" and follow the setup

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/hatch_rest` folder to your `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for "Hatch Rest"

## Setup

### Automatic Discovery (Recommended)

1. Make sure your Hatch Rest is powered on and within Bluetooth range
2. The integration will automatically discover your device
3. You'll see "Hatch Rest - Configure" in your integrations page
4. Click "Configure" and confirm the connection

### Manual Setup

1. Find your Hatch Rest MAC address (use nRF Connect app or similar)
2. Add the integration manually and enter the MAC address
3. Click "Submit" to connect

## Usage

### Light Entity

The integration creates a light entity with full RGB and brightness control:

**Entity ID:** `light.hatch_rest`

**Controls:**
- 🎨 **Color** - RGB color picker
- 💡 **Brightness** - 0-100% slider
- 🔌 **Power** - On/Off toggle

### Example Automations

#### Gradual Wake-Up Routine

```yaml
automation:
  - alias: "Gentle Wake Up"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      # Start dim orange
      - service: light.turn_on
        target:
          entity_id: light.hatch_rest
        data:
          brightness: 10
          rgb_color: [255, 100, 0]

      # Gradually increase brightness over 10 minutes
      - repeat:
          count: 10
          sequence:
            - delay: "00:01:00"
            - service: light.turn_on
              target:
                entity_id: light.hatch_rest
              data:
                brightness: "{{ 10 + repeat.index * 24 }}"
```

#### Bedtime Routine

```yaml
automation:
  - alias: "Bedtime"
    trigger:
      platform: time
      at: "21:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hatch_rest
        data:
          brightness: 30
          rgb_color: [255, 50, 0]  # Warm orange

      # Gradually dim over 30 minutes
      - repeat:
          count: 30
          sequence:
            - delay: "00:01:00"
            - service: light.turn_on
              target:
                entity_id: light.hatch_rest
              data:
                brightness: "{{ 30 - repeat.index }}"

      # Turn off
      - service: light.turn_off
        target:
          entity_id: light.hatch_rest
```

#### Nap Time

```yaml
automation:
  - alias: "Nap Time"
    trigger:
      platform: time
      at: "13:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.hatch_rest
        data:
          brightness: 20
          rgb_color: [100, 100, 255]  # Soft blue
```

## Troubleshooting

### Device Not Discovered

**Problem:** Hatch Rest doesn't show up in discovered integrations

**Solutions:**
1. Make sure Bluetooth is enabled on your Home Assistant host
2. Ensure the device is powered on
3. Move the device closer to your HA host
4. Check that the device isn't already connected to the Hatch app on your phone
5. Try power cycling the Hatch Rest

### Connection Failed

**Problem:** "Cannot connect to device" error

**Solutions:**
1. Make sure the device isn't connected to another app (Hatch app on phone)
2. Power cycle the Hatch Rest (unplug and plug back in)
3. Restart the Bluetooth service on your HA host
4. Check Home Assistant logs for detailed error messages

### Entity Shows "Unavailable"

**Problem:** Light entity is unavailable

**Solutions:**
1. Check if device is powered on
2. Verify device is within Bluetooth range (~10-15 feet)
3. Check Home Assistant logs for connection errors
4. Try reloading the integration
5. Remove and re-add the integration

### Checking Logs

View detailed logs in Home Assistant:

**Settings** → **System** → **Logs**

Filter by: `hatch_rest`

## Limitations

### What This Integration Does NOT Support

❌ **Sound/Audio control** - Not included in v0.1.0 (may add later)
❌ **Volume control** - Not included in v0.1.0
❌ **Built-in wake-up programs** - Hardware doesn't support this
❌ **Time-to-rise features** - Only on WiFi models

**However:** You can create custom wake-up routines using Home Assistant automations (see examples above)!

### Device Limitations

The Hatch Rest (1st gen, Bluetooth-only) is a simple remote-controlled device:
- No internal scheduling or programs
- No WiFi connectivity
- Must be within Bluetooth range of HA host
- Commands are immediate only (no delayed execution in device)

## Technical Details

### Dependencies

- `pyhatchbabyrest>=2.1.0` - Python library for Hatch Rest control
- Home Assistant Bluetooth integration

### Platforms

- `light` - RGB light with brightness control

### IoT Class

`local_push` - Device sends state updates via BLE notifications

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Home Assistant logs
3. [Open an issue](https://github.com/stgarrity/homeassistant-hatch-rest/issues) with:
   - Home Assistant version
   - Integration version
   - Hatch Rest model
   - Error logs
   - Steps to reproduce

## Credits

This integration uses the excellent [`pyhatchbabyrest`](https://github.com/kjoconnor/pyhatchbabyrest) library by @kjoconnor for BLE communication.

## License

MIT License - see [LICENSE](LICENSE) file for details
