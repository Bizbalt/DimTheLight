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


# --- Beispielablauf ---

# 1. Modul-Version abfragen (Verbindungstest)
send_at_command("AT+VER=?")

# 2. LoRaWAN-Modus aktivieren (1 = LoRaWAN, 0 = P2P)
send_at_command("AT+NWM=1")
# todo: get your chirpstack ip
# data from Chirpstack: Name Device	Device EUI (EUI64)	Join EUI (EUI64)	Application key

name_device = "Lampe1_a"
device_eui = "11DAF29BEE739281"
join_eui = "52FE2E02FF435854"
app_key = "F9C8C14DB8B357FF1AD158233F2CFEBE"

# todo: read data from cirpstack_key file
# with open("chirpstack_key", "r") as f:
#     name_device = f.readline().strip()
#     device_eui = f.readline().strip()
#     join_eui = f.readline().strip()
#     app_key = f.readline().strip()


# 3. Keys für OTAA setzen (Ersetze die X mit deinen echten TTN/Chirpstack Keys)
print(send_at_command("AT+DEVEUI=" + device_eui))
print(send_at_command("AT+APPEUI=" + join_eui))
print(send_at_command("AT+APPKEY=" + app_key))

# 4. Join-Prozess starten (Netzwerkbeitritt)
# Format: AT+JOIN=1:0:10:8 (Join aktivieren:Auto-Join nach stromverlust aus:Intervall:Versuche)
print(send_at_command("AT+JOIN=1:0:10:8", wait_ms=5000))



# Kurz warten, bis der Join im Netzwerk verarbeitet wurde
time.sleep(5)
#blubb
# 5. Payload senden (Sende den Hex-String "AABBCC" auf Port 2)
# Wichtig: LoRaWAN Payloads müssen beim RAK meist als Hex-String übergeben werden.
send_at_command("AT+SEND=2:AABBCC", wait_ms=3000)