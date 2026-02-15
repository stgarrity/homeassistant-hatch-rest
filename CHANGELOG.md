# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-02-15

### Fixed
- **Fixed BLE connection contention with phone app.** Hatch Rest 1st gen only supports a single BLE connection at a time. The old coordinator polled every 30 seconds and scheduled redundant refreshes after commands, which monopolized the BLE slot and blocked the Hatch phone app from connecting. Commands were also delayed when the phone held the connection.

### Changed
- Increased poll interval from 30 seconds to 5 minutes to minimize BLE contention
- Replaced `async_request_refresh()` after commands with `async_set_updated_data()` — the library already reads state after each command, so we push it immediately without opening another BLE connection
- Removed broken `client.disconnect()` calls (the upstream library's disconnect method is a no-op that actually opens a connection)
- Corrected `iot_class` from `local_push` to `local_polling`

## [1.0.1] - 2025-11-20

### Fixed
- Fixed device naming to use the actual Bluetooth device name (e.g., "Cooper's Room") instead of "Hatch Rest"

## [1.0.0] - 2025-11-20

### Added
- Support for Hatch Rest+ (2nd generation) devices
- Automatic discovery via Bluetooth using manufacturer ID (1076 - Hatch Baby)
- ESP32 Bluetooth Proxy support for extended range

### Fixed
- Fixed API compatibility with pyhatchbabyrest 2.1.0+
  - Updated `is_on` to use `power` property
  - Updated `current_sound` to use `sound` property
  - Updated connection check to use `device` instead of `connected`
- Fixed `connect_async` function call to use correct parameter format

### Changed
- Updated Bluetooth discovery to support both original Hatch Rest (service UUID) and Hatch Rest+ (manufacturer ID)
- Improved connection handling and error recovery

## [0.1.0] - Initial Release

### Added
- Initial integration for Hatch Rest devices
- Light entity with RGB color and brightness control
- Bluetooth connectivity
- Config flow for easy setup
