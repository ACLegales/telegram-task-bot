import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters
import re
from typing import List

# Palabras clave BILINGUES simples
TASK_KEYWORDS = [
    # Español
    "tarea:", "hacer:", "pendiente:", "urgente:", "importante:",
    "hay que", "debo", "necesito", "falta", "revisar",
    "contactar", "llamar", "enviar", "preparar",
    # English
    "task:", "todo:", "urgent:", "important:", "need:",
    "must:", "contact", "call", "send", "review",
    "deadline", "reminder", "follow up"
]

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            chat_name TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Base de datos lista / Database ready")

# Guardar tarea
def save_task(chat_id: int, chat_name: str, message: str):
    try:
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('INSERT INTO tasks (chat_id, chat_name, message) VALUES (?, ?, ?)',
                  (chat_id, chat_name, message))
        conn.commit()
        conn.close()
        print(f"[SAVED] Tarea guardada: {message[:50]}")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar: {e}")

# Extraer tareas
def extract_tasks(text: str) -> List[str]:
    tasks = []
    if not text:
        return tasks

    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue

        # Buscar palabra clave
        has_keyword = any(kw in line_lower for kw in TASK_KEYWORDS)

        if has_keyword:
            task = line.strip()
            task = re.sub(r'^[•\-\*\[\]\(\)@]+\s*', '', task)
            task = re.sub(r'\s+', ' ', task).strip()

            if len(task) > 3:
                tasks.append(task)
                print(f"[DETECT] Tarea detectada: {task[:50]}")

    return tasks

# Handler de mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.text:
            chat_id = update.message.chat_id
            chat_name = update.message.chat.title or update.message.chat.first_name or "Chat"
            text = update.message.text

            print(f"[MSG] De {chat_name}: {text[:50]}")

            tasks = extract_tasks(text)
            if tasks:
                for task in tasks:
                    save_task(chat_id, chat_name, task)
    except Exception as e:
        print(f"[ERROR] En handle_message: {e}")

# Comando: resumen
async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()

        time_threshold = datetime.now() - timedelta(hours=24)
        c.execute('''
            SELECT chat_name, message, created_at FROM tasks
            WHERE chat_id = ? AND created_at > ?
            ORDER BY created_at DESC
        ''', (chat_id, time_threshold))

        rows = c.fetchall()
        conn.close()

        if not rows:
            await update.message.reply_text("Sin tareas pendientes (ultimas 24h)")
            return

        summary = "TAREAS PENDIENTES (ultimas 24h)\n"
        summary += "=" * 50 + "\n\n"

        tasks_by_chat = {}
        for chat_name, message, created_at in rows:
            if chat_name not in tasks_by_chat:
                tasks_by_chat[chat_name] = []
            tasks_by_chat[chat_name].append({
                'message': message,
                'time': datetime.fromisoformat(created_at)
            })

        for chat_name, tasks in sorted(tasks_by_chat.items()):
            summary += f"[{chat_name}]\n"
            for task in tasks:
                time_str = task['time'].strftime('%H:%M')
                summary += f"  - {task['message']}\n    ({time_str})\n"
            summary += "\n"

        await update.message.reply_text(summary)
    except Exception as e:
        print(f"[ERROR] En cmd_resumen: {e}")
        await update.message.reply_text(f"Error: {e}")

# Comando: resumen global
async def cmd_resumen_global(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()

        time_threshold = datetime.now() - timedelta(hours=24)
        c.execute('''
            SELECT chat_name, message, created_at FROM tasks
            WHERE created_at > ?
            ORDER BY chat_name, created_at DESC
        ''', (time_threshold,))

        rows = c.fetchall()
        conn.close()

        if not rows:
            await update.message.reply_text("Sin tareas pendientes (ultimas 24h)")
            return

        summary = "TODAS LAS TAREAS (ultimas 24h)\n"
        summary += "=" * 50 + "\n\n"

        tasks_by_chat = {}
        for chat_name, message, created_at in rows:
            if chat_name not in tasks_by_chat:
                tasks_by_chat[chat_name] = []
            tasks_by_chat[chat_name].append({
                'message': message,
                'time': datetime.fromisoformat(created_at)
            })

        for chat_name, tasks in sorted(tasks_by_chat.items()):
            summary += f"[{chat_name}]\n"
            for task in tasks:
                time_str = task['time'].strftime('%H:%M')
                summary += f"  - {task['message']}\n    ({time_str})\n"
            summary += "\n"

        await update.message.reply_text(summary)
    except Exception as e:
        print(f"[ERROR] En cmd_resumen_global: {e}")
        await update.message.reply_text(f"Error: {e}")

# Comando: limpiar
async def cmd_limpiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE chat_id = ?', (chat_id,))
        conn.commit()
        conn.close()
        await update.message.reply_text("[LIMPIAR] Tareas del chat eliminadas")
    except Exception as e:
        print(f"[ERROR] En cmd_limpiar: {e}")
        await update.message.reply_text(f"Error: {e}")

# Comando: help
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
BOT DE TAREAS - COMANDOS

/resumen - Tareas de este chat (ultimas 24h)
/resumen_global - Todas las tareas
/limpiar - Eliminar tareas de este chat
/help - Este mensaje

DETECTA AUTOMATICAMENTE:
- tarea:, hacer:, pendiente:, urgente:, importante:
- task:, todo:, urgent:, important:, need:
- contact, call, send, review, deadline, etc.

Solo escribe naturalmente!
"""
    await update.message.reply_text(help_text)

# Main
def main():
    init_db()

    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        print("[ERROR] Define TELEGRAM_BOT_TOKEN")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("resumen", cmd_resumen))
    app.add_handler(CommandHandler("resumen_global", cmd_resumen_global))
    app.add_handler(CommandHandler("limpiar", cmd_limpiar))
    app.add_handler(CommandHandler("help", cmd_help))

    print("[INICIADO] Bot de tareas bilingue - Español + English")
    print("[OK] Listening for messages...")

    app.run_polling()

if __name__ == '__main__':
    main()
