from telegram.ext import Application, CommandHandler, MessageHandler, filters
from requests.exceptions import RequestException
import logging
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your remove.bg API key
REMOVE_BG_API_KEY = '6H6qvsjWASfTkp82VdUL6tS3'

# Your Telegram bot token
TELEGRAM_BOT_TOKEN = '7278921314:AAG7UMoqbbUtLjU__1GxDkhPQEyhVb-gjTk'

# Retry function for making requests to Remove.bg
def remove_background(image_data):
    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            headers={'X-Api-Key': REMOVE_BG_API_KEY},
            files={'image_file': ('image.png', image_data)},
            data={'size': 'auto'}
        )
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Error from Remove.bg: {response.text}")
            return None
    except RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

# Start command handler
async def start(update, context):
    await update.message.reply_text("Send me a photo, and I'll remove its background for you!")

# Photo handler
async def handle_photo(update, context):
    try:
        # Get the photo file
        photo = update.message.photo[-1]
        file = await photo.get_file()
        image_bytes = await file.download_as_bytearray()

        # Process the image with Remove.bg
        result = remove_background(image_bytes)
        if result:
            # Send back the background-removed image
            output_image = BytesIO(result)
            output_image.name = "bg_removed.png"
            output_image.seek(0)
            await update.message.reply_photo(photo=output_image, caption="Here is your image with the background removed!")
        else:
            await update.message.reply_text("Sorry, I couldn't remove the background. Please try again later.")
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await update.message.reply_text("An error occurred while processing your image.")

# Main function to run the bot
def main():
    # Create the Application and pass the bot token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
