import sys
import json
import random
import urllib

import requests
from fbchat.models import ThreadType, MessageReaction
from googletrans import Translator

from bot import Bot
import strings

# THREAD_ID is only used for readding admins. Leona will work in any chat she's
# added to.
THREAD_ID = "1261018777320723"


class LeonaBot(Bot):
    def __init__(self, email, password, name, admins=[], protected=[],
                 *args, **kwargs):
        super(LeonaBot, self).__init__(email=email, password=password,
                                       name=name, admins=admins,
                                       protected=protected, *args, **kwargs)

        self.add_message_handler("say", self.say_cmd, admin=True)
        self.add_message_handler("protect", self.protect_cmd, admin=True)
        self.add_message_handler("unprotect", self.unprotect_cmd, admin=True)
        self.add_message_handler("meme", self.meme_cmd)
        self.add_message_handler("readd", self.readd_cmd, admin=True)
        self.add_message_handler("trump", self.trump_cmd)
        self.add_message_handler("love", self.love_cmd)
	self.add_message_handler("translate", self.translate_cmd)
        self.translator = Translator()

    def translate_cmd(self, msg):
        """Translate any text to English."""
        text = msg['message'][10:].strip()
	result = "Translation: " + self.translator.translate(text).text
        self.sendMessage(result, msg['thread_id'], msg['thread_type'])

    def love_cmd(self, msg):
        """I'll heart react your message."""
        self.reactToMessage(msg['mid'], MessageReaction.LOVE)

    def say_cmd(self, msg):
        """Repeat the words following 'say'."""
        self.sendMessage(msg['message'][4:].strip(), msg['thread_id'],
                         msg['thread_type'])

    def protect_cmd(self, msg):
        """Readd the specified person if they are removed."""
        protect_name = msg['message'][8:].strip('@').strip()
        protect_id = self.protect_user(protect_name)
        if protect_id:
            self.sendMessage("{} ({}) added to protected users list.".format(
                protect_name, protect_id),
                msg['thread_id'], msg['thread_type'])
        else:
            self.sendMessage("I couldn't find a user with that name.",
                             msg['thread_id'], msg['thread_type'])

    def unprotect_cmd(self, msg):
        """Stop readding the specified person."""
        uprotect_name = msg['message'][10:].strip('@').strip()
        uprotect_id = self.unprotect_user(uprotect_name)
        if uprotect_id:
            self.sendMessage("{} removed from protected users list.".format(
                             uprotect_name),
                             msg['thread_id'], msg['thread_type'])
        else:
            self.sendMessage("I couldn't find a user with that name.",
                             msg['thread_id'], msg['thread_type'])

    def meme_cmd(self, msg):
        """Generate a meme. Use 'meme help' command for more info."""
        def clean(s):
            """Clean text before sending it to memegen."""
            s = '_'.join(s.split())
            s = s.replace('?', '~q').replace('%', '~p').replace('#', '~h')
            s = s.replace('/', '~s').replace('"', "''")
            return s
        def url_format(string, *args):
            """Encode a URL with given parameters."""
            return string.format(*(urllib.quote(arg, safe="") for arg in args))

        meme_data = msg['message'].lower().split(' ')
        if meme_data == ["meme", "help"]:
            self.sendMessage(strings.meme_help,
                             msg['thread_id'], msg['thread_type'])
        else:
            meme_type = meme_data[1]
            meme_text = [t.strip()
                         for t in ' '.join(meme_data[2:]).split('/', 1)]
            top_text = clean(meme_text[0])

            if len(meme_text) > 1:
                bottom_text = clean(meme_text[1])
                img_url = url_format("https://memegen.link/{}/{}/{}.jpg",
                                     meme_type, top_text, bottom_text)
            else:
                img_url = url_format("https://memegen.link/{}/{}.jpg",
                                     meme_type, top_text)
            self.sendRemoteImage(img_url, "",
                                 msg['thread_id'], msg['thread_type'])

    def readd_cmd(self, msg):
        """I'll readd you to the group chat."""
        if THREAD_ID:
            self.sendMessage("Readding you to the chat.",
                             msg['thread_id'], msg['thread_type'])
            self.addUsersToGroup(msg['author_id'], THREAD_ID)
        else:
            self.sendMessage("Error: Thread ID not specified in the code.",
                             msg['thread_id'], msg['thread_type'])
            sys.stderr.write(
                "Error: You must specify thread ID in the code.\n")

    def trump_cmd(self, msg):
        """Search for Trump quotes."""
        params = {'query': msg['message'].split(' ', 1)[1]}
        r = requests.get("https://api.tronalddump.io/search/quote",
                         params=params)
        data = json.loads(r.content)
        count = data['count']
        if count < 1:
            self.sendMessage("I couldn't find a quote with that keyword.",
                             msg['thread_id'], msg['thread_type'])
            return
        n = random.randint(0, count - 1)
        quote = data['_embedded']['quotes'][n]['value']
        self.sendMessage(quote, msg['thread_id'], msg['thread_type'])

    def protect_user(self, user_name):
        users = self.fetchAllUsers()
        users = filter(lambda u: u.name == user_name, users)
        if users:
            uid = users[0].uid
            if uid not in self.protected:
                self.protected.append(uid)
            return uid
        else:
            return None

    def unprotect_user(self, user_name):
        users = self.fetchAllUsers()
        users = filter(lambda u: u.name == user_name, users)
        if users:
            uid = users[0].uid
            if uid in self.protected:
                self.protected.remove(uid)
            return uid
        else:
            return None

    def onPersonRemoved(self, removed_id, author_id, thread_id, **kwargs):
        if (removed_id != self.uid and
                author_id != self.uid and
                removed_id != author_id and
                removed_id in self.protected):
            # and author_id not in self.admins):
            self.addUsersToGroup(removed_id, thread_id=thread_id)
