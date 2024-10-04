import logging
from telegram import Update

def log_command(update: Update, command: str):
    user = update.effective_user
    user_info = (
        f"ID: {user.id}, "
        f"Nickname: @{user.username or 'N/A'}, "
        f"First Name: {user.first_name or 'N/A'}, "
        f"Last Name: {user.last_name or 'N/A'}"
    )
    logging.info(f"Comando /{command} recibido de usuario {user_info}")