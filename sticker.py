import cv2
import numpy as np
from telegram import Update, InputSticker
from telegram.constants import StickerFormat
from telegram.error import BadRequest

from user import User


async def add_sticker_pack(user: User, bot, sticker_path: str) -> None:
    await bot.create_new_sticker_set(
        user.id,
        user.sticker_set_name,
        user.sticker_set_title,
        [InputSticker(open(sticker_path, "rb"), "🍟")],
        sticker_format=StickerFormat.STATIC,
    )
    print("Sticker set created")


async def add_sticker(user, bot, output_path):
    try:
        print("add sticker")
        await add_sticker_(user, bot, output_path)
        sticker_set = await bot.get_sticker_set(user.sticker_set_name)
        await bot.send_sticker(
            user.chat_id,
            sticker_set.stickers[-1],
        )
    except Exception as e:
        print("add sticker pack")
        print(f"exception: {e}")
        await add_sticker_pack(user, bot, output_path)
        sticker_set = await bot.get_sticker_set(user.sticker_set_name)
        await bot.send_sticker(
            user.chat_id,
            sticker_set.stickers[-1],
        )


async def add_sticker_(user: User, bot, sticker_path: str) -> None:
    await bot.add_sticker_to_set(
        user.id, user.sticker_set_name, InputSticker(open(sticker_path, "rb"), "🍟")
    )
    print("Sticker added")


async def delete_sticker(update: Update, sticker_id) -> None:
    user = User(update)
    bot = update.get_bot()
    sticker_set = await bot.get_sticker_set(user.sticker_set_name)
    if len(sticker_set.stickers) > 0:
        try:
            await bot.delete_sticker_from_set(sticker_id)
            await update.message.reply_text("Sticker deleted 🥲")
        except BadRequest as e:
            await update.message.reply_text(
                "Can't delete, sticker does not belong to this pack 👎"
            )
    else:
        await update.message.reply_text("Can't delete, no sticker left in pack 👎")


def make_original_image(input_path, output_path):
    image = cv2.imread(input_path)
    image = rescale_image(image)
    cv2.imwrite(output_path, image)


def rescale_image(image, px=512, padding=0):
    height, width, _ = image.shape
    if [height, width].index(max([height, width])) == 0:
        factor = px / height
        height = px
        width = int(width * factor)
    else:
        factor = px / width
        width = px
        height = int(height * factor)

    image_resized = cv2.resize(
        image, dsize=(width, height), interpolation=cv2.INTER_LINEAR
    )

    # Create a larger canvas with the same number of channels as the input image
    padded_height = height + 2 * padding
    padded_width = width + 2 * padding
    padded_image = np.zeros(
        (padded_height, padded_width, image.shape[2]), dtype=np.uint8
    )

    # Calculate the position to place the resized image in the center
    x_offset = (padded_width - width) // 2
    y_offset = (padded_height - height) // 2

    # Place the resized image in the center of the padded canvas
    padded_image[
        y_offset : y_offset + height, x_offset : x_offset + width
    ] = image_resized

    return padded_image


def compress_image(input_path, output_path):
    # Load the original PNG image
    original_image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)

    # Define the compression parameters for PNG (lossless compression)
    compression_params = [
        cv2.IMWRITE_PNG_COMPRESSION,
        9,
    ]  # 0 (no compression) to 9 (max compression)

    # Compress and save the image as PNG
    cv2.imwrite(output_path, original_image, compression_params)
