from telegram import Update, InputSticker
from telegram.constants import StickerFormat

from user import User, Bot


async def add_sticker_pack(user: User, bot: Bot, sticker_path: str) -> None:
    await bot.create_new_sticker_set(
        user.id,
        user.sticker_set_name,
        user.sticker_set_title,
        [InputSticker(open(sticker_path, "rb"), "🍟")],
        sticker_format=StickerFormat.STATIC,
    )
    print("Sticker set created")


async def add_sticker(user: User, bot, sticker_path: str) -> None:
    await bot.add_sticker_to_set(
        user.id, user.sticker_set_name, InputSticker(open(sticker_path, "rb"), "🍟")
    )
    print("Sticker added")


async def delete_sticker(update: Update) -> None:
    user = User(update)
    bot = update.get_bot()
    sticker_set = await bot.get_sticker_set(user.sticker_set_name)
    if len(sticker_set.stickers) > 0:
        last_sticker = sticker_set.stickers[-1].file_id
        await bot.delete_sticker_from_set(last_sticker)
        print("Sticker deleted")
        await update.message.reply_text("Last sticker deleted! 🥲")
    else:
        await update.message.reply_text("Can't delete, no sticker left in pack")
