#include <DHT.h>
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
// WiFi credentials and Blynk auth token
char auth[] = "Your_Blynk_Auth_Token";
char ssid[] = "Your_WiFi_SSID";
char pass[] = "Your_WiFi_Password";
// Pin assignments
#define DHTPIN 2 // DHT22 sensor
#define PIR1_PIN 3 // PIR sensor 1
#define PIR2_PIN 4 // PIR sensor 2
#define FLAME_SENSOR_PIN 5 // Flame sensor
#define MOISTURE_SENSOR_PIN A0 // Soil moisture sensor
#define BUZZER_PIN 6 // Buzzer
#define LED_PIN 7 // LED for PIR1
#define TEMP_LED_PIN 8 // LED for temperature
#define WATER_PUMP_PIN 9 // Water pump
DHT dht(DHTPIN, DHT22);
LiquidCrystal_I2C lcd(0x27, 16, 2); // Set the LCD I2C address
// Variables for sensor readings
float humidity;
float temperature;

int soilMoisture;
bool isPIR1Enabled = true;
// Blynk virtual pins
#define VIRTUAL_PIN_PIR1 V1
#define VIRTUAL_PIN_TEMP V2
#define VIRTUAL_PIN_HUMIDITY V3
#define VIRTUAL_PIN_SOIL_MOISTURE V4
#define VIRTUAL_PIN_PUMP V5
BlynkTimer timer;
void setup() {
Serial.begin(9600);
dht.begin();
lcd.init();
lcd.backlight();
pinMode(PIR1_PIN, INPUT);
pinMode(PIR2_PIN, INPUT);
pinMode(FLAME_SENSOR_PIN, INPUT);
pinMode(BUZZER_PIN, OUTPUT);
pinMode(LED_PIN, OUTPUT);
pinMode(TEMP_LED_PIN, OUTPUT);
pinMode(WATER_PUMP_PIN, OUTPUT);
WiFi.begin(ssid, pass);
Blynk.begin(auth, ssid, pass);
// Setup a function to be called every second
timer.setInterval(1000L, sendSensorData);
Blynk.virtualWrite(VIRTUAL_PIN_PUMP, LOW); // Initial state of the pump

}
void sendSensorData() {
humidity = dht.readHumidity();
temperature = dht.readTemperature();
soilMoisture = analogRead(MOISTURE_SENSOR_PIN);
// Display on I2C LCD
lcd.clear();
lcd.print("Temp: ");
lcd.print(temperature);
lcd.print("C");
lcd.setCursor(0, 1);
lcd.print("Humidity: ");
lcd.print(humidity);
lcd.print("%");
// Send to Blynk
Blynk.virtualWrite(VIRTUAL_PIN_TEMP, temperature);
Blynk.virtualWrite(VIRTUAL_PIN_HUMIDITY, humidity);
Blynk.virtualWrite(VIRTUAL_PIN_SOIL_MOISTURE, soilMoisture);
// Check for temperature
if (temperature < 20) {
digitalWrite(TEMP_LED_PIN, HIGH);
} else {
digitalWrite(TEMP_LED_PIN, LOW);
}
// Check soil moisture and control water pump
if (soilMoisture < thresholdMoisture) { // Define thresholdMoisture as per your requirement

digitalWrite(WATER_PUMP_PIN, HIGH);
} else {
digitalWrite(WATER_PUMP_PIN, LOW);
}
}
void loop() {
Blynk.run();
timer.run();
// PIR1 functionality
if (isPIR1Enabled && digitalRead(PIR1_PIN) == HIGH) {
digitalWrite(LED_PIN, HIGH);
digitalWrite(BUZZER_PIN, HIGH);
Blynk.notify("Motion detected by PIR1!");
delay(1000);
digitalWrite(LED_PIN, LOW);
digitalWrite(BUZZER_PIN, LOW);
}
// PIR2 functionality
if (digitalRead(PIR2_PIN) == HIGH) {
digitalWrite(LED_PIN, HIGH);
delay(10000);
digitalWrite(LED_PIN, LOW);
}
// Flame sensor functionality
if (digitalRead(FLAME_SENSOR_PIN) == HIGH) {
digitalWrite(BUZZER_PIN, HIGH);
Blynk.notify("Fire detected!");

while (temperature > normalTemperature) { // Define normalTemperature as per your requirement
delay(1000);
}
digitalWrite(BUZZER_PIN, LOW);
}
}
// Handling Blynk app button press for PIR1
BLYNK_WRITE(VIRTUAL_PIN_PIR1) {
isPIR1Enabled = param.asInt();
}
// Handling Blynk app button press for water pump
BLYNK_WRITE(VIRTUAL_PIN_PUMP) {
if (param.asInt()) {
digitalWrite(WATER_PUMP_PIN, HIGH);
} else {
digitalWrite(WATER_PUMP_PIN, LOW);
}
}
