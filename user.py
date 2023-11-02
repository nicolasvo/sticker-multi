from telegram import Update


class User:
    def __init__(self, update: Update):
        if update.callback_query:
            self.chat_id = update.callback_query.message.chat_id
            self.id = update.callback_query.from_user.id
            self.firstname = update.callback_query.from_user.first_name
        elif update.message:
            self.chat_id = update.message.chat_id
            self.id = update.message.from_user.id
            self.firstname = update.message.from_user.first_name
        bot = update.get_bot()
        self.bot_username = bot.username


async def get_sticker_set_name(user, bot, pack_number=0):
    sticker_set_name = f"w_{pack_number}_{user.id}_by_{user.bot_username}"
    try:
        sticker_set = await bot.get_sticker_set(sticker_set_name)
        if sticker_set:
            if len(sticker_set.stickers) == 120:
                pack_number += 1
                return await get_sticker_set_name(user, bot, pack_number)
            return sticker_set_name
    except:
        return sticker_set_name
