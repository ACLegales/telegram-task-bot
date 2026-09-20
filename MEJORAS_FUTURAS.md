# Mejoras Futuras para el Bot

## 1. Resumen automático programado

Recibe un resumen a una hora específica cada día:

```python
from telegram.ext import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Agregar al main()
scheduler = AsyncIOScheduler()
scheduler.add_job(
    send_daily_summary,
    "cron",
    hour=8,      # 8 AM
    minute=0,
    args=[app.bot, CHAT_ID_TUYO]
)
scheduler.start()

async def send_daily_summary(bot, chat_id):
    summary = get_pending_tasks(hours=24)
    await bot.send_message(chat_id=chat_id, text=summary, parse_mode='Markdown')
```

## 2. Prioridades y emojis

```python
PRIORITY_KEYWORDS = {
    "urgente": "🔴",
    "importante": "🟠",
    "normal": "🟡",
    "baja": "🟢"
}

# En extract_tasks():
def get_priority(text):
    for key, emoji in PRIORITY_KEYWORDS.items():
        if key in text.lower():
            return emoji
    return "⚪"

# En get_pending_tasks():
priority = get_priority(task['message'])
summary += f"  {priority} {task['message']}\n"
```

## 3. Asignar tareas a personas

```python
# Detectar @usuario en Telegram
import re

def extract_assignee(text):
    matches = re.findall(r'@(\w+)', text)
    return matches[0] if matches else None

# En save_task():
assignee = extract_assignee(message)
c.execute('''
    INSERT INTO tasks (chat_id, chat_name, message, assigned_to)
    VALUES (?, ?, ?, ?)
''', (chat_id, chat_name, message, assignee))
```

## 4. Marcar tareas completadas

```python
async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /done 5  (marca la tarea 5 como completada)
    if not context.args:
        await update.message.reply_text("Uso: /done [ID]")
        return
    
    task_id = context.args[0]
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET processed=1 WHERE id=?', (task_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Tarea {task_id} marcada completada")

# Agregar al main():
app.add_handler(CommandHandler("done", cmd_done))
```

## 5. Exportar a Google Sheets

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def export_to_sheets(spreadsheet_id):
    creds = Credentials.from_service_account_file('credentials.json')
    service = build('sheets', 'v4', credentials=creds)
    
    tasks = get_tasks_from_db()
    values = [['Chat', 'Tarea', 'Fecha', 'Prioridad']]
    values.extend(tasks)
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='A1',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()
```

## 6. Integración con Notion

```python
import requests

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('NOTION_DB_ID')

def save_to_notion(task_text, chat_name):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Tarea": {"title": [{"text": {"content": task_text}}]},
            "Chat": {"select": {"name": chat_name}},
            "Estado": {"select": {"name": "Pendiente"}}
        }
    }
    
    requests.post(
        "https://api.notion.com/v1/pages",
        json=payload,
        headers=headers
    )
```

## 7. Análisis de productividad

```python
def analytics_report():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    
    # Tareas por chat
    c.execute('''
        SELECT chat_name, COUNT(*) as count
        FROM tasks
        WHERE created_at > datetime('now', '-7 days')
        GROUP BY chat_name
        ORDER BY count DESC
    ''')
    
    stats = "📊 **PRODUCTIVIDAD (últimos 7 días)**\n\n"
    for chat, count in c.fetchall():
        stats += f"{chat}: {count} tareas\n"
    
    conn.close()
    return stats
```

## 8. Integración con Telegram Web App

Crear un pequeño dashboard para ver/gestionar tareas desde web:

```python
from flask import Flask, jsonify
from telegram.ext import Application

app_flask = Flask(__name__)

@app_flask.route('/api/tasks/<chat_id>')
def get_chat_tasks(chat_id):
    tasks = get_pending_tasks(chat_id=int(chat_id))
    return jsonify({"tasks": tasks})
```

## 9. Detectar patrones y contexto mejorado

```python
# Usar spaCy para NLP más sofisticado
import spacy

nlp = spacy.load('es_core_news_sm')

def extract_tasks_nlp(text):
    doc = nlp(text)
    tasks = []
    
    # Detectar verbos de acción
    action_verbs = ['hacer', 'revisar', 'verificar', 'completar', 'preparar']
    
    for token in doc:
        if token.lemma_ in action_verbs:
            # Extraer la oración completa
            start = token.sent.start_char
            end = token.sent.end_char
            tasks.append(text[start:end])
    
    return tasks
```

## 10. Filtros personalizados

```python
async def cmd_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /filter urgente  → solo muestra tareas urgentes
    if not context.args:
        await update.message.reply_text("Uso: /filter [palabra_clave]")
        return
    
    keyword = context.args[0].lower()
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute(
        'SELECT * FROM tasks WHERE LOWER(message) LIKE ?',
        (f'%{keyword}%',)
    )
    # Procesar y mostrar...
```

---

## Recomendación para ENERCO/Crypto:

Para tus operaciones con Oscar en la consultoría de crypto:
1. **Prioridades** (urgentes: DASP filings)
2. **Asignación** a personas (@oscar, @javi)
3. **Exportar a Sheets** para seguimiento financiero
4. **Resumen diario** a las 7 AM

¿Cuál implementar primero?
