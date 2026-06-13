from machine import UART, Pin
import time


# Konfiguriere UART1 (Pico TX = Pin 4, Pico RX = Pin 5)
# Die Standard-Baudrate für den RAK3172 (RUI3) ist 115200.
lora_uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

lamps_dict = \
        {"Lampe1_a": {"device_eui": "11DAF29BEE739281", "join_eui": "52FE2E02FF435854",
                      "app_key": "F9C8C14DB8B357FF1AD158233F2CFEBE"},
         "LED_2": {"device_eui": "058F765DEEE4C078", "join_eui": "D615D621ED9C765A",
                   "app_key": "2BF20406D9ECB278A922F2EE5D896916"}}

def routine():
    # Check whether UART communication works
    send_at_command("AT+VER=?")

    # Set the device specific WAN keys
    authorize_lamp(lamps_dict["Lampe1_a"])

    # Attempt a LoRaWAN join
    join_wan()

    # Check for messages from the WAN server
    while True:
        read_queue()
        time.sleep(10)


def send_at_command(cmd, wait_ms=2000):
    print(f"Sende: {cmd}")
    # Kommando senden mit Carriage Return und Line Feed
    lora_uart.write(cmd + "\r\n")
    time.sleep_ms(wait_ms)

    # Antwort lesen
    if lora_uart.any():
        response = lora_uart.read().decode('utf-8').strip()
        print(f"Antwort:\n{response}\n")
        return response
    else:
        print("Keine Antwort vom Modul.\n")
        return None

def authorize_lamp(devicekeys = lamps_dict["Lampe1_a"]):
    # 2. LoRaWAN-Modus aktivieren (1 = LoRaWAN, 0 = P2P)
    send_at_command("AT+NWM=1")

    send_at_command("AT+DEVEUI=" + devicekeys["device_eui"])
    send_at_command("AT+APPKEY=" + devicekeys["app_key"])
    send_at_command("AT+APPEUI=" + devicekeys["join_eui"])

def join_wan():
    # 4. Join-Prozess starten
    send_at_command("AT+JOIN=1:0:10:16", wait_ms=10000)

def read_queue():
    print("Sende Dummy-Uplink, um Downlink abzuholen...")
    lora_uart.write("AT+SEND=1:00\r\n")

    # Wir lauschen dynamisch für 10 Sekunden (10000 Millisekunden)
    timeout_ms = 10000
    start_time = time.ticks_ms()

    print("Lese Antworten aus dem Buffer (Warte bis zu 10 Sekunden)...")

    # Solange die 10 Sekunden nicht abgelaufen sind...
    while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
        if lora_uart.any():
            response = lora_uart.read().decode('utf-8').strip()

            # Manchmal kommen leere Strings an, die filtern wir heraus
            if response:
                print(response)

        # Kurze Pause, um die CPU des Picos nicht zu 100% auszulasten
        time.sleep_ms(100)

    print("Lauschen beendet.")