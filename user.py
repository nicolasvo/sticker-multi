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
        self.sticker_set_name = self.get_sticker_set_name()
        self.sticker_set_title = f"{self.firstname} 🐶"
        self.emoji = "🇫🇷"

    def get_sticker_set_name(self, pack_number=0):
        return f"w_{pack_number}_{self.id}_by_{self.bot_username}"
