# Bot de Tareas en Telegram - Setup

## 1️⃣ Crear el Bot en Telegram

1. Abre **BotFather** en Telegram: `@BotFather`
2. Envía: `/newbot`
3. Elige un nombre (ej: "Mi Bot de Tareas")
4. Elige un username único (ej: `mi_bot_tareas_bot`)
5. **Copia el TOKEN** que te da (será algo como: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## 2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

## 3️⃣ Configurar el token

**Opción A: Variable de entorno (recomendado)**
```bash
export TELEGRAM_BOT_TOKEN="tu_token_aqui"
python telegram_task_bot.py
```

**Opción B: En Windows**
```cmd
set TELEGRAM_BOT_TOKEN=tu_token_aqui
python telegram_task_bot.py
```

## 4️⃣ Agregar el bot a tus grupos

1. Ve a un grupo de Telegram donde quieras monitorear tareas
2. Busca tu bot (`@mi_bot_tareas_bot`)
3. Agrega como miembro

## 5️⃣ Usar el bot

### Comandos disponibles:

```
/resumen         - Resumen de tareas de este chat (últimas 24h)
/resumen_global  - Resumen de todos los grupos monitoreados
/limpiar         - Eliminar todas las tareas de este chat
/help            - Ver la ayuda
```

### Cómo detecta tareas:

El bot busca automáticamente palabras clave en los mensajes:
- `tarea:`, `hacer:`, `pendiente:`, `todo:`, `acción:`
- `necesito:`, `hay que`, `debo`, `tengo que`
- `urgente:`, `importante:`, `revisar`, `verificar`, etc.

**Ejemplo en un chat:**
```
"Mañana hay que revisar el proyecto de energía solar"
→ Se extrae: "Mañana hay que revisar el proyecto de energía solar"

"tarea: actualizar presupuesto de ENERCO
  con los datos de septiembre"
→ Se extrae: "tarea: actualizar presupuesto de ENERCO con los datos de septiembre"
```

## 6️⃣ Desplegar en producción

### Opción 1: Railway (gratuito y fácil)

1. Ve a [railway.app](https://railway.app)
2. Crea una cuenta con GitHub
3. Nuevo proyecto → GitHub repo
4. Conecta tu repo con el bot
5. Agrega variable de entorno: `TELEGRAM_BOT_TOKEN`
6. Deploy automático ✅

### Opción 2: Render (gratuito)

1. Ve a [render.com](https://render.com)
2. Nuevo servicio web
3. Conecta tu repo
4. Build: `pip install -r requirements.txt`
5. Start: `python telegram_task_bot.py`
6. Agrega env variable

### Opción 3: VPS propio (DigitalOcean, Linode, etc.)

```bash
# En tu servidor:
git clone tu_repo
cd tu_proyecto
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="tu_token"

# Opción A: Ejecutar en background
nohup python telegram_task_bot.py &

# Opción B: Usar systemd (permanente)
sudo nano /etc/systemd/system/telegram-bot.service
```

**Contenido del archivo systemd:**
```ini
[Unit]
Description=Telegram Task Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-bot
Environment="TELEGRAM_BOT_TOKEN=tu_token_aqui"
ExecStart=/home/ubuntu/telegram-bot/venv/bin/python telegram_task_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## 7️⃣ Próximas mejoras (opcional)

- Agregar categorías a las tareas
- Resumen por horario programado (cada mañana a las 8am)
- Marcar tareas como completadas
- Exportar a Google Sheets o Notion
- Prioridades (🔴 urgente, 🟡 normal, 🟢 baja)

## 🔍 Debug

Si el bot no funciona:

```bash
# Ver logs (en terminal)
python telegram_task_bot.py

# Prueba el token manualmente
curl https://api.telegram.org/bot[TU_TOKEN]/getMe
```

---

¿Preguntas? Adapta el código según tus necesidades específicas de ENERCO o crypto operations. 🚀
