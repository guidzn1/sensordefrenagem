import serial
import time

PORTA = 'COM4'   # <--- CONFIRA SUA PORTA
BAUD_RATE = 9600

print(f"Tentando conectar na {PORTA}...")

try:
    arduino = serial.Serial(PORTA, BAUD_RATE, timeout=1)
    time.sleep(2) # Tempo para o Arduino reiniciar
    print("Conectado! Lendo dados brutos...")
except Exception as e:
    print(f"ERRO DE CONEXÃO: {e}")
    exit()

print("--- O QUE O ARDUINO ESTÁ ENVIANDO ---")
print("(Se não aparecer nada abaixo em 5 segundos, temos um problema)")

while True:
    if arduino.in_waiting > 0:
        # Lê a linha bruta (em bytes)
        linha_bytes = arduino.readline() 
        
        try:
            # Tenta converter para texto
            linha_texto = linha_bytes.decode('utf-8').strip()
            print(f"Recebi: '{linha_texto}'")
        except:
            print(f"Recebi lixo (bytes): {linha_bytes}")