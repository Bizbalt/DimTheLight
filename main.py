from machine import UART, Pin
import time


# Konfiguriere UART1 (Pico TX = Pin 4, Pico RX = Pin 5)
# Die Standard-Baudrate für den RAK3172 (RUI3) ist 115200.
lora_uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

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

# all AT commands refer to m5 stack asr6501 firmware.
# 1. Modul-Version abfragen (Verbindungstest)
#send_at_command("AT+VER=?")
# todo: read data from cirpstack_key file
# with open("chirpstack_key", "r") as f:
#     name_device = f.readline().strip()
#     device_eui = f.readline().strip()
#     join_eui = f.readline().strip()
#     app_key = f.readline().strip()


# 2. LoRaWAN-Modus aktivieren (1 = LoRaWAN, 0 = P2P)
send_at_command("AT+NWM=1")

def authorize_lamp(lampname="Lampe1_a"):
    lamps = {"Lampe1_a": {"device_eui": "11DAF29BEE739281", "join_eui": "52FE2E02FF435854",
                          "app_key": "F9C8C14DB8B357FF1AD158233F2CFEBE"},
             "LED_2": {"device_eui": "058F765DEEE4C078", "join_eui": "D615D621ED9C765A",
                       "app_key": "2BF20406D9ECB278A922F2EE5D896916"}}

    send_at_command("AT+DEVEUI=" + lamps[lampname]["device_eui"])
    send_at_command("AT+APPEUI=" + lamps[lampname]["join_eui"])
    send_at_command("AT+APPKEY=" + lamps[lampname]["app_key"])


# 3. Keys für OTAA setzen
authorize_lamp("Lampe1_a")

# 4. Join-Prozess starten
send_at_command("AT+JOIN=1:0:10:16", wait_ms=10000)

# 5. Dummy-Payload senden, um Empfangsfenster zu öffnen!
# Wir senden "00" (ein leeres Byte) auf Port 1.
# Das teilt ChirpStack mit: "Ich bin da, hast du was für mich?"
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