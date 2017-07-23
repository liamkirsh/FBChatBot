from collections import namedtuple

from fbchat import Client


class Bot(Client):
    Command = namedtuple('Command', ['func', 'admin', 'directed'])

    def __init__(self, email, password, name, admins=[], protected=[], *args, **kwargs):
        super(Bot, self).__init__(email=email, password=password,
                                     *args, **kwargs)
        self.name = name
        self.protected = protected + admins
        self.admins = admins
        self.commands = {}
        
        self.add_message_handler("help", self.commands_cmd)

    def commands_cmd(self, msg):
        """Print this message."""
        def get_commands():
            return self.commands.iteritems()

        commands_msg = "You can say:\n"
        for kword, cmd in sorted(get_commands(), key=lambda x: x[1].admin):
            admin_msg = " (admin only)" if cmd.admin else ""
            commands_msg += "{}:{} {}\n".format(kword, admin_msg, cmd.func.__doc__)
        self.sendMessage(commands_msg, msg['thread_id'], msg['thread_type'])

    def add_message_handler(self, kword, func, admin=False, directed=True):
        self.commands[kword] = Bot.Command(func, admin, directed)

    def onMessage(self, **kwargs):
        super(Bot, self).onMessage(**kwargs)
        if kwargs['author_id'] == self.uid:
            return

        is_admin = kwargs['author_id'] in self.admins
        is_directed = (kwargs['message'].startswith("@" + self.name)
                       or kwargs['thread_type'] == "USER")
        if is_directed:
            kwargs['message'] = kwargs['message'].split("@" + self.name)[1].strip()
        kword = kwargs['message'].split(' ', 1)[0].lower()
        cmd = self.commands.get(kword)
        if (cmd and (not cmd.admin or is_admin)
                and (not cmd.directed or is_directed)):
            cmd.func(kwargs) 
