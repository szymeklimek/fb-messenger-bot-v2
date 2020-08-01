import os
import argparse
import pickle

from fbchat import Client
from fbchat.models import *
from drive_api import DriveSetup
import json
import collections


class MessengerBot(Client):
    # dictionary - key:thread_id, value:list of user tuples - (user_id, name)
    tuples_dict = collections.defaultdict(list)

    bot_name = "Amad"

    help_message = "Available commands:\n'" + bot_name + " tag' => Tags all of the conversation members.\n'" + bot_name + " meme' => Sends a " \
                   "random meme.\n'" + bot_name + " link' => Sends a Google Drive link for uploading memes.\n'" + bot_name + " calc [eq]' => " \
                   "Calculate an equation."

    def __init__(self, email, pw, thread_list, img_folder, cmd_args, max_tries, session_cookies):
        self.drive_service = DriveSetup()
        self.thread_list = thread_list
        self.img_folder_link = img_folder
        self.cmd_args = cmd_args
        self.thread_type = ThreadType.GROUP
        self.command_dict = {"help": self.cmd_show_help, "tag": self.cmd_tag_users,
                             "meme": self.cmd_send_img, "link": self.cmd_send_link,
                             "calc": self.cmd_do_calc}
        super(MessengerBot, self).__init__(email, pw, max_tries=max_tries, session_cookies=session_cookies)

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
        # self.markAsDelivered(thread_id, message_object.uid)
        # self.markAsRead(thread_id)

        if message_object.text is not None:
            cmd_list = message_object.text.split(" ")[:3]

            if thread_type == self.thread_type and thread_id in self.thread_list and cmd_list[0] == self.bot_name:

                if cmd_list[1] in self.command_dict:
                    self.command_dict[cmd_list[1]](message_object, thread_id, thread_type, command=cmd_list)

    def onPeopleAdded(self, mid, added_ids, author_id, thread_id, ts, msg):
        self.set_group_users(thread_id)

    def onPersonRemoved(self, mid, removed_id, author_id, thread_id, ts, msg):
        self.set_group_users(thread_id)

    def cmd_show_help(self, message_object, thread_id, thread_type, **kwargs):
        self.reactToMessage(message_object.uid, MessageReaction.YES)
        self.send(Message(
            text=self.help_message,
            reply_to_id=message_object.uid),
            thread_id=thread_id,
            thread_type=thread_type
        )

    def cmd_tag_users(self, message_object, thread_id, thread_type, **kwargs):
        self.reactToMessage(message_object.uid, MessageReaction.YES)
        tag = "@Everyone"

        msg = Message(text=tag, mentions=[
            Mention(thread_id=t_id,
                    offset=0, length=len(t_name)) for t_id, t_name in self.tuples_dict[thread_id]],
                    reply_to_id=message_object.uid)
        self.send(msg, thread_id=thread_id, thread_type=thread_type)

    def cmd_send_img(self, message_object, thread_id, thread_type, **kwargs):
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

    def cmd_send_link(self, message_object, thread_id, thread_type, **kwargs):
        self.reactToMessage(message_object.uid, MessageReaction.YES)
        self.send(Message(
            text="Meme folder link: \n" + self.img_folder_link,
            reply_to_id=message_object.uid),
            thread_id=thread_id,
            thread_type=thread_type
        )

    def cmd_do_calc(self, message_object, thread_id, thread_type, **kwargs):

        result = None

        try:
            eq = kwargs["command"][2].replace("^", "**")
            result = str(eval(eq, {"__builtins__": None}, {}))
        except (SyntaxError, NameError, ZeroDivisionError):
            result = "Wrong syntax :(\nIs there an error in your equation?"
        finally:
            self.reactToMessage(message_object.uid, MessageReaction.YES)
            self.send(Message(
                text=result,
                reply_to_id=message_object.uid),
                thread_id=thread_id,
                thread_type=thread_type
            )

    def send_greeting(self):
        for thread_id in self.thread_list:
            self.send(Message(
                text="I'm alive!\nType in '" + self.bot_name + " help' for available commands."),
                thread_id=thread_id,
                thread_type=self.thread_type
            )


def main():
    os.chdir("..")

    parser = argparse.ArgumentParser()

    parser.add_argument('-nl', '--nogooglelog', action='store_true', help="disables google cloud logging")
    parser.add_argument('-ng', '--nogreeting', action='store_true', help="disables greeting message")

    args = parser.parse_args()

    if not args.nogooglelog:

        import logging
        import google.cloud.logging
        from google.cloud.logging.handlers import CloudLoggingHandler

        logclient = google.cloud.logging.Client()
        handler = CloudLoggingHandler(logclient)
        cloud_logger = logging.getLogger('cloudLogger')
        cloud_logger.setLevel(logging.INFO)
        cloud_logger.addHandler(handler)

    with open('bot_creds.json', 'r') as file:
        bot_data = json.load(file)

    if os.path.exists('cookies.pickle'):
        with open('cookies.pickle', 'rb') as token:
            cookies = pickle.load(token)
    else:
        cookies = None

    # noinspection PyTypeChecker
    client = MessengerBot(
        bot_data["email"],
        bot_data["pw"],
        bot_data["thread_list"],
        bot_data["img_folder"],
        args,
        max_tries=1,
        session_cookies=cookies
    )

    session = client.getSession()

    with open('cookies.pickle', 'wb') as token:
        pickle.dump(session, token)

    client.listen()


if __name__ == '__main__':
    main()
