from bot import Bot


class WilfredBot(Bot):
    def __init__(self, email, password, name, admins=[], protected=[],
                 *args, **kwargs):
        super(WilfredBot, self).__init__(email=email, password=password,
                                         name=name, admins=admins,
                                         protected=protected, num_threads=2,
                                         *args, **kwargs)
        self.add_message_handler("say", self.say_cmd,
                                 admin=True, directed=True)

    def say_cmd(self, msg):
        """Repeat the words following 'say'."""
        self.sendMessage(msg['message'][4:].strip(), msg['thread_id'],
                         msg['thread_type'])

    def onPersonRemoved(self, removed_id, author_id, thread_id, **kwargs):
        if (removed_id != self.uid and
                author_id != self.uid and
                removed_id != author_id and
                removed_id in self.protected):
            # and author_id not in self.admins):
            self.addUsersToGroup(removed_id, thread_id)
