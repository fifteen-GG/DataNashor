#include <Esplora.h>
#include <Keyboard.h>
char cmd;

void setup() {
  Keyboard.begin();
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()){
    cmd = Serial.read(); 

    if(cmd=='a'){
      Serial.println("8배 시작");
      Esplora.writeRed(100);
      for(int i = 0; i < 8; i++) {
        Keyboard.press('=');
        delay(100);
        Keyboard.release('=');
      }
      Keyboard.press('O');
      delay(100);
      Keyboard.release('O');
      Esplora.writeRed(0);
    }
  }
}