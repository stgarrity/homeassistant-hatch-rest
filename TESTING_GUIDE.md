# Testing Guide - Hatch Rest Integration on macOS + Docker

**Challenge:** Docker Desktop on macOS runs in a Linux VM, and Bluetooth devices don't pass through easily.

**Good news:** There are several workarounds! 🎉

---

## Your Current Setup

```
Container: ha-dev
Image: ghcr.io/home-assistant/home-assistant:stable
Network: kerblwelt_default (bridge)
Config: /Users/sgarrity/projects/kerblwelt/ha-dev/config
Status: Stopped
```

**Issue:** Container has no Bluetooth device access, and macOS Docker doesn't easily support it.

---

## Testing Options (Ranked by Difficulty)

### ⭐ Option 1: ESPHome Bluetooth Proxy (RECOMMENDED)

**Best option** if you have an ESP32 lying around.

**What it is:**
- Use an ESP32 as a Bluetooth proxy
- ESP32 connects to your network
- HA connects to ESP32 via network
- ESP32 handles Bluetooth communication with Hatch

**Pros:**
- ✅ Works perfectly with Docker
- ✅ Extends Bluetooth range
- ✅ Solves the Docker/macOS Bluetooth issue
- ✅ Can be used for other BLE devices too

**Cons:**
- ❌ Requires ESP32 hardware (~$5-10)
- ❌ 10-15 minutes setup time

**Setup:**
1. Flash ESP32 with ESPHome Bluetooth Proxy firmware
2. Add to HA via ESPHome integration
3. Bluetooth devices will auto-discover through proxy

**Detailed instructions:** https://esphome.github.io/bluetooth-proxies/

---

### ⭐⭐ Option 2: Run HA Directly on macOS (NO DOCKER)

**Temporary setup** just for testing this integration.

**What it is:**
- Install Home Assistant Core directly on macOS
- Native Bluetooth access
- Test integration, then go back to Docker

**Pros:**
- ✅ Direct Bluetooth access
- ✅ Fast testing
- ✅ No hardware needed

**Cons:**
- ❌ Separate HA instance from your main Docker one
- ❌ Some setup required
- ❌ Only for testing, not production

**Quick Setup:**

```bash
# 1. Create virtual environment
python3 -m venv ~/hass-test
source ~/hass-test/bin/activate

# 2. Install Home Assistant
pip3 install homeassistant

# 3. Create config directory
mkdir -p ~/.homeassistant-test

# 4. Copy our integration
cp -r /Users/sgarrity/projects/hatch/homeassistant-hatch-rest/custom_components/hatch_rest \
     ~/.homeassistant-test/custom_components/

# 5. Start HA
hass -c ~/.homeassistant-test
```

Then open http://localhost:8123 and add the integration.

**To clean up later:**
```bash
rm -rf ~/hass-test ~/.homeassistant-test
```

---

### ⭐⭐⭐ Option 3: Bluetooth Proxy Container (EXPERIMENTAL)

Use a separate container to bridge Bluetooth to your HA container via network.

**What it is:**
- Run `bluetooth-mqtt-gateway` or similar
- It accesses macOS Bluetooth
- Exposes devices via MQTT
- HA connects via MQTT

**Pros:**
- ✅ Works with your existing Docker setup

**Cons:**
- ❌ Complex setup
- ❌ May not work well on macOS
- ❌ Additional MQTT broker needed

**Not recommended** unless you're already using MQTT.

---

### ⭐⭐⭐⭐ Option 4: Modify Docker Container for Host Bluetooth (HARD)

Try to pass through macOS Bluetooth to Docker.

**Reality:** This is **extremely difficult** on macOS and often doesn't work because:
- Docker runs in a Linux VM
- macOS Bluetooth stack is different from Linux
- CoreBluetooth (macOS) ≠ BlueZ (Linux)

**Verdict:** ❌ **Don't try this** - it's a rabbit hole

---

## My Recommendation

**For quick testing:** Use **Option 2** (HA on macOS directly)

**For long-term use:** Use **Option 1** (ESP32 Bluetooth Proxy)

---

## Option 2 - Detailed Step-by-Step

Let's go with this since it's the fastest way to test:

### Step 1: Install HA Core on macOS

```bash
# Create virtual environment
cd /Users/sgarrity/projects/hatch
python3 -m venv hass-test-env
source hass-test-env/bin/activate

# Install Home Assistant
pip3 install homeassistant

# Verify installation
hass --version
```

### Step 2: Set Up Config Directory

```bash
# Create config directory
mkdir -p ~/.homeassistant-test
cd ~/.homeassistant-test

# Create custom_components directory
mkdir -p custom_components

# Copy our integration
cp -r /Users/sgarrity/projects/hatch/homeassistant-hatch-rest/custom_components/hatch_rest \
     custom_components/
```

### Step 3: Start Home Assistant

```bash
# Start HA (it will create initial config)
hass -c ~/.homeassistant-test
```

**First start takes 2-3 minutes** - it's installing dependencies.

You'll see:
```
INFO (MainThread) [homeassistant.bootstrap] Home Assistant initialized in Xs
INFO (MainThread) [homeassistant.core] Starting Home Assistant
```

