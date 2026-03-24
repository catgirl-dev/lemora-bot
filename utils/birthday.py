from datetime import datetime

from configuration.environment import bot

from database.models import BirthDays


def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%m-%d").strftime("%m-%d")
    except ValueError:
        return None

async def check_birthdays():
    today = datetime.now().strftime("%m-%d")

    birthdays = BirthDays.select().where(
        BirthDays.birthday == today
    )

    chats = {}

    for b in birthdays:
        chats.setdefault(b.chat_id, []).append(b.user_id)

    for chat_id, users in chats.items():
        text = "Сегодня День рождения у:\n"

        for user_id in users:
            try:
                member = await bot.get_chat_member(chat_id, user_id)
                user = member.user

                if user.username:
                    name = f"@{user.username}"
                else:
                    name = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

            except Exception:
                name = f"пользователь {user_id}"

            text += f"{name}\n"

        await bot.send_message(chat_id, text)