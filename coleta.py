import serial
import csv
import time
import os

# --- CONFIGURAÇÃO ---
PORTA = 'COM4'   # <--- CONFIRA SE AINDA É ESSA PORTA
BAUD_RATE = 9600
NOME_ARQUIVO = 'dados_colisao.csv'

# Mostra onde o arquivo vai ser salvo para você não perder ele
print(f"O arquivo será salvo em: {os.getcwd()}\{NOME_ARQUIVO}")

try:
    arduino = serial.Serial(PORTA, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Conectado! Pode começar a mexer a mão.")
except:
    print("ERRO: Arduino não encontrado. Verifique a porta COM.")
    exit()

# Abre o arquivo para escrita
# 'utf-8' ajuda a evitar erros de caracteres estranhos
with open(NOME_ARQUIVO, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Tempo', 'Distancia']) # Cabeçalho

    inicio = time.time()
    
    print("\n--- GRAVANDO (Ctrl+C para parar) ---")
    
    try:
        while True:
            if arduino.in_waiting > 0:
                try:
                    linha = arduino.readline().decode('utf-8').strip()
                    if linha:
                        distancia = int(linha)
                        tempo_decorrido = round(time.time() - inicio, 2)
                        
                        print(f"Salvando: {tempo_decorrido}s -> {distancia}cm")
                        writer.writerow([tempo_decorrido, distancia])
                        
                        # --- O SEGREDO ESTÁ AQUI ---
                        file.flush() # Força o Python a salvar no HD agora!
                        
                except ValueError:
                    pass
    except KeyboardInterrupt:
        print(f"\nSTOP! Coleta finalizada.")
        print(f"Verifique o arquivo em: {NOME_ARQUIVO}")
        arduino.close()