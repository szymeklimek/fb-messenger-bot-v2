import os
from fbchat import Client
from fbchat.models import *
import driveapi
import json


class EchoBot(Client):
    tuples = list()

    help_message = "Available commands:\n'Bot tag' => Tags all of the conversation members.\n'Bot meme' => Sends a " \
                   "random meme.\n'Bot link' => Sends a Google Drive link for uploading memes. "

    def __init__(self, email, pw, thread_id, img_folder, session_cookies):
        self.drive_service = driveapi.DriveSetup()
        self.thread_id = thread_id
        self.img_folder_link = img_folder
        self.thread_type = ThreadType.GROUP
        super(EchoBot, self).__init__(email, pw, session_cookies)

    def set_group_users(self):
        user_ids = self.fetchGroupInfo(self.thread_id)[self.thread_id].participants
        user_tuples = list()

        for id in user_ids:
            temp_user = self.fetchUserInfo(id)
            user_tuples.append((id, temp_user[id].name))

        self.tuples = user_tuples

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        if message_object.text == "Bot help" and thread_id == self.thread_id and thread_type == self.thread_type:
            self.reactToMessage(message_object.uid, MessageReaction.YES)
            self.send(Message(
                text=self.help_message,
                reply_to_id=message_object.uid),
                thread_id=thread_id,
                thread_type=thread_type
            )

        if message_object.text == "Bot tag" and thread_id == self.thread_id and thread_type == self.thread_type:
            self.reactToMessage(message_object.uid, MessageReaction.YES)
            tag = "@Everyone"

            msg = Message(text=tag, mentions=[
                Mention(thread_id=t_id,
                        offset=0, length=len(t_name)) for t_id, t_name in self.tuples],
                        reply_to_id=message_object.uid)
            self.send(msg, thread_id=thread_id, thread_type=thread_type)

        if message_object.text == "Bot link" and thread_id == self.thread_id and thread_type == self.thread_type:
            self.reactToMessage(message_object.uid, MessageReaction.YES)
            self.send(Message(
                text="Meme folder link: \n" + self.img_folder_link,
                reply_to_id=message_object.uid),
                thread_id=thread_id,
                thread_type=thread_type
            )

        if message_object.text == "Bot meme" and thread_id == self.thread_id and thread_type == self.thread_type:
            self.reactToMessage(message_object.uid, MessageReaction.YES)
            img = self.drive_service.create_random_img()
            self.sendLocalFiles(
                img,
                thread_id=self.thread_id,
                thread_type=self.thread_type,
            )
            os.remove(img)

    def onPeopleAdded(
            self,
            mid=None,
            added_ids=None,
            author_id=None,
            thread_id=None,
            ts=None,
            msg=None,
    ):
        self.set_group_users()

    def onPersonRemoved(
            self,
            mid=None,
            removed_id=None,
            author_id=None,
            thread_id=None,
            ts=None,
            msg=None,
    ):
        self.set_group_users()

    def send_greeting(self):
        self.send(Message(
            text="I'm alive!\nType in 'Bot help' for available commands."),
            thread_id=self.thread_id,
            thread_type=self.thread_type
        )


def main():
    os.chdir("..")
    with open("bot_creds.json", 'r') as file:
        bot_data = json.load(file)

    client = EchoBot(
        bot_data["email"],
        bot_data["pw"],
        bot_data["thread_id"],
        bot_data["img_folder"],
        session_cookies=str(bot_data["cookies"])
    )
    client.set_group_users()
    client.send_greeting()
    client.listen()


if __name__ == '__main__':
    main()

# thread_id = "3724459277571389"
# thread_type = ThreadType.GROUP

# # Will send a message to the thread
# client.send(Message(text="Hello World!"), thread_id=thread_id, thread_type=thread_type)
#
# # Will send the default `like` emoji
# client.send(
#     Message(emoji_size=EmojiSize.LARGE), thread_id=thread_id, thread_type=thread_type
# )
#
# # Will send the emoji `👍`
# client.send(
#     Message(text="👍", emoji_size=EmojiSize.LARGE),
#     thread_id=thread_id,
#     thread_type=thread_type,
# )
#
# # Will send the sticker with ID `767334476626295`
# client.send(
#     Message(sticker=Sticker("767334476626295")),
#     thread_id=thread_id,
#     thread_type=thread_type,
# )
#
# # Will send a message with a mention
# client.send(
#     Message(
#         text="This is a @mention", mentions=[Mention(thread_id, offset=10, length=8)]
#     ),
#     thread_id=thread_id,
#     thread_type=thread_type,
# )
