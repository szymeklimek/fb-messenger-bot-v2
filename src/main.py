from fbchat import Client
from fbchat.models import *

client = Client("mafiabot123@gmail.com", "*jK`=s:5kV]}Ub>*")

thread_id = "3724459277571389"
thread_type = ThreadType.GROUP

# Will send a message to the thread
client.send(Message(text="Hello World!"), thread_id=thread_id, thread_type=thread_type)

# Will send the default `like` emoji
client.send(
    Message(emoji_size=EmojiSize.LARGE), thread_id=thread_id, thread_type=thread_type
)

# Will send the emoji `👍`
client.send(
    Message(text="👍", emoji_size=EmojiSize.LARGE),
    thread_id=thread_id,
    thread_type=thread_type,
)

# Will send the sticker with ID `767334476626295`
client.send(
    Message(sticker=Sticker("767334476626295")),
    thread_id=thread_id,
    thread_type=thread_type,
)

# Will send a message with a mention
client.send(
    Message(
        text="This is a @mention", mentions=[Mention(thread_id, offset=10, length=8)]
    ),
    thread_id=thread_id,
    thread_type=thread_type,
)