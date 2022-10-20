# Changelog

## [2.22.0] - October 2022

### Changed
- DSG-5445 Added metadata tag for Python 3.10
- DSG-5542 Removed metadata tag for Python 3.6

### Fixed
- DSG-4403 Fixed detection of configurable endpoint size for Atmel-ICE and Power Debugger
- DSG-5624 Fixed detection of serial ports, using pyserial for all operating systems (updated pyserial requirement)

## [2.20.3] - May 2022

### Added 
- DSG-3994 Added more ATmega328P AVR ISP protocol commands (beta)
- DSG-4533 Added TPI protocol (alpha) for test purposes
- DSG-3934 Added PID for EDBG in mass-storage mode
- DSG-4291 Added Curiosity Nano DFU to udev rules
- DSG-4864 Raise exception on HID write error

## [2.19.3] - October 2021

### Added
- DSG-3270 Added argument range checks for LE16, LE32
- DSG-3804 Added py39 to setup metadata

### Fixed
- DSG-3327 Fixed crash caused by logging device ID 'None'
- DSG-3817 Fixed SAM D21 user row programming

### Changed
- DSG-3272 Removed makefile
- DSG-3319 Documentation tweaks
- DSG-3324 Removed readthedocs yaml
- DSG-3816 Device detection filters by Atmel VID and 'CMSIS-DAP' string

## [2.18.3] - April 2021

### Changed
- DSG 3317 Tweaks to docstrings

## [2.18.2] - March 2021

### Added
- DSG-3109 Added missing constants

### Fixed
- DSG-2997 Typo fix in function name: find_matching_tools_ports
- DSG-2998 Removed blanket exception catches

### Changed
- DSG-3145 Switched from proprietary to MIT license

## [2.17.7] - December 2020

### Added
- DSG-2496 Added serial port test function
- DSG-2519 Added hint at missing udev rules
- DSG-2575 Added help for dialout group
- DSG-2775 Added requirements.txt

### Fixed
- DSG-2230 Naming consistency
- DSG-2596 Improved documentation
- DSG-2838 Docstring escape character

## [2.15.2] - October 2020

### Fixed
- DSG-2046 Python 3.8 support
- DSG-2233 Logging improvements - correct usage of logging module

## [2.10.0] - June 2020
- First public release to PyPi
