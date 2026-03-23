from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router

from database.models import BirthDays
from utils.birthday import parse_date

from configuration.environment import bot

birthday: Router = Router()

@birthday.message(Command('add_birthday'))
async def add_birthday(message: Message):
    """ Добавление Дня рождения пользователя """
    args = message.text.split()

    if len(args) != 3:
        await message.reply("Для использования команды введите /add_birthday <user_id> <MM-DD>")
        return

    date = parse_date(args[2])

    if not date:
        await message.reply("Неверный формат даты. Используйте MM-DD")
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("user_id должен быть числом")
        return

    if user_id > 9223372036854775807 or user_id < 0:
        await message.reply("Некорректный user_id!")
        return

    user, created = BirthDays.get_or_create(
        chat_id=message.chat.id,
        user_id=user_id,
        defaults={
            "birthday": date
        }
    )

    if not created:
        await message.reply("День рождения для пользователя уже есть в БД. "
                            "Для изменения даты используйте /change_birthday <user_id> <MM-DD>")
        return

    await message.reply("День рождения добавлен в БД")

@birthday.message(Command('delete_birthday'))
async def delete_birthday(message: Message):
    """ Удаление Дня рождения пользователя """
    args = message.text.split()

    if len(args) != 2:
        await message.reply("Для использования команды введите /delete_birthday <user_id>")
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("user_id должен быть числом")
        return

    user = BirthDays.get_or_none(
        BirthDays.chat_id == message.chat.id,
        BirthDays.user_id == user_id
    )

    if not user:
        await message.reply("Пользователь не найден в БД")
        return

    user.delete_instance()

    await message.reply("День рождения успешно удалён")

@birthday.message(Command('change_birthday'))
async def change_birthday(message: Message):
    """ Изменение Дня рождения пользователя """
    args = message.text.split()

    if len(args) != 3:
        await message.reply(
            "Для использования команды введите /change_birthday <user_id> <MM-DD>"
        )
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("user_id должен быть числом")
        return

    if user_id > 9223372036854775807 or user_id < 0:
        await message.reply("Некорректный user_id!")
        return

    date = parse_date(args[2])

    if not date:
        await message.reply("Неверный формат даты. Используйте MM-DD")
        return

    user = BirthDays.get_or_none(
        BirthDays.chat_id == message.chat.id,
        BirthDays.user_id == user_id
    )

    if not user:
        await message.reply("Пользователь не найден")
        return

    user.birthday = date
    user.save()

    await message.reply("День рождения успешно обновлён")

@birthday.message(Command('get_all_birthdays'))
async def get_all_birthdays(message: Message):
    """ Показывает список дней рождения в чате """
    birthdays = BirthDays.select().where(
        BirthDays.chat_id == message.chat.id
    ).order_by(BirthDays.birthday)

    if not birthdays:
        await message.reply("Список дней рождения пуст.")
        return

    text = ["Список дней рождения:\n"]
    for b in birthdays:
        try:
            member = await bot.get_chat_member(message.chat.id, b.user_id)
            user = member.user
            if user.username:
                name = f"@{user.username}"
            else:
                name = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        except TelegramBadRequest:
            name = f"@{b.username}" if b.username else f"пользователь {b.user_id}"

        if b.birthday and '-' in b.birthday:
            month, day = b.birthday.split('-')
            date_str = f"{day}.{month}"
        else:
            date_str = b.birthday

        text.append(f"{name} — {date_str}")

    await message.reply("\n".join(text))