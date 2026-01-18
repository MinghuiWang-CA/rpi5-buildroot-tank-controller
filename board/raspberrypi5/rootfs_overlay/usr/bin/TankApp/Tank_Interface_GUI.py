#!/usr/bin/env python3
import sys
import time
import os
import warnings
import paho.mqtt.client as mqtt

from PyQt5 import QtWidgets, uic, QtCore, QtGui


# Here we should include fake packages not necessarily used
# to force students to look for them while building their image
# import ujson
# import Pillow
# import aiohttp
# import psutil
### A.K

# Suppress DeprecationWarning from sip module
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sip")

# ================= CONFIGURATION =================
BROKER_ADDRESS = "192.168.4.1"
PORT = 1883
ROBOT_NAME = "Tank_1" # <-- you can change the robot name  
# for each student group if you find the same name means they cheated

TOPIC_CMD_MOVE   = f"Tanks/{ROBOT_NAME}/cmd/move"
TOPIC_CMD_MODE   = f"Tanks/{ROBOT_NAME}/cmd/mode"
TOPIC_CMD_LIGHTS = f"Tanks/{ROBOT_NAME}/cmd/lights"
TOPIC_FEEDBACK   = f"Tanks/{ROBOT_NAME}/feedback/#"
# =================================================

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RES_DIR = os.path.join(BASE_DIR, "ressources")
UI_FILE = os.path.join(RES_DIR, "Tank_GUI.ui")  

# ---------- MQTT Worker Thread ----------
class MqttClient(QtCore.QThread):
    message_received = QtCore.pyqtSignal(str, str)
    connected = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected_flag = False
        self.running = True

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✓ Connected to MQTT broker")
            self.connected_flag = True
            self.connected.emit(True)
            client.subscribe(f"Tanks/{ROBOT_NAME}/#")
        else:
            print(f"✗ Connection failed with code {rc}")
            self.connected.emit(False)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        print(f"{msg.topic} → {payload}")
        self.message_received.emit(msg.topic, payload)

    def run(self):
        try:
            self.client.connect(BROKER_ADDRESS, PORT, 60)
            self.client.loop_start()
            while self.running:
                time.sleep(0.1)
        except Exception as e:
            print(f"MQTT Error: {e}")

    def stop(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()

    # ----------- Publish methods -----------
    def send_move_command(self, direction, speed):
        payload = f"{direction.upper()} {speed}"
        self.client.publish(TOPIC_CMD_MOVE, payload)
        print(f"MOVE: {payload}")

    def send_mode_command(self, mode):
        self.client.publish(TOPIC_CMD_MODE, mode.upper())
        print(f"MODE: {mode.upper()}")

    def send_lights_command(self, state):
        self.client.publish(TOPIC_CMD_LIGHTS, state.upper())
        print(f"LIGHTS: {state.upper()}")

# ---------- Main GUI ----------
class TankGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Correctly load .ui from resources
        if os.path.exists(UI_FILE):
            uic.loadUi(UI_FILE, self)
        else:
            raise FileNotFoundError(f"UI file not found: {UI_FILE}")

        self.showFullScreen()  # optional

        # MQTT Thread
        self.mqtt = MqttClient()
        self.mqtt.message_received.connect(self.handle_mqtt_message)
        self.mqtt.connected.connect(self.on_mqtt_connected)
        self.mqtt.start()

        # UI Connections
        self.left_engine_bt.pressed.connect(self.move_left)
        self.right_engine_bt.pressed.connect(self.move_right)
        self.forward_bt.pressed.connect(self.move_forward)
        self.backward_bt.pressed.connect(self.move_backward)
        self.stop_bt.pressed.connect(self.stop_movement)
        self.motors_speed_slider.valueChanged.connect(self.update_speed)
        

        self.reverse = False
        self.speed_value = 0
        self.displayed_speed = 0

        # Initial UI setup
        self.actual_speed.display(0)
        self.speed_disp_left.display(0)
        self.speed_disp_right.display(0)

    # ---------- MQTT Handlers ----------
    def on_mqtt_connected(self, ok):
        if ok:
            self.status_label.setText("✓ MQTT connected IP: " + BROKER_ADDRESS )
        else:
            self.status_label.setText("✗ MQTT connection failed")

    def handle_mqtt_message(self, topic, payload):
        if "speed" in topic.lower():
            try:
                speed_val = int(payload)
                self.actual_speed.display(speed_val)
            except ValueError:
                pass

    # ---------- UI Logic ----------
    def move_left(self):
        self.mqtt.send_move_command("LEFT", self.speed_value)
        self.mvstatus_label.setText("LEFT")
        self.speed_disp_left.display(self.displayed_speed )
        self.speed_disp_right.display(-self.displayed_speed )

    def move_right(self):
        self.mvstatus_label.setText("RIGHT")
        self.mqtt.send_move_command("RIGHT", self.speed_value)
        self.speed_disp_left.display(-self.displayed_speed)
        self.speed_disp_right.display(self.displayed_speed)
        
        
    def move_forward(self):
        self.mqtt.send_move_command("FORWARD", self.speed_value)
        self.mvstatus_label.setText("FORWARD")
        self.speed_disp_left.display(self.displayed_speed )
        self.speed_disp_right.display(self.displayed_speed )
        
    def move_backward(self):
        self.mqtt.send_move_command("BACKWARD", self.speed_value)
        self.mvstatus_label.setText("BACKWARD")
        self.speed_disp_left.display(-self.displayed_speed )
        self.speed_disp_right.display(-self.displayed_speed )
        
    def stop_movement(self):
        self.mqtt.send_move_command("STOP", 0)
        self.mvstatus_label.setText("STOP")
        self.speed_disp_left.display(0)
        self.speed_disp_right.display(0)

    def update_speed(self, value):
       # rescale 0-99 to 0-255
        self.speed_value = int(value * 255 / 99)
        self.displayed_speed = value
        self.actual_speed.display(self.displayed_speed)
        
    def closeEvent(self, event):
        self.mqtt.stop()
        event.accept()

# ---------- Main ----------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TankGUI()
    window.show()
    sys.exit(app.exec_())
