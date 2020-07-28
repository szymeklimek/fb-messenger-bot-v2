import os
import argparse
from fbchat import Client
from fbchat.models import *
import driveapi
import json
import collections


class MessengerBot(Client):
    # dictionary - key:thread_id, value:list of user tuples - (user_id, name)
    tuples_dict = collections.defaultdict(list)

    help_message = "Available commands:\n'Bot tag' => Tags all of the conversation members.\n'Bot meme' => Sends a " \
                   "random meme.\n'Bot link' => Sends a Google Drive link for uploading memes. "

    def __init__(self, email, pw, thread_list, img_folder, cmd_args, session_cookies):
        self.drive_service = driveapi.DriveSetup()
        self.thread_list = thread_list
        self.img_folder_link = img_folder
        self.cmd_args = cmd_args
        self.thread_type = ThreadType.GROUP
        self.command_dict = {"Bot help": self.cmd_show_help, "Bot tag": self.cmd_tag_users,
                             "Bot meme": self.cmd_send_img, "Bot link": self.cmd_send_link}
        super(MessengerBot, self).__init__(email, pw, session_cookies)

        self.set_group_users(self.thread_list)
        if not self.cmd_args.nogreeting:
            self.send_greeting()

    def set_group_users(self, thread_list):
        for thread_id in thread_list:
            user_ids = self.fetchGroupInfo(thread_id)[thread_id].participants
            user_tuples = list()

            for user_id in user_ids:
                temp_user = self.fetchUserInfo(user_id)
                user_tuples.append((user_id, temp_user[user_id].name))

            self.tuples_dict[thread_id] = user_tuples

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        if thread_type == self.thread_type and thread_id in self.thread_list:

            if message_object.text in self.command_dict:
                self.command_dict[message_object.text](message_object, thread_id, thread_type)

    def onPeopleAdded(self, mid, added_ids, author_id, thread_id, ts, msg):
        self.set_group_users(thread_id)

    def onPersonRemoved(self, mid, removed_id, author_id, thread_id, ts, msg):
        self.set_group_users(thread_id)

    def cmd_show_help(self, message_object, thread_id, thread_type):
        self.reactToMessage(message_object.uid, MessageReaction.YES)
        self.send(Message(
            text=self.help_message,
            reply_to_id=message_object.uid),
            thread_id=thread_id,
            thread_type=thread_type
        )

    def cmd_tag_users(self, message_object, thread_id, thread_type):
        self.reactToMessage(message_object.uid, MessageReaction.YES)
        tag = "@Everyone"

        msg = Message(text=tag, mentions=[
            Mention(thread_id=t_id,
                    offset=0, length=len(t_name)) for t_id, t_name in self.tuples_dict[thread_id]],
                      reply_to_id=message_object.uid)
        self.send(msg, thread_id=thread_id, thread_type=thread_type)

    def cmd_send_img(self, message_object, thread_id, thread_type):
        img = self.drive_service.create_random_img()
        if img:
            self.reactToMessage(message_object.uid, MessageReaction.YES)
            self.sendLocalFiles(
                img,
                Message(reply_to_id=message_object.uid),
                thread_id=thread_id,
                thread_type=thread_type,
            )
            os.remove(img)
        else:
            self.reactToMessage(message_object.uid, MessageReaction.NO)
            self.send(Message(
                text="Folder Empty :("),
                thread_id=thread_id,
                thread_type=self.thread_type
            )

    def cmd_send_link(self, message_object, thread_id, thread_type):
        self.reactToMessage(message_object.uid, MessageReaction.YES)
        self.send(Message(
            text="Meme folder link: \n" + self.img_folder_link,
            reply_to_id=message_object.uid),
            thread_id=thread_id,
            thread_type=thread_type
        )

    def send_greeting(self):
        for thread_id in self.thread_list:
            self.send(Message(
                text="I'm alive!\nType in 'Bot help' for available commands."),
                thread_id=thread_id,
                thread_type=self.thread_type
            )


def main():

    os.chdir("..")

    parser = argparse.ArgumentParser()

    parser.add_argument('-gl', '--googlelog', action='store_true', help="enables google cloud logging")
    parser.add_argument('-ng', '--nogreeting', action='store_true', help="disables greeting message")

    args = parser.parse_args()

    if args.googlelog:

        import google.cloud.logging
        logclient = google.cloud.logging.Client()
        logclient.get_default_handler()
        logclient.setup_logging()

    with open("bot_creds.json", 'r') as file:
        bot_data = json.load(file)

    # noinspection PyTypeChecker
    client = MessengerBot(
        bot_data["email"],
        bot_data["pw"],
        bot_data["thread_list"],
        bot_data["img_folder"],
        args,
        session_cookies=str(bot_data["cookies"])
    )

    client.listen()


if __name__ == '__main__':
    main()
