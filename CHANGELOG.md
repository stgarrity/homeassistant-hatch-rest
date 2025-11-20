# Changelog

All notable changes to this project will be documented in this file.

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
