import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 1. CARREGAR DADOS
print("Carregando dataset...")
df = pd.read_csv('dados_colisao.csv')

# Engenharia de Atributos (Janela de Tempo)
# X = Distância Atual + Distância Anterior (Velocidade implícita)
# Y = Distância Futura (Previsão)
df['Dist_Anterior'] = df['Distancia'].shift(1)
df['Target_Futuro'] = df['Distancia'].shift(-1)
df = df.dropna()

X = df[['Distancia', 'Dist_Anterior']].values
y = df['Target_Futuro'].values

# 2. NORMALIZAÇÃO (Requisito Obrigatório do Projeto)
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_norm = scaler_X.fit_transform(X)
y_norm = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

# Separação Treino/Teste (Não misturar dados)
X_train, X_test, y_train, y_test = train_test_split(X_norm, y_norm, test_size=0.3, shuffle=False)

# 3. REDE NEURAL (MLP)
print("Treinando MLP...")
mlp = MLPRegressor(hidden_layer_sizes=(10, 10), # 2 Camadas Ocultas
                   activation='relu',           # Função de Ativação
                   solver='adam',               # Otimizador
                   max_iter=1000, 
                   random_state=42)

mlp.fit(X_train, y_train)

# 4. AVALIAÇÃO
previsoes_norm = mlp.predict(X_test)
# Desnormalizar para ver em cm
previsoes_reais = scaler_y.inverse_transform(previsoes_norm.reshape(-1, 1))
y_test_reais = scaler_y.inverse_transform(y_test.reshape(-1, 1))

mse = mean_squared_error(y_test_reais, previsoes_reais)
r2 = r2_score(y_test_reais, previsoes_reais)

print(f"MSE (Erro): {mse:.2f}")
print(f"R2 (Precisão): {r2:.2f}")



# Gráfico 1: Real vs Previsto 
plt.figure(figsize=(12, 6))
plt.plot(y_test_reais, label='Real (Sensor)', color='blue', linewidth=2)
plt.plot(previsoes_reais, label='Previsto (IA)', color='orange', linestyle='--', linewidth=2)
plt.title(f'Resultado da IA: Previsão de Frenagem (R² = {r2:.2f})')
plt.xlabel('Amostras de Teste')
plt.ylabel('Distância (cm)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('grafico_resultado.png', dpi=300) # Salva em alta qualidade
plt.show()

# Gráfico 2: Curva de Perda
plt.figure(figsize=(8, 4))
plt.plot(mlp.loss_curve_, color='green')
plt.title('Curva de Aprendizado (Loss Function)')
plt.xlabel('Épocas (Iterações)')
plt.ylabel('Erro (Loss)')
plt.grid(True)
plt.savefig('grafico_loss.png', dpi=300)
plt.show()