#include <Arduino_RouterBridge.h>

constexpr unsigned long CH9328_BAUD = 9600;
constexpr unsigned long KEY_DELAY_MS = 20;

void type_text(String text) {
  for (size_t index = 0; index < text.length(); ++index) {
    Serial1.write(text[index]);
    delay(KEY_DELAY_MS);
  }
}

void setup() {
  Serial1.begin(CH9328_BAUD);
  Bridge.begin();
  Bridge.provide_safe("type_text", type_text);
}

void loop() {
}

