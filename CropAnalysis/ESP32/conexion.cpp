#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // Instalar desde el gestor de librerías
#include "esp_camera.h"  // Librería nativa para la cámara del ESP32

// 1. Configuración de Red
const char* ssid = "TU_WIFI_SSID";
const char* password = "TU_WIFI_PASSWORD";

// 2. IP y Puerto de tu servidor Python (FastAPI)
const char* serverName = "tuIP"; 
const int serverPort = 8000;
const char* serverPath = "/api/analyze";

void setup() {
  Serial.begin(115200);
  
  // Conexión a WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a la red WiFi");

  // NOTA: Aquí debes incluir tu función de inicialización de la cámara (esp_camera_init)
  // configCamera(); 
}

void loop() {
  // Ejecutar el ciclo de monitoreo cada cierto tiempo (ej. cada hora = 3600000 ms)
  // Para pruebas, lo haremos cada 30 segundos
  Serial.println("\n--- Iniciando ciclo de monitoreo ---");
  capturarYAnalizar();
  delay(30000); 
}

void capturarYAnalizar() {
  // 1. Tomar la foto
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Error: No se pudo capturar la imagen");
    return;
  }
  Serial.printf("Foto capturada! Tamaño: %u bytes\n", fb->len);

  // 2. Conectar al servidor FastAPI por TCP nativo para enviar el multipart a mano
  WiFiClient client;
  if (!client.connect(serverName, serverPort)) {
    Serial.println("Error: Conexión al servidor Python fallida");
    esp_camera_fb_return(fb); // Liberar memoria siempre!
    return;
  }

  // 3. Construir el paquete Multipart
  String boundary = "----GrotixBoundary123456789";
  
  // Cabecera inicial del multipart
  String head = "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"file\"; filename=\"captura_esp32.jpg\"\r\n";
  head += "Content-Type: image/jpeg\r\n\r\n";
  
  // Cierre del multipart
  String tail = "\r\n--" + boundary + "--\r\n";

  // Calcular la longitud total del payload (Head + Bytes de Imagen + Tail)
  uint32_t contentLength = head.length() + fb->len + tail.length();

  // 4. Enviar los Headers HTTP
  client.println("POST " + String(serverPath) + " HTTP/1.1");
  client.println("Host: " + String(serverName));
  client.println("Content-Length: " + String(contentLength));
  client.println("Content-Type: multipart/form-data; boundary=" + boundary);
  client.println(); // Línea en blanco obligatoria que separa headers del body

  // 5. Enviar el Body en tres partes (Head -> Imagen -> Tail)
  client.print(head);
  
  // Enviar los bytes puros de la cámara directamente desde el buffer
  uint8_t *fbBuf = fb->buf;
  size_t fbLen = fb->len;
  for (size_t n = 0; n < fbLen; n += 1024) {
    if (n + 1024 < fbLen) {
      client.write(fbBuf, 1024);
      fbBuf += 1024;
    } else {
      client.write(fbBuf, fbLen % 1024);
    }
  }
  
  client.print(tail);

  // Ya enviamos la foto, podemos liberar la RAM de la cámara
  esp_camera_fb_return(fb); 
  Serial.println("Imagen enviada a Gemini. Esperando diagnóstico...");

  // 6. Leer la respuesta de Python
  long startTimer = millis();
  boolean state = false;
  String jsonResponse = "";
  
  while ((startTimer + 15000) > millis()) { // Esperar hasta 15 segundos
    while (client.available()) {
      char c = client.read();
      if (c == '{') state = true; // Empezar a guardar cuando veamos el inicio del JSON
      if (state) jsonResponse += c;
    }
    if (jsonResponse.length() > 0) break;
  }
  
  client.stop();

  if (jsonResponse.length() > 0) {
    Serial.println("Respuesta recibida:");
    Serial.println(jsonResponse);
    procesarDiagnostico(jsonResponse);
  } else {
    Serial.println("Error: Timeout esperando la respuesta del servidor");
  }
}

void procesarDiagnostico(String json) {
  // 7. Parsear el JSON para extraer los datos
  // Asignamos memoria para el documento JSON (300 bytes es suficiente para esto)
  StaticJsonDocument<300> doc;
  DeserializationError error = deserializeJson(doc, json);

  if (error) {
    Serial.print("Error leyendo JSON: ");
    Serial.println(error.c_str());
    return;
  }

  // Extraer las variables exactas que devuelve nuestro Python
  const char* estado = doc["estado_germinacion"];
  int score = doc["health_score"];
  const char* observaciones = doc["observaciones"];

  Serial.println("\n--- ANÁLISIS DE HARDWARE ---");
  Serial.printf("Estado: %s\n", estado);
  Serial.printf("Health Score: %d\n", score);
  
  // 8. Lógica de Control (Telemetría / Actuadores)
  if (score < 40 && String(estado) != "unknown") {
    Serial.println("¡ALERTA CRÍTICA! Activando bomba de agua y enviando alerta al broker...");
    
    // digitalWrite(PIN_BOMBA, HIGH);
    // enviarTelemetriaRabbitMQ("ALERTA", observaciones);
  } else {
    Serial.println("Cultivo estable. Ninguna acción requerida.");
  }
}