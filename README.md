# ArkanTranscripter Bot

ArkanTranscripter es un bot de Telegram diseñado para transcribir videos de YouTube y videos enviados directamente al chat. Utiliza la API de YouTube Transcript y la tecnología de OpenAI para proporcionar transcripciones precisas y mejoradas.

## 🛠️ Características principales

1. **Transcripción de videos de YouTube**

   - Transcribe videos de YouTube a partir de un enlace compartido.
   - Soporta múltiples idiomas (prioriza inglés si está disponible).

2. **Transcripción de videos enviados**

   - Transcribe videos enviados directamente al chat de Telegram.
   - Utiliza el modelo Whisper de OpenAI para la transcripción inicial.

3. **Mejora de transcripciones con IA**

   - Utiliza GPT-4o mini de OpenAI para mejorar la calidad de las transcripciones.
   - Corrige errores ortográficos, mejora la puntuación y la estructura de las oraciones.

4. **Transcripción automática**

   - Opción para activar/desactivar la transcripción automática de enlaces y videos.

5. **Manejo de videos largos**

   - Divide las transcripciones largas en múltiples mensajes para facilitar la lectura.

6. **Configuración de usuarios autorizados**
   - Controla quién puede utilizar el bot mediante una lista de usuarios autorizados.

## 📋 Comandos disponibles

- `/start`: Inicia el bot y muestra un mensaje de bienvenida.
- `/transcribe [URL de YouTube]`: Transcribe el video de YouTube especificado.
- `/toggle_autotranscription`: Activa o desactiva la transcripción automática.
- `/toggle_enhanced_transcription`: Activa o desactiva la transcripción mejorada.

## 📚 Uso

1. **Iniciar el bot**

   - Inicia una conversación con el bot en Telegram.
   - Envía el comando `/start` para recibir un mensaje de bienvenida y las instrucciones básicas.

2. **Transcribir un video de YouTube**

   - Envía el comando `/transcribe` seguido del enlace del video de YouTube.
   - Ejemplo: `/transcribe https://www.youtube.com/watch?v=ejemplo`

3. **Transcribir un video o audio enviado directamente**

   - Envía un archivo de video, audio o un mensaje de voz directamente al chat con el bot.
   - El bot procesará y enviará la transcripción correspondiente.

4. **Configurar funcionalidades**
   - Utiliza los comandos de toggle para activar o desactivar funcionalidades específicas según tus necesidades.

## ⚙️ Configuración

El bot utiliza las siguientes APIs y servicios:

- **API de Telegram**: Para la interacción con los usuarios.
- **API de YouTube Transcript**: Para obtener transcripciones de videos de YouTube.
- **OpenAI API**: Utiliza los modelos Whisper para transcripción y GPT-4o mini para mejora de transcripciones.

### Variables de Entorno

Asegúrate de configurar las claves de API correspondientes en el archivo `.env`:

```env
BOT_TOKEN=tu_token_de_telegram
OPENAI_API_KEY=tu_api_key_de_openai
```

### Archivo de Configuración

El archivo `config/bot_settings.json` contiene la configuración de las funcionalidades y los usuarios autorizados. Asegúrate de actualizar este archivo según tus necesidades.

```json
{
  "auto_transcription_enabled": true,
  "enhanced_transcription_enabled": true,
  "authorized_users": ["123456789", "987654321"]
}
```

## 📦 Requisitos

Ver `requirements.txt` para la lista completa de dependencias.

```plaintext
# Telegram Bot API wrapper
python-telegram-bot

# YouTube transcript API for fetching video captions
youtube-transcript-api

# OpenAI API client for GPT y Whisper models
openai==1.50.2

# Environment variable management
python-dotenv==1.0.1

# Asyncio for asynchronous processing
asyncio==3.4.3
```

## 📝 Notas

- La transcripción automática está habilitada por defecto.
- El bot puede manejar tanto enlaces de YouTube como videos enviados directamente.
- Las transcripciones mejoradas pueden tardar un poco más debido al procesamiento adicional con GPT-4o mini.
- Asegúrate de que los usuarios que interactúan con el bot estén incluidos en la lista de `authorized_users` para garantizar la seguridad y el control de acceso.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de enviar un pull request.

## 📄 Licencia

Este proyecto está bajo la [Licencia MIT](./LICENSE).

## 🔗 Enlaces Útiles

- [Repositorio de Repopack](https://github.com/yamadashy/repopack)

---

**¡Gracias por utilizar ArkanTranscripter Bot! Si tienes alguna pregunta o sugerencia, no dudes en contactarnos.**
