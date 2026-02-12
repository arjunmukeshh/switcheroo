#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <ESPmDNS.h>
#include "config.h"


Servo switchServo;
WebServer server(80);

void pressSwitch(bool turnOn) {
  int targetAngle;
  if (turnOn) {
    targetAngle = SERVO_NEUTRAL_ANGLE + SERVO_PRESS_AMPLITUDE_ON;
  } else {
    targetAngle = SERVO_NEUTRAL_ANGLE - SERVO_PRESS_AMPLITUDE_OFF;
  }

  // 1. Move to target angle (Press)
  Serial.printf("Moving to %d degrees (Pressing)...\n", targetAngle);
  switchServo.write(targetAngle);
  delay(PRESS_DELAY_MS);

  // 2. Return to neutral (Release)
  Serial.printf("Returning to %d degrees (Neutral)...\n", SERVO_NEUTRAL_ANGLE);
  switchServo.write(SERVO_NEUTRAL_ANGLE);
}

void handleToggle() {
  if (!server.hasArg("state")) {
    server.send(400, "text/plain", "Missing 'state'");
    return;
  }
  String state = server.arg("state");
  
  if (state == "on") {
    pressSwitch(true); // Turn ON
    server.send(200, "application/json", "{\"status\":\"ok\",\"state\":\"on\",\"message\":\"Switched ON\"}");
  } else if (state == "off") {
    pressSwitch(false); // Turn OFF
    server.send(200, "application/json", "{\"status\":\"ok\",\"state\":\"off\",\"message\":\"Switched OFF\"}");
  } else {
    server.send(400, "text/plain", "Invalid state. Use 'on' or 'off'.");
  }
}

void handleRoot() {
  server.send(200, "text/html", "<h1>Servo Switch Controller</h1><p><a href='/toggle?state=on'>TURN ON</a> | <a href='/toggle?state=off'>TURN OFF</a></p>");
}

void setup() {
  Serial.begin(115200);
  
  // Setup Servo
  switchServo.attach(SERVO_PIN);
  switchServo.write(SERVO_NEUTRAL_ANGLE); // Start at Neutral
  
  // Setup WiFi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  if (!MDNS.begin("switcheroo")) {
    Serial.println("Error setting up MDNS responder!");
  } else {
    Serial.println("mDNS responder started: switcheroo.local");
    // Add service to mDNS-SD
    MDNS.addService("http", "tcp", 80);
  }

  // Setup Server
  server.on("/", handleRoot);
  server.on("/toggle", handleToggle);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
