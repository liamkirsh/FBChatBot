import json
import random

import requests
from fbchat.models import ThreadType, MessageReaction

from bot import Bot
import strings

#SP_THREAD_ID = "1596917460381604"
SP_THREAD_ID = "1261018777320723"


class LeonaBot(Bot):
    def __init__(self, email, password, name, admins=[], protected=[], *args, **kwargs):
        super(LeonaBot, self).__init__(email=email, password=password, name=name,
                                       admins=admins, protected=protected,
                                       *args, **kwargs)
        
        self.no_swearing = False

        self.add_message_handler("noswear", self.noswear_cmd)
        self.add_message_handler("swear", self.swear_cmd, admin=True)
        self.add_message_handler("say", self.say_cmd, admin=True)
        self.add_message_handler("protect", self.protect_cmd, admin=True)
        self.add_message_handler("unprotect", self.unprotect_cmd, admin=True)
        self.add_message_handler("meme", self.meme_cmd)
        self.add_message_handler("readd", self.readd_cmd, admin=True)
        self.add_message_handler("trump", self.trump_cmd)
        self.add_message_handler("love", self.love_cmd)

    def love_cmd(self, msg):
        """I'll heart react your message."""
        self.reactToMessage(msg['mid'], MessageReaction.LOVE)

    def noswear_cmd(self, msg):
        """Kick people for swearing."""
        self.sendMessage("Swearing now prohibited. Violators will be kicked.",
                         msg['thread_id'], msg['thread_type'])
        self.no_swearing = True

    def swear_cmd(self, msg):
        """Turn off noswear."""
        self.sendMessage("Cover your ears, kids. Swearing now allowed.", 
                         msg['thread_id'], msg['thread_type'])
        self.no_swearing = False

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
            self.sendMessage("{} ({}) removed from protected users list.".format(
                             uprotect_name, uprotect_id),
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
            return s

        meme_data = msg['message'].split(' ')
        if meme_data == ["meme", "help"]:
            self.sendMessage(strings.meme_help,
                             msg['thread_id'], msg['thread_type'])
        else:
            meme_type = meme_data[1]
            meme_text = [t.strip() for t in ' '.join(meme_data[2:]).split('/', 1)]
            top_text = clean(meme_text[0])
            if len(meme_text) > 1:
                bottom_text = clean(meme_text[1])
                img_url = "https://memegen.link/{}/{}/{}.jpg".format(meme_type, top_text, bottom_text)
            else:
                img_url = "https://memegen.link/{}/{}.jpg".format(meme_type, top_text)
            self.sendRemoteImage(img_url, "", msg['thread_id'], msg['thread_type'])

    def readd_cmd(self, msg):
        """I'll readd you to the group chat."""
        self.sendMessage("Readding you to the Shitposters chat.", msg['thread_id'], msg['thread_type'])
        self.addUsersToGroup(msg['author_id'], SP_THREAD_ID)

    def trump_cmd(self, msg):
        """Search for Trump quotes."""
        params = {'query': msg['message'].split(' ', 1)[1]}
        r = requests.get("https://api.tronalddump.io/search/quote", params=params)
        data = json.loads(r.content)
        count = data['count']
        if count < 1:
            self.sendMessage("I couldn't find a quote with that keyword.",
                             msg['thread_id'], msg['thread_type'])
            return
        n = random.randint(0, count - 1)
        quote = data['_embedded']['quotes'][n]['value']
        self.sendMessage(quote, msg['thread_id'], msg['thread_type'])

    def onMessage(self, **kwargs):
        super(LeonaBot, self).onMessage(**kwargs)
        if (self.no_swearing and any(swear in kwargs['message'].lower() for swear in strings.swears)
                and kwargs['thread_type'] == ThreadType.GROUP and kwargs['author_id'] != self.uid
                and kwargs['author_id'] not in self.protected):
            self.sendMessage("Please don't swear on my profile thanks.", kwargs['thread_id'], kwargs['thread_type'])
            self.removeUserFromGroup(kwargs['author_id'], kwargs['thread_id'])
            
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
        if (thread_id == SP_THREAD_ID
            and removed_id != self.uid
            and author_id != self.uid
            and removed_id != author_id
            and removed_id in self.protected):
            #and author_id not in self.admins):
            self.addUsersToGroup(removed_id, thread_id=SP_THREAD_ID)