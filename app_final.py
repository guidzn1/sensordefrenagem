import serial
import time
import pandas as pd
import numpy as np
import os
import sys
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler

# --- CONFIGURAÇÃO ---
PORTA = 'COM4'   # <--- CONFIRA SUA PORTA
BAUD_RATE = 9600

# Cores para o Terminal
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==============================================================================
# 1. TREINAMENTO DA IA
# ==============================================================================
limpar_tela()
print(f"{BOLD}--- INICIANDO SISTEMA DE FRENAGEM (AEB) ---{RESET}")
print("1. Carregando memória de treinamento...")

if not os.path.exists('dados_colisao.csv'):
    print(f"{RED}ERRO: 'dados_colisao.csv' não encontrado!{RESET}")
    sys.exit()

df = pd.read_csv('dados_colisao.csv')
df['Distancia_Passada'] = df['Distancia'].shift(1)
df['Target_Futuro'] = df['Distancia'].shift(-1)
df = df.dropna()

X = df[['Distancia', 'Distancia_Passada']].values
y = df['Target_Futuro'].values

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_norm = scaler_X.fit_transform(X)
y_norm = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

print("2. Treinando Rede Neural...")
mlp = MLPRegressor(hidden_layer_sizes=(10, 10), activation='relu', solver='adam', max_iter=500)
mlp.fit(X_norm, y_norm)
print(f"{GREEN}   Modelo treinado e carregado!{RESET}")

# ==============================================================================
# 2. CONEXÃO COM ARDUINO
# ==============================================================================
print(f"3. Conectando na porta {PORTA}...")
try:
    arduino = serial.Serial(PORTA, BAUD_RATE, timeout=0.1)
    time.sleep(2)
except Exception as e:
    print(f"{RED}ERRO AO CONECTAR: {e}{RESET}")
    sys.exit()

print(f"\n{GREEN}=== SISTEMA OPERANTE ==={RESET}")
print("Monitorando sensor... (Ctrl+C para sair)\n")

distancia_anterior = 50
travado = False
contador_travamento = 0

try:
    while True:
        if arduino.in_waiting > 0:
            try:
                linha = arduino.readline().decode('utf-8').strip()
                if not linha: continue
                
                dist_atual = int(linha)
                
                # --- FILTRO DE RUÍDO REFORÇADO ---
                velocidade_bruta = distancia_anterior - dist_atual
                
                # Se mudou menos de 6cm, considera ruído (mão tremendo) e zera
                if abs(velocidade_bruta) < 6: 
                    velocidade = 0
                else: 
                    velocidade = velocidade_bruta
                
                # Previsão IA
                entrada = np.array([[dist_atual, distancia_anterior]])
                entrada_norm = scaler_X.transform(entrada)
                prev_norm = mlp.predict(entrada_norm)
                prev_cm = scaler_y.inverse_transform(prev_norm.reshape(-1, 1))[0][0]

                # --- LÓGICA DE CONTROLE ---
                cor_barra = GREEN 

                if travado:
                    contador_travamento -= 1
                    if contador_travamento <= 0:
                        travado = False 
                    
                    msg = f"{RED}⛔ COLISÃO EVITADA! FREIOS ATIVOS ⛔{RESET}"
                    arduino.write(b'F') 
                    barra = "█" * 40
                    print(f"\r{msg} | {barra} | Travado por {contador_travamento} ciclos   ", end="")
                    continue

                # --- NOVAS REGRAS (MAIS DIFÍCEIS DE ATIVAR) ---
                
                # Regra 1: Colisão Iminente
                # Tem que prever batida em < 15cm (bem perto) E velocidade real > 8 (rápido)
                regra_1 = (prev_cm <= 15 and velocidade > 8)
                
                # Regra 2: Pânico (Alta Energia)
                # Velocidade muito alta (> 20) e distância < 60cm
                regra_2 = (velocidade > 20 and dist_atual < 60)

                if regra_1 or regra_2:
                    status = f"{RED}!!! PERIGO - FREANDO !!!{RESET}"
                    cor_barra = RED
                    travado = True
                    contador_travamento = 30 # Trava por menos tempo (~1.5s)
                    arduino.write(b'F')
                    
                # Aviso Amarelo (Alta velocidade, mas longe ou seguro)
                elif velocidade > 8:
                    status = f"{YELLOW}ALTA VELOCIDADE{RESET}"
                    cor_barra = YELLOW
                    arduino.write(b'L')
                    
                else:
                    status = f"{GREEN}MONITORANDO{RESET}"
                    cor_barra = GREEN
                    arduino.write(b'L')

                # Desenha a barra
                tamanho_barra = int(40 - (dist_atual / 3)) 
                if tamanho_barra < 0: tamanho_barra = 0
                if tamanho_barra > 40: tamanho_barra = 40
                
                desenho_barra = (cor_barra + "█" * tamanho_barra + RESET) + ("." * (40 - tamanho_barra))

                print(f"\rDist: {dist_atual:03d}cm | Vel: {velocidade:02d} | {desenho_barra} | {status}    ", end="")

                distancia_anterior = dist_atual
                
            except ValueError:
                pass
        time.sleep(0.05)

except KeyboardInterrupt:
    print(f"\n\n{RED}Sistema Desligado.{RESET}")
    arduino.close()