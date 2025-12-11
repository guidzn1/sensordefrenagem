import customtkinter as ctk
import serial
import threading
import pandas as pd
import numpy as np
import time
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import os

# --- CONFIGURAÇÃO ---
PORTA_ARDUINO = 'COM4' 
BAUD_RATE = 9600

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppFrenagem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Frenagem Autônoma - IA Preditiva")
        self.geometry("600x600")
        self.resizable(False, False)

        self.travado_em_colisao = False

        self.scaler_X = None
        self.scaler_y = None
        self.mlp = None

        self.status_ia = "Carregando IA..."
        self.treinar_ia()

        self.criar_interface()

        self.arduino = None
        self.rodando = True
        self.thread_sensor = threading.Thread(target=self.loop_sensor)
        self.thread_sensor.daemon = True
        self.thread_sensor.start()

    def criar_interface(self):
        self.lbl_titulo = ctk.CTkLabel(self, text="MONITORAMENTO DE COLISÃO (AEB)", 
                                     font=("Roboto", 24, "bold"), text_color="#E0E0E0")
        self.lbl_titulo.pack(pady=20)

        self.frame_status = ctk.CTkFrame(self, width=450, height=150, corner_radius=20)
        self.frame_status.pack(pady=10)
        
        self.lbl_status = ctk.CTkLabel(self.frame_status, text="AGUARDANDO...", 
                                     font=("Arial", 30, "bold"))
        self.lbl_status.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_reset = ctk.CTkButton(self, text="REINICIAR SISTEMA / DESTRAVAR", 
                                     command=self.resetar_sistema,
                                     width=300, height=40,
                                     fg_color="#555555", hover_color="#333333",
                                     state="disabled")
        self.btn_reset.pack(pady=10)

        self.frame_dados = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_dados.pack(pady=10)

        self.lbl_real_titulo = ctk.CTkLabel(self.frame_dados, text="Distância Real", font=("Arial", 14))
        self.lbl_real_titulo.grid(row=0, column=0, padx=30)
        self.lbl_real_val = ctk.CTkLabel(self.frame_dados, text="-- cm", font=("Roboto", 40, "bold"), text_color="#4facfe")
        self.lbl_real_val.grid(row=1, column=0, padx=30)

        self.lbl_vel_titulo = ctk.CTkLabel(self.frame_dados, text="Aproximação", font=("Arial", 14))
        self.lbl_vel_titulo.grid(row=0, column=1, padx=30)
        self.lbl_vel_val = ctk.CTkLabel(self.frame_dados, text="-- cm/s", font=("Roboto", 40, "bold"), text_color="#fad390")
        self.lbl_vel_val.grid(row=1, column=1, padx=30)

        self.lbl_prev_titulo = ctk.CTkLabel(self.frame_dados, text="Previsão (IA)", font=("Arial", 14))
        self.lbl_prev_titulo.grid(row=0, column=2, padx=30)
        self.lbl_prev_val = ctk.CTkLabel(self.frame_dados, text="-- cm", font=("Roboto", 40, "bold"), text_color="#ff9a9e")
        self.lbl_prev_val.grid(row=1, column=2, padx=30)

        self.lbl_barra = ctk.CTkLabel(self, text="Nível de Risco de Colisão", font=("Arial", 12))
        self.lbl_barra.pack(pady=(10, 0))
        self.barra_risco = ctk.CTkProgressBar(self, width=400, height=20)
        self.barra_risco.set(0)
        self.barra_risco.pack(pady=5)

        self.lbl_footer = ctk.CTkLabel(self, text="Status do Sistema: Iniciando...", font=("Arial", 10), text_color="gray")
        self.lbl_footer.pack(side="bottom", pady=10)

    def treinar_ia(self):
        try:
            if not os.path.exists('dados_colisao.csv'):
                self.status_ia = "ERRO: CSV não encontrado!"
                return

            df = pd.read_csv('dados_colisao.csv')
            df['Distancia_Passada'] = df['Distancia'].shift(1)
            df['Target_Futuro'] = df['Distancia'].shift(-1)
            df = df.dropna()

            X = df[['Distancia', 'Distancia_Passada']].values
            y = df['Target_Futuro'].values

            self.scaler_X = MinMaxScaler()
            self.scaler_y = MinMaxScaler()
            X_norm = self.scaler_X.fit_transform(X)
            y_norm = self.scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

            self.mlp = MLPRegressor(hidden_layer_sizes=(10, 10), activation='relu', solver='adam', max_iter=500)
            self.mlp.fit(X_norm, y_norm)
        except Exception as e:
            self.status_ia = f"Erro na IA: {e}"

    def resetar_sistema(self):
        self.travado_em_colisao = False
        self.btn_reset.configure(state="disabled", fg_color="#555555")
        self.frame_status.configure(fg_color="#00b894")
        self.lbl_status.configure(text="SISTEMA REINICIADO")
        self.barra_risco.configure(progress_color="#3b8ed0")
        if self.arduino:
            self.arduino.write(b'L')

    def loop_sensor(self):
        try:
            self.arduino = serial.Serial(PORTA_ARDUINO, BAUD_RATE, timeout=1)
            time.sleep(2)
            self.atualizar_footer(f"Conectado na {PORTA_ARDUINO}! Sistema Ativo.")
        except:
            self.atualizar_footer(f"ERRO: Não foi possível conectar na {PORTA_ARDUINO}")
            return

        distancia_anterior = 50
        
        while self.rodando:
            if self.travado_em_colisao:
                if self.arduino: self.arduino.write(b'F')
                time.sleep(0.1)
                continue

            if self.arduino and self.arduino.in_waiting > 0:
                try:
                    linha = self.arduino.readline().decode('utf-8').strip()
                    if not linha: continue
                    
                    dist_atual = int(linha)
                    
                    # CÁLCULO DA VELOCIDADE
                    velocidade_bruta = distancia_anterior - dist_atual
                    
                    # --- FILTRO DE RUÍDO (AQUI ESTÁ A CORREÇÃO) ---
                    # Se a velocidade for menor que 3 (ruído da mão tremendo), ignora
                    if abs(velocidade_bruta) < 3:
                        velocidade = 0
                    else:
                        velocidade = velocidade_bruta

                    entrada = np.array([[dist_atual, distancia_anterior]])
                    entrada_norm = self.scaler_X.transform(entrada)
                    prev_norm = self.mlp.predict(entrada_norm)
                    prev_cm = self.scaler_y.inverse_transform(prev_norm.reshape(-1, 1))[0][0]

                    self.after(0, self.atualizar_tela, dist_atual, prev_cm, velocidade)

                    # --- LÓGICA DE TRAVAMENTO COM FILTRO ---
                    # Regra 1: Perto (< 20cm) e Rápido (> 3)
                    condicao_1 = (prev_cm <= 20 and velocidade > 3)
                    
                    # Regra 2: Pânico (> 10) mas só se não estiver longe demais (< 150)
                    condicao_2 = (velocidade > 10 and dist_atual < 150)

                    if condicao_1 or condicao_2:
                        self.travado_em_colisao = True
                        self.arduino.write(b'F')
                        self.after(0, self.mostrar_tela_travada)
                    else:
                        self.arduino.write(b'L')

                    distancia_anterior = dist_atual
                    
                except ValueError:
                    pass
            time.sleep(0.05)

    def mostrar_tela_travada(self):
        self.frame_status.configure(fg_color="#cf000f")
        self.lbl_status.configure(text="⛔ COLISÃO EVITADA ⛔", text_color="white")
        self.barra_risco.configure(progress_color="red")
        self.barra_risco.set(1.0)
        self.lbl_vel_val.configure(text="TRAVADO")
        self.btn_reset.configure(state="normal", fg_color="#3498db")

    def atualizar_tela(self, real, prev, velocidade):
        if self.travado_em_colisao:
            return

        self.lbl_real_val.configure(text=f"{real} cm")
        self.lbl_prev_val.configure(text=f"{prev:.1f} cm")
        sinal = "+" if velocidade > 0 else ""
        self.lbl_vel_val.configure(text=f"{sinal}{velocidade} cm/ciclo")

        if velocidade < 2 and real > 5:
            self.frame_status.configure(fg_color="#00b894") 
            self.lbl_status.configure(text="MANOBRA SEGURA", text_color="white")
            self.barra_risco.configure(progress_color="#00b894")
            self.barra_risco.set(0.1)
            return

        risco = 0
        if prev <= 0: prev = 0.1
        risco = 1 - (prev / 50) 
        if risco < 0: risco = 0
        self.barra_risco.set(risco)

        if prev < 30:
            self.frame_status.configure(fg_color="#f39c12")
            self.lbl_status.configure(text="⚠️ ALTA VELOCIDADE", text_color="black")
            self.barra_risco.configure(progress_color="orange")
        else:
            self.frame_status.configure(fg_color="#00b894")
            self.lbl_status.configure(text="SEGURO", text_color="white")
            self.barra_risco.configure(progress_color="#00b894")

    def atualizar_footer(self, msg):
        self.after(0, lambda: self.lbl_footer.configure(text=msg))

    def on_closing(self):
        self.rodando = False
        if self.arduino: self.arduino.close()
        self.destroy()

if __name__ == "__main__":
    app = AppFrenagem()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()