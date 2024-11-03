from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from bot.utils.database import db

def check_auth():
    # Decorator function to check if a user is authorized to use the bot
    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
            # Check if the user's ID is in the database of authorized users
            if str(update.effective_user.id) not in db.get_authorized_users():
                # If not authorized, send a message to the user
                await update.message.reply_text(
                    "Lo siento, no estás autorizado para usar este bot."
                )
                return
            # If authorized, call the original function
            return await func(update, context, *args, **kwargs)
        return wrapped
    return decorator
