import base64
import json
import os

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from user import User
from sticker import add_sticker, delete_sticker, make_original_image, compress_image

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = os.getenv("BOT_API_TOKEN")


def make_keyboard(message_id):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=f"yes_{message_id}"),
            InlineKeyboardButton("No", callback_data=f"no_{message_id}"),
        ],
        [
            InlineKeyboardButton(
                "Make sticker w/ original picture",
                callback_data=f"original_{message_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                "Send sticker as file", callback_data=f"file_{message_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Write text prompt", callback_data=f"sam_{message_id}"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def make_keyboard_sam(message_id):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=f"yes_{message_id}"),
            InlineKeyboardButton("No", callback_data=f"no_{message_id}"),
        ],
        [
            InlineKeyboardButton(
                "Try another text prompt",
                callback_data=f"again_{message_id}",
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
        return encoded_image.decode("utf-8")


def base64_to_image(base64_string, output_file_path):
    with open(output_file_path, "wb") as image_file:
        decoded_image = base64.b64decode(base64_string)
        image_file.write(decoded_image)


def request_rembg(input_path):
    payload = {
        "image": image_to_base64(input_path),
    }
    url = os.getenv("API_URL_REMBG")
    print("making request")
    r = requests.post(url, json=payload, timeout=600)
    print("request completed")
    image_base64 = json.loads(r.content)["image"]
    return image_base64


def request_gsa(input_path, text_prompt):
    payload = {
        "image": image_to_base64(input_path),
        "text_prompt": text_prompt,
    }
    url = os.getenv("API_URL_GSA")
    print("making request")
    r = requests.post(url, json=payload, timeout=600)
    print("request completed")
    image_base64 = json.loads(r.content)["image"]
    return image_base64


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! I make stickers. Send me a picture 👨‍🎨")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = update.get_bot()
    user = User(update)
    user_message_id = f"{user.id}_{update.message.id}"
    input_path = f"/tmp/{user_message_id}_input.jpeg"
    output_path = f"/tmp/{user_message_id}_output.webp"
    output_png_path = f"/tmp/{user_message_id}_output.png"
    output_original_path = f"/tmp/{user_message_id}_output_original.webp"
    if update.message.photo:
        await update.message.reply_text("🧮")
        print(user.sticker_set_name)
        print(user.sticker_set_title)
        reply_markup = make_keyboard(update.message.id)
        file_id = update.message.photo[-1].file_id
        media_message = await context.bot.get_file(file_id)
        await media_message.download_to_drive(input_path)

        try:
            image_base64 = request_rembg(input_path)
            base64_to_image(image_base64, output_path)
            base64_to_image(image_base64, output_png_path)
            compress_image(output_path, output_path)
            await update.message.reply_text(
                "Do you want to add this sticker? ✍️",
            )
            await bot.send_sticker(
                user.id,
                output_path,
                reply_markup=reply_markup,
            )
            make_original_image(
                input_path,
                output_original_path,
            )
        except Exception as e:
            await update.message.reply_text(str(e))
    else:
        import re

        user = User(update)
        directory = "/tmp/"
        pattern = rf"^{user.id}_.*_input_sam\.jpeg$"
        files = os.listdir(directory)
        filtered_files = [file for file in files if re.match(pattern, file)]
        filtered_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True
        )
        print(filtered_files)
        if len(filtered_files) > 0:
            await update.message.reply_text("🪄")
            input_sam_path = f"/tmp/{filtered_files[0]}"
            image_base64 = request_gsa(input_sam_path, update.message.text)
            base64_to_image(image_base64, output_path)
            compress_image(output_path, output_path)
            reply_markup = make_keyboard_sam(update.message.id)
            await update.message.reply_text(
                "Do you want to add this sticker? ✍️",
            )
            await bot.send_sticker(
                user.id,
                output_path,
                reply_markup=reply_markup,
            )
            # if image_base64 == "":
            #     await update.message.reply_text(f"'{update.message.text}' was not detected in the image.\nTry another prompt?")
            #     return

        else:
            await update.message.reply_text("Send me a picture 👨‍🎨")


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    user = User(update)
    query = update.callback_query
    # await query.edit_message_reply_markup(reply_markup=None)
    await query.answer()
    user_message_id = f"{user.id}_{query.data.split('_')[-1]}"
    input_path = f"/tmp/{user_message_id}_input.jpeg"
    input_sam_path = f"/tmp/{user_message_id}_input_sam.jpeg"
    output_path = f"/tmp/{user_message_id}_output.webp"
    output_png_path = f"/tmp/{user_message_id}_output.png"
    output_original_path = f"/tmp/{user_message_id}_output_original.webp"
    data = query.data.split("_")[0]

    if data == "sam":
        os.rename(input_path, input_sam_path)
        await query.message.reply_text(
            "Write what you want to cut.\nFor example: person left and brown cat 🖖"
        )
    elif data == "yes":
        await query.delete_message()
        await query.message.reply_text("Sticker added 👌")
        await add_sticker(
            user,
            update.get_bot(),
            output_path,
        )
        os.remove(input_sam_path) if os.path.exists(input_sam_path) else None
    elif data == "no":
        await query.delete_message()
        await query.message.reply_text("Sticker discarded 🤌")
        os.remove(input_sam_path) if os.path.exists(input_sam_path) else None
    elif data == "original":
        if not os.path.exists(output_original_path):
            print(f"file {output_original_path} not found")
            await query.message.reply_text(
                f"Sorry, request expired, send picture again 👇"
            )
            return
        await query.delete_message()
        await query.message.reply_text("Original sticker added ✌")
        await add_sticker(
            user,
            update.get_bot(),
            output_original_path,
        )
    elif data == "file":
        if not os.path.exists(output_png_path):
            print(f"file {output_png_path} not found")
            await query.message.reply_text(
                f"Sorry, request expired, send picture again 👇"
            )
            return
        await query.delete_message()
        await query.message.reply_text("File sent 👍")
        await query.message.reply_document(open(output_png_path, "rb"))
    os.remove(input_path) if os.path.exists(input_path) else None
    os.remove(output_path) if os.path.exists(output_path) else None
    os.remove(output_png_path) if os.path.exists(output_png_path) else None
    os.remove(output_original_path) if os.path.exists(output_original_path) else None


async def handle_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await delete_sticker(update)
    await update.message.reply_text("Last sticker deleted 🥲")


async def handle_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = User(update)
    link = f"https://t.me/addstickers/{user.sticker_set_name}"
    await update.message.reply_text(f"Link to sticker pack: {link}")


def main():
    # application = Application.builder().token(TOKEN).build()
    application = Application.builder().token(TOKEN).concurrent_updates(10).build()

    # Add command handler
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Add picture handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.add_handler(CallbackQueryHandler(handle_choice))

    # Add a /start command handler
    application.add_handler(
        MessageHandler(filters.COMMAND & filters.Regex(r"/start"), start)
    )
    application.add_handler(
        MessageHandler(filters.COMMAND & filters.Regex(r"/delete"), handle_delete)
    )
    application.add_handler(
        MessageHandler(filters.COMMAND & filters.Regex(r"/getpack"), handle_pack)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
