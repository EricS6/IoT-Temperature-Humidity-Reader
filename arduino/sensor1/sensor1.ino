#include <DHT.h>
#define DHTPIN 2      // Sensor data pin
#define DHTTYPE DHT11 // Sensor type
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature(true);
  float hum = dht.readHumidity();

  if(isnan(temp) || isnan(hum)) {
    Serial.println("Sensor error");
    delay(2000);
    return;
  }

  Serial.print("{\"temperature\": ");
  Serial.print(temp);
  Serial.print(", \"humidity\": ");
  Serial.print(hum);
  Serial.println("}");
  delay(2000); // Delay 2 seconds
}
