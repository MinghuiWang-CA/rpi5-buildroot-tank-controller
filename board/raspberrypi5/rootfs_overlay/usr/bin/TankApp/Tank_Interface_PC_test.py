#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time

# =============== CONFIGURATION ===============
BROKER_ADDRESS = "192.168.4.1"  # Change to your Pi or broker IP
PORT = 1883
ROBOT_NAME = "Tank_1"

# Topics (must match ESP32)
TOPIC_CMD_MOVE      = f"Tanks/{ROBOT_NAME}/cmd/move"
TOPIC_CMD_MODE      = f"Tanks/{ROBOT_NAME}/cmd/mode"
TOPIC_CMD_LIGHTS    = f"Tanks/{ROBOT_NAME}/cmd/lights"
# =============================================


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" Connected to MQTT broker")
        client.subscribe(f"Tanks/{ROBOT_NAME}/#")  # Listen for any feedback
    else:
        print(f" Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    print(f" Received [{msg.topic}] → {msg.payload.decode()}")


# ---------------- COMMAND SENDERS ----------------
def send_move_command(client, direction, speed):
    payload = f"{direction.upper()} {speed}"
    client.publish(TOPIC_CMD_MOVE, payload)
    print(f" Sent MOVE command: {payload}")


def send_mode_command(client, mode):
    payload = mode.upper()
    client.publish(TOPIC_CMD_MODE, payload)
    print(f" Sent MODE command: {payload}")


def send_lights_command(client, state):
    payload = state.upper()
    client.publish(TOPIC_CMD_LIGHTS, payload)
    print(f" Sent LIGHTS command: {payload}")


# ---------------- MAIN LOOP ----------------
def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to MQTT broker...")
    client.connect(BROKER_ADDRESS, PORT, 60)
    client.loop_start()

    try:
        while True:
            print("\nCommands:")
            print("1 - Move FORWARD")
            print("2 - Move BACKWARD")
            print("3 - Turn LEFT")
            print("4 - Turn RIGHT")
            print("5 - STOP")
            print("6 - Toggle LIGHTS ON/OFF")
            print("7 - Change MODE (MANUAL/AUTONOMOUS)")
            print("q - Quit")

            choice = input("Select: ").strip().lower()

            if choice == "1":
                send_move_command(client, "FORWARD", 100)
            elif choice == "2":
                send_move_command(client, "BACKWARD", 100)
            elif choice == "3":
                send_move_command(client, "LEFT", 70)
            elif choice == "4":
                send_move_command(client, "RIGHT", 70)
            elif choice == "5":
                send_move_command(client, "FORWARD", 0)
            elif choice == "6":
                state = input("Enter ON/OFF: ")
                send_lights_command(client, state)
            elif choice == "7":
                mode = input("Enter MANUAL or AUTONOMOUS: ")
                send_mode_command(client, mode)
            elif choice == "q":
                break
            else:
                print("Invalid option")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
