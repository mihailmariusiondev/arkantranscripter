# ArkanTranscripter Bot

![License](https://img.shields.io/github/license/mihailmariusiondev/arkantranscripter)
![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Project Status](https://img.shields.io/badge/status-active-brightgreen)

## Description

**ArkanTranscripter Bot** is a Telegram bot designed to transcribe YouTube videos, directly sent videos, and audio messages. It uses the YouTube Transcript API and OpenAI technology to provide accurate and enhanced transcriptions.

## Features

- **YouTube Video Transcription**: Transcribes YouTube videos from shared links.
- **Direct Video Transcription**: Transcribes videos sent directly to the Telegram chat.
- **Audio Message Transcription**: Transcribes audio and voice messages.
- **Enhanced Transcriptions**: Uses OpenAI's GPT-4o mini to improve transcription quality.
- **Automatic Transcription**: Option to enable/disable automatic transcription of links and videos.
- **Long Video Handling**: Splits long transcriptions into multiple messages for easier reading.
- **Authorized User Configuration**: Controls who can use the bot through an authorized users list.

## Available Commands

- `/start`: Start the bot and display a welcome message.
- `/transcribe [YouTube URL]`: Transcribe the specified YouTube video.
- `/toggle_autotranscription`: Enable or disable automatic transcription.
- `/toggle_enhanced_transcription`: Enable or disable enhanced transcription.

## Repository Structure

```
bot/
├── __init__.py
├── bot.py
├── handlers/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── error_handler.py
│   │   ├── message_handler.py
│   │   ├── start_handler.py
│   │   ├── toggle_autotranscription_handler.py
│   │   ├── toggle_enhanced_transcription_handler.py
│   │   └── transcribe_handler.py
│   └── media/
│       ├── __init__.py
│       ├── audio_handler.py
│       ├── video_handler.py
│       └── youtube_handler.py
└── utils/
    ├── __init__.py
    ├── auth_utils.py
    ├── config_utils.py
    ├── logging_utils.py
    └── transcription_utils.py
config/
├── __init__.py
├── bot_config.py
├── bot_settings.json
├── constants.py
└── logging_config.py
main.py
environment.yml
```

## Installation

### Prerequisites

- **Python**: This project uses Python 3.12. Make sure you have Python 3.12 installed or use the provided Conda environment.
- **Anaconda or Miniconda**: Ensure you have Anaconda or Miniconda installed. Download from [anaconda.com](https://www.anaconda.com/products/distribution) or [docs.conda.io](https://docs.conda.io/en/latest/miniconda.html).
- **Git**: To clone the repository. Download from [git-scm.com](https://git-scm.com/downloads).

### Installation Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/mihailmariusiondev/arkantranscripter.git
   cd arkantranscripter
   ```

2. **Create the Conda environment**:

   ```bash
   conda env create -f environment.yml
   ```

   If the environment already exists, you can update it instead:

   ```bash
   conda env update -f environment.yml --prune
   ```

3. **Activate the Conda environment**:

   ```bash
   conda activate arkantranscripter
   ```

   Your prompt should now show `(arkantranscripter)` at the beginning.

4. **Set up environment variables**:

   Create a `.env` file in the root of the project and add your tokens:

   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Verify installation**:

   To ensure everything is set up correctly, run:

   ```bash
   python -c "from bot import run_bot; print('ArkanTranscripter Bot is ready to run!')"
   ```

   This should print "ArkanTranscripter Bot is ready to run!" without any errors.

## Usage

1. **Activate the Conda environment** (if not already activated):

   ```bash
   conda activate arkantranscripter
   ```

2. **Run the bot**:

   ```bash
   python main.py
   ```

   You will see the message `Starting bot...` in the console, indicating that the bot is up and running.

3. **Interacting with the Bot**:

   - **Commands**:

     - `/start`: Start a conversation with the bot.
     - `/transcribe [YouTube URL]`: Transcribe a YouTube video.
     - `/toggle_autotranscription`: Enable/disable automatic transcription.
     - `/toggle_enhanced_transcription`: Enable/disable enhanced transcription.

   - **Transcribing Content**:
     - Send a YouTube link to transcribe the video.
     - Send a video file directly to transcribe it.
     - Send an audio or voice message to transcribe it.

## Deactivating and Deleting the Conda Environment

When you're done working with the bot, you can deactivate the Conda environment. If you need to remove the environment entirely, you can delete it as well.

### Deactivating the Environment

To deactivate the current Conda environment, simply run:

```bash
conda deactivate
```

This will return you to your base Conda environment or your regular shell.

### Deleting the Environment

If you want to completely remove the environment, you can delete it using the following command:

```bash
conda env remove --name arkantranscripter
```

This will remove the entire `arkantranscripter` environment and all its installed packages.

Note: Make sure you're not inside the environment you're trying to remove. If you are, deactivate it first using the command mentioned above.

### Verifying Environment Removal

To confirm that the environment has been removed, you can list all available environments:

```bash
conda env list
```

The `arkantranscripter` environment should no longer appear in this list if it was successfully removed.

## Contribution

Contributions are welcome! If you would like to improve **ArkanTranscripter Bot**, follow these steps:

1. **Fork** the repository.
2. **Create a branch** for your feature or bug fix:

   ```bash
   git checkout -b feature/new-feature
   ```

3. **Make your changes** and **commit** them:

   ```bash
   git commit -m "Add new feature"
   ```

4. **Push** your branch:

   ```bash
   git push origin feature/new-feature
   ```

5. **Create a Pull Request** describing your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

- **Developer**: [@mihailmariusiondev](https://github.com/mihailmariusiondev)

## Contact

For support or inquiries, you can contact me at [@mihailmariusiondev](https://github.com/mihailmariusiondev).

## Acknowledgements

- Thanks to the Python, Telegram, and OpenAI developer communities for continuous inspiration and support.

## Support

If you encounter any issues or have suggestions, please open an [issue](https://github.com/mihailmariusiondev/arkantranscripter/issues) on GitHub.

## Project Status

This project is currently in active development. Features and documentation are subject to change as the project evolves.

## Production Use

For production deployment, consider using process management tools like `systemd` or `supervisor` to ensure the bot automatically restarts in case of failure.

## Conclusion

**ArkanTranscripter Bot** is a powerful tool for transcribing various types of media in your Telegram chats. With its advanced features and easy-to-use commands, it's an excellent addition to any Telegram group or channel where transcription services are needed.
