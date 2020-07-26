from fbchat import log, Client
from fbchat.models import *


# Subclass fbchat.Client and override required methods
class EchoBot(Client):

    tuples = list()

    def __init__(self, email, pw, session_cookies):
        self.thread_id = "3724459277571389"
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

        if message_object.text == "Bot tag" and thread_type == self.thread_type and thread_id == self.thread_id:

            tag = "@Everyone"

            msg = Message(text=tag, mentions=[Mention(thread_id=t_id, offset=0, length=len(t_name)) for t_id,
            t_name in self.tuples])
            self.send(msg, thread_id=thread_id, thread_type=thread_type)

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


client = EchoBot('matthew.botte69123@gmail.com', '*jK`=s:5kV]}Ub>*',
                 session_cookies="{'c_user': '100053935090694', 'datr': 'vvQdX9HmsHfiNUQx8wjcCMm1', "
                                 "'fr': '1069E9ozoKcxcfE5s.AWUgFyXfJpNDLPJztIAt1noBsgI.BfHfS-.aF.AAA.0.0.BfHfS"
                                 "-.AWXQHQv3', 'noscript': '1', 'sb': 'vvQdX9B5blaGXc5EizxVOMcv', "
                                 "'spin': 'r.1002420352_b.trunk_t.1595798720_s.1_v.2_', "
                                 "'xs': '24%3AZKTsBfIjWnYnkg%3A2%3A1595798718%3A-1%3A-1'}")

client.set_group_users()

client.listen()

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
