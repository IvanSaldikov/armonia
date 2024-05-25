from telegram import Update
from telegram.ext import ContextTypes


def validate_user(handler):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # cast(User, update.effective_user).id
        # if not await is_user_in_channel(user_id, config.TELEGRAM_BOTANIM_CHANNEL_ID):
        #     await send_response(
        #         update, context, response=render_template("vote_cant_vote.j2")
        #     )
        #     return
        await handler(update, context)

    return wrapped
