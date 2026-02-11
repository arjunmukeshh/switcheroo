#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Servo Configuration
const int SERVO_PIN = 14;              // GPIO Pin connected to servo signal
const int SERVO_NEUTRAL_ANGLE = 90;    // Neutral/Resting position
const int SERVO_PRESS_AMPLITUDE = 60;  // Degrees to move for press
const int PRESS_DELAY_MS = 500;        // Duration of press in milliseconds

#endif
