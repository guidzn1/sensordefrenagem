import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# --- 1. CARREGAMENTO E PREPARAÇÃO DOS DADOS ---
print("Carregando dados...")
# Lê o CSV gerado pelo Arduino
df = pd.read_csv('dados_colisao.csv')

# Engenharia de Atributos (O Pulo do Gato)
# Para prever o futuro, a IA precisa saber o "agora" e o "passado" (para calcular velocidade)
# Input (X): Distância no tempo T e Distância no tempo T-1
# Output (Y): Distância no tempo T+1 (Futuro)

df['Distancia_Passada'] = df['Distancia'].shift(1) # Cria coluna com valor anterior
df['Target_Futuro'] = df['Distancia'].shift(-1)    # Cria coluna com valor futuro (o que queremos prever)

# Remove linhas vazias geradas pelo shift
df = df.dropna()

# Separa X (Entradas) e y (Saída)
X = df[['Distancia', 'Distancia_Passada']].values
y = df['Target_Futuro'].values

# --- 2. NORMALIZAÇÃO (Obrigatório no projeto) ---
print("Normalizando dados...")
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_norm = scaler_X.fit_transform(X)
y_norm = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

# Separa em Treino (70%) e Teste (30%)
X_train, X_test, y_train, y_test = train_test_split(X_norm, y_norm, test_size=0.3, random_state=42, shuffle=False)

# --- 3. CRIAÇÃO E TREINAMENTO DA MLP ---
print("Treinando Rede Neural...")
# Arquitetura: 2 camadas ocultas com 10 neurônios cada
# Ativação ReLU (padrão para regressão) e Solver Adam
mlp = MLPRegressor(hidden_layer_sizes=(10, 10), 
                   activation='relu', 
                   solver='adam', 
                   max_iter=2000, 
                   random_state=42)

mlp.fit(X_train, y_train)

# --- 4. AVALIAÇÃO E GRÁFICOS ---
print("Gerando previsões...")
previsoes_norm = mlp.predict(X_test)

# Desfaz a normalização para vermos os números em cm reais
previsoes_reais = scaler_y.inverse_transform(previsoes_norm.reshape(-1, 1))
y_test_reais = scaler_y.inverse_transform(y_test.reshape(-1, 1))

# Cálculo do Erro (para colocar no artigo)
mse = mean_squared_error(y_test_reais, previsoes_reais)
r2 = r2_score(y_test_reais, previsoes_reais)
print(f"\n--- RESULTADOS ---")
print(f"Erro Médio Quadrático (MSE): {mse:.2f}")
print(f"R2 Score (Precisão): {r2:.2f}")

# Gráfico 1: Real vs Previsto (O que o professor pediu)
plt.figure(figsize=(10, 6))
plt.plot(y_test_reais, label='Real (Sensor)', color='blue', linewidth=2)
plt.plot(previsoes_reais, label='Previsto pela IA', color='orange', linestyle='--', linewidth=2)
plt.title('Sistema de Frenagem: Distância Real vs Prevista pela MLP')
plt.xlabel('Amostras de Teste')
plt.ylabel('Distância (cm)')
plt.legend()
plt.grid(True)
plt.savefig('grafico_resultado.png') # Salva a imagem para o artigo
plt.show()

# Gráfico 2: Curva de Perda (Mostra que a rede aprendeu)
plt.figure(figsize=(6, 4))
plt.plot(mlp.loss_curve_)
plt.title('Curva de Aprendizado (Loss)')
plt.xlabel('Iterações')
plt.ylabel('Erro')
plt.grid(True)
plt.show()