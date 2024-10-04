# Import the run_bot function from the bot module
from bot import run_bot

# Check if this script is being run directly (not imported)
if __name__ == "__main__":
    # If so, call the run_bot function to start the Telegram bot
    run_bot()
