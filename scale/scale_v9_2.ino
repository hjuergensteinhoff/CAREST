//
// Hand contact force tool for cold/heat plate
// Heinz-Juergen Steinhoff 19.11.2024
// with M5Stack basic (Board: M5Core)
//
#include "HX711.h"
#include <M5Stack.h>
// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 36; // not working with 22
const int LOADCELL_SCK_PIN = 26; // not working with 21
char inword = '1';
float force = 0;
bool screenGreen = 1;
HX711 scale;
//
void setup() {
  M5.begin(true, false, false, false);        // Init LCD of M5Core
  Serial.begin(19200);
  // Initializing the scale;
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);            
  //scale.set_scale(INSERT YOUR CALIBRATION FACTOR);
  scale.set_scale(2641);
  scale.tare();               // reset the scale to 0
  //
  M5.Power.begin();  // Init Power module
  M5.Lcd.fillScreen(GREEN);
  M5.Lcd.setCursor(50, 30);  // Move the cursor position to (x,y)
  M5.Lcd.setTextColor(BLACK);  // Set the font color to white
  M5.Lcd.setTextSize(2);  // Set the font size
  M5.Lcd.printf("Hand contact force");
  M5.Lcd.fillCircle(300, 220, 10, BLUE);
}
//
void loop() {
  force = scale.get_units(5);
  if (Serial.available()) {
    inword = Serial.read();
    M5.Lcd.fillCircle(300, 220, 10, YELLOW);
    delay(50);
    if (inword == '0') {
      scale.tare();
      delay(50);
      }
      else {
      Serial.println(force, 1);
    }
  }
  if ((force < 1.0 && screenGreen == 0) || (force >= 1.0 && screenGreen == 1)) {
    M5.Lcd.fillScreen(force < 1.0 ? GREEN : RED);
    screenGreen = force < 1.0 ? 1 : 0;
  }
  M5.Lcd.setCursor(50, 30);
  M5.Lcd.setTextSize(2);
  M5.Lcd.printf("Hand contact force");
  M5.Lcd.setTextSize(4);
  if (screenGreen == 0) {
    M5.Lcd.fillRect(100, 110, 180, 35, RED);
  }
  else {
    M5.Lcd.fillRect(100, 110, 180, 35, GREEN);
  }
  M5.Lcd.setCursor(100, 110);
  M5.Lcd.printf(" %4.1f", force);
	M5.Lcd.setCursor(50, 180);
  M5.Lcd.setTextSize(2);
  M5.Lcd.printf("Newton");
  M5.Lcd.fillCircle(300, 220, 10, BLUE);  
  delay(50);
}
