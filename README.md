# rpi5-buildroot-tank-controller

This project consists of designing a from-scratch Embedded Linux system for the Raspberry Pi 5 to act as the central control unit for a tracked vehicle. The system integrates network infrastructure, real-time messaging, and a graphical interface.

<br>

## Key Features
- **Custom OS**: Built using Buildroot (LTS version) with a custom minimal kernel configuration.
- **Connectivity**: Configured as a **WiFi Access Point** (hostapd) with DHCP/DNS services (dnsmasq) to create a private network for the robot components.
- **Messaging**: Local **MQTT Broker (Mosquitto)** facilitating low-latency communication between the RPi5 and the vehicle's ESP32.
- **User Interface**: Custom **PyQt5 GUI** designed for touchscreens, featuring real-time telemetry and motor control.
- **Boot Optimization**: Automated service management via custom **init scripts** and a personal **splash screen** for a professional boot experience.

<br>

## System Architecture
The system follows a distributed architecture:
1. **HMI (RPi5)**: Runs the `Tank_Interface_GUI.py` application.
2. **Communication**: Commands (FORWARD, LEFT, etc.) are published via MQTT.
3. **Execution**: An **ESP32** subscribes to these topics and coordinates with an **STM32** to drive the dual-motor tread system using PWM signals.



<br>

## Software Stack
- **Buildroot**: Toolchain, Bootloader (U-Boot), and optimized RootFS.
- **Python 3**: PyQt5 for the GUI, Paho-MQTT for messaging.
- **Networking**: Hostapd, Dnsmasq, Mosquitto, SSH.

<br>

## How to Build
To generate the firmware image:
1. Copy the `configs/rpi5_tank_defconfig` to the Buildroot `configs/` directory.
2. Run `make rpi5_tank_defconfig`.
3. Run `make` to compile the cross-toolchain, kernel, and rootfs.
4. The final image `sdcard.img` will be located in `output/images/`.

<br>

## Application Requirements (GUI)
The `Tank_Interface_GUI.py` application is integrated into the Buildroot image, but can also be run standalone for testing:

- **Python 3.11+**
- **PyQt5**: `pip install PyQt5`
- **Paho-MQTT**: `pip install paho-mqtt`
- **MQTT Broker**: A running Mosquitto broker at the IP specified in the script.
