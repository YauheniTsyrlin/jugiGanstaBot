from main import messages
from telebot.types import Message

def write_message(message: Message, filter):
    row = {}
    row = {'id': message.message_id}
    row = {'username': message.from_user.username}
    row = {'chat': message.chat.id}
    row = {'forward_date': message.forward_date if message.forward_date else None}
    row = {'forward_from_username': message.from_user.username if message.forward_from else None}
    row = {'text': message.text}
    row = {'json': message.json}

    newvalues = { "$set":  row}
    result = messages.update_one(filter, newvalues)
    if result.matched_count < 1:
        messages.insert_one(row)