### Step 4: Access Web UI

Open browser: http://localhost:8123

**First time:**
1. Create user account
2. Set up location (skip for testing)
3. Complete onboarding

### Step 5: Add Hatch Rest Integration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Hatch Rest"**
4. Follow setup wizard

**If auto-discovery works:**
- You'll see "Hatch Rest - Configure" automatically
- Click "Configure" and confirm

**If manual setup needed:**
- Enter your Hatch MAC address
- Click Submit

### Step 6: Test Features

Once added, you should see:
- ✅ **Device:** "Hatch Rest"
- ✅ **Entity:** `light.hatch_rest`

**Test controls:**
1. **Power:** Turn on/off
2. **Color:** Click the light, use color picker
3. **Brightness:** Use slider
4. **Availability:** Unplug Hatch, entity should show "Unavailable"
5. **Reconnect:** Plug back in, should auto-recover

### Step 7: Test Automation

Create a simple automation:

```yaml
# In Settings → Automations → Create Automation → Edit in YAML
automation:
  - alias: "Test Hatch"
    trigger:
      platform: time
      at: "00:00:01"  # Adjust to near future
    action:
      - service: light.turn_on
        target:
          entity_id: light.hatch_rest
        data:
          brightness: 50
          rgb_color: [255, 100, 0]
```

### Step 8: Check Logs

If anything goes wrong:

```bash
# View logs in real-time
tail -f ~/.homeassistant-test/home-assistant.log

# Or in HA UI:
# Settings → System → Logs
# Filter by: hatch_rest
```

### Step 9: Clean Up (When Done)

```bash
# Stop HA (Ctrl+C in terminal)

# Deactivate virtual environment
deactivate

# Remove test environment (optional)
rm -rf ~/hass-test-env ~/.homeassistant-test
```

---

## Option 1 - ESP32 Bluetooth Proxy (For Production)

If you want to use this long-term with your Docker setup:

### What You Need

- ESP32 board (ESP32, ESP32-C3, or ESP32-S3)
- USB cable
- 5-10 minutes

### Quick Setup

1. **Go to:** https://esphome.github.io/bluetooth-proxies/

2. **Click "Install"** and select your ESP32 model

3. **Connect ESP32** via USB to your computer

4. **Follow web flasher** - it will install firmware

5. **Configure WiFi** through the web interface

6. **Add to Home Assistant:**
   - Settings → Devices & Services
   - Should auto-discover "ESPHome Bluetooth Proxy"
   - Click Configure

7. **Done!** Now Bluetooth devices will be discovered through the proxy

### Benefits

- Works perfectly with Docker
- Extends Bluetooth range (put ESP32 near your Hatch)
- Can handle multiple BLE devices
- Costs ~$5-10 for the ESP32

---

## Troubleshooting

### "No module named 'bleak'" Error

**On macOS HA:**
```bash
source hass-test-env/bin/activate
pip install bleak
```

**In Docker:**
- Should auto-install, but if not, add to `configuration.yaml`:
```yaml
homeassistant:
  packages: !include_dir_named packages
```

### "Bluetooth device is turned off"

**On macOS:**
- Enable Bluetooth in System Preferences
- Grant Terminal Bluetooth access:
  - System Settings → Privacy & Security → Bluetooth
  - Enable for Terminal

### "Cannot connect to device"

1. Make sure Hatch is powered on
2. Ensure it's not connected to phone app
3. Move closer to computer/ESP32
4. Power cycle the Hatch (unplug/replug)

### Integration Doesn't Show Up

```bash
# Check if integration loaded
grep "hatch_rest" ~/.homeassistant-test/home-assistant.log

# Manually restart HA
# In UI: Developer Tools → YAML → Restart
```

### Container Can't See Bluetooth (Docker)

**This is expected on macOS!**

You need Option 1 (ESP32 proxy) or Option 2 (native macOS HA) to test.

---

## Quick Decision Tree

```
Do you have an ESP32?
  ├─ Yes → Use Option 1 (Bluetooth Proxy)
  └─ No → Do you want long-term Docker use?
        ├─ Yes → Buy ESP32 ($5-10), use Option 1
        └─ No → Use Option 2 (macOS HA) for quick test
```

---

## What I Recommend For You

Based on your setup, here's my suggestion:

**Short-term (Today):**
1. ✅ **Use Option 2** - Run HA directly on macOS
2. ✅ Takes 10 minutes to set up
3. ✅ Test all features with your Hatch
4. ✅ Verify integration works
5. ✅ Clean up when done

**Long-term (For Production):**
1. ⚪ **Get an ESP32** (~$8 on Amazon)
2. ⚪ Flash with Bluetooth Proxy firmware
3. ⚪ Use with your Docker HA setup
4. ⚪ Works for Hatch + any future BLE devices

---

## Ready to Test?

Let me know which option you want to try, and I'll help you set it up!

**My vote: Start with Option 2 (macOS native HA) for quick testing now.**

Then if you like the integration, get an ESP32 for your production Docker setup.

Want me to walk you through the setup? 🚀
