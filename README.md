# 🚗 Protótipo de Frenagem Autônoma (AEB) com Arduino + MLP

O objetivo é **prever a próxima distância** medida por um sensor ultrassônico (HC-SR04) usando uma **Rede Neural MLP**, como base para um futuro sistema de **Frenagem Autônoma de Emergência (AEB)**.
---

## 🧠 Ideia do projeto
- O Arduino mede a distância (cm) com o **HC-SR04** e envia pela **Serial**.
- O Python **salva as leituras em CSV**.
- O Python prepara os dados com:
  - Entrada: distância atual *(t)* e distância anterior *(t-1)*
  - Saída: distância futura *(t+1)*
- Treinamos uma **MLP (10,10)** e avaliamos com **MSE** e **R²**.
- Geramos gráficos para o artigo e apresentação.

---

## 🧰 Materiais
- Arduino (ou compatível)
- Sensor ultrassônico **HC-SR04**
- Protoboard e jumpers
- PC para rodar os scripts em Python

---

## 🗂️ Estrutura sugerida do repositório
Você pode organizar assim (recomendado):

```
.
├─ arduino/
│  └─ firmware_hcsr04_serial.ino
├─ python/
│  ├─ coletar_dados.py
│  └─ treinar_mlp.py
├─ dados/
│  └─ dados_colisao.csv
├─ imagens/
│  ├─ fotoprotitpo.png
│  ├─ coleta.png
│  ├─ metricas.png
│  ├─ grafico_resultado.png
│  └─ grafico_loss.png
├─ artigo/
│  └─ main.tex
└─ README.md
```

> Se seus arquivos estiverem em outra pasta, tudo bem — só ajuste os caminhos nos scripts.

---

## ✅ Pré-requisitos (Python)
- Python 3.9+ (recomendado)
- Instalar bibliotecas:

```bash
pip install pandas numpy matplotlib scikit-learn pyserial
```

---

## 🔌 Configuração do Arduino (firmware)
1. Abra o Arduino IDE
2. Carregue o arquivo `.ino` do firmware
3. Selecione a placa e a porta COM correta
4. Faça upload

### Conexões (HC-SR04 → Arduino)
- VCC → 5V
- GND → GND
- TRIG → pino 9 *(pode alterar no código)*
- ECHO → pino 10 *(pode alterar no código)*

---

## 📈 Etapa 1 — Coleta de dados (CSV)
1. Conecte o Arduino ao computador
2. No arquivo `python/coletar_dados.py`, ajuste a porta:
   - Windows: `COM4`, `COM5`, etc.
   - Linux/macOS: `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.

3. Rode:

```bash
python python/coletar_dados.py
```

4. Durante a coleta, faça movimentos variados com a mão:
- aproximar rápido
- aproximar lento
- afastar
- parar por alguns instantes

5. Para parar, use `Ctrl + C`.

> O arquivo gerado é `dados_colisao.csv` (recomendado salvar em `dados/`).

---

## 🧪 Etapa 2 — Treinamento da MLP e geração dos gráficos
1. Garanta que o CSV existe e o caminho no código está correto.
2. Rode:

```bash
python python/treinar_mlp.py
```

3. Saídas esperadas:
- MSE e R² no terminal
- Imagens dos gráficos (por exemplo):
  - `grafico_resultado.png`
  - `grafico_loss.png`

> Se quiser salvar tudo dentro da pasta `imagens/`, ajuste o `plt.savefig()` para esse caminho.

---

## 📊 Como ler os gráficos (resumo)
- **Real vs Previsto**: mostra se a previsão acompanha o valor do sensor.
- **Loss**: mostra se o erro do treinamento diminuiu e estabilizou.
- **Métricas (MSE e R²)**:
  - **R²** perto de 1 = bom ajuste
  - **MSE** menor = menos erro médio

---



## 🧾 Referência teórica usada
FERREIRA, Jefferson Adiniz Borges. (2020). Trabalho disponível no repositório da UnB:  
https://repositorio.unb.br/bitstream/10482/41133/1/2020_JeffersonAdinizBorgesFerreira.pdf

---

## 🛠️ Problemas comuns
**1) “Arduino não encontrado”**
- Verifique se a porta COM está correta
- Feche o Monitor Serial do Arduino IDE (ele pode bloquear a porta)

**2) Valores com picos (ruído do sensor)**
- Pode ocorrer por posição/ângulo/reflexo do ultrassom
- Melhoria futura: média móvel, mediana de 3 leituras, remover outliers

**3) Erro ao instalar bibliotecas**
- Use: `python -m pip install ...`
- Confirme se está usando o Python correto

---

## 📄 Licença
Uso acadêmico/didático. (Você pode adicionar uma licença MIT se o professor permitir.)
