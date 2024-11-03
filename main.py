# Import the run_bot function from the bot module
from bot import run_bot
from bot.utils.database import db

# Check if this script is being run directly (not imported)
if __name__ == "__main__":
    # Initialize database with default authorized user
    db.add_authorized_user("6025856")  # Add your default admin user ID here
    # Run the bot
    run_bot()
