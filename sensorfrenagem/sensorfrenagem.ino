
const int trigPin = 9;
const int echoPin = 10;


void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(ledFreio, OUTPUT);
  
  // Pisca 3 vezes para dizer que ligou
  for(int i=0; i<3; i++) {
    digitalWrite(ledFreio, HIGH); delay(100);
    digitalWrite(ledFreio, LOW); delay(100);
  }
}

void loop() {
  // 1. MEDIR DISTÂNCIA
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.034 / 2;

  // Filtro de ruído
  if (distance > 0 && distance < 400) {
    Serial.println(distance); // Envia para o Python
  }

  // 2. RECEBER ORDEM DA IA (Ouvir o Python)
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    if (comando == 'F') {
      digitalWrite(ledFreio, HIGH); // F = FREAR (Liga LED)
    } 
    else if (comando == 'L') {
      digitalWrite(ledFreio, LOW);  // L = LIBERADO (Desliga LED)
    }
  }

  delay(50); // Leitura rápida para o sistema ser ágil
}