from main import messages
from telebot.types import Message

def new_message(message: Message, filter):
    row = {}
    row.update({'id': message.message_id})
    row.update({'date': message.date})
    row.update({'username': message.from_user.username})
    row.update({'chat': message.chat.id})
    row.update({'forward_date': message.forward_date if message.forward_date else None})
    row.update({'forward_from_username': message.forward_from.username if message.forward_from else None})
    row.update({'text': message.text})
    # row.update({'json': message.json})

    newvalues = { "$set":  row}
    result = messages.update_one(filter, newvalues)
    if result.matched_count < 1:
        messages.insert_one(row)
        return True
    return False



