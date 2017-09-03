#!/usr/bin/python
import os
import sys

import ConfigParser

from leona import LeonaBot as Bot

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
CFG = os.path.join(__location__, 'settings.cfg')


def main():
    config = ConfigParser.RawConfigParser()
    session = admins = protected = name = None
    user = pwd = None

    if os.path.exists(CFG):
        with open(CFG, 'rb') as f:
            config.readfp(f)
            if config.has_section('session'):
                # If a session was opened, try to reuse it
                session = dict(config.items('session'))
            if config.has_section('roles'):
                admins = config.get('roles', 'admins')
                admins = admins.split(',')
                protected = config.get('roles', 'protected')
                protected = protected.split(',')
            if config.has_section('login'):
                user = config.get('login', 'user')
                pwd = config.get('login', 'pass')
            if config.has_section('bot'):
                name = config.get('bot', 'name')

    if not name:
        raise Exception("You must set the bot's name in the settings file.")
    client = Bot(user, pwd, name,
                        admins=admins, protected=protected,
                        session_cookies=session)

    if not session:
        session = client.getSession()
        with open(CFG, 'wb') as f:
            try:
                config.add_section('session')
            except ConfigParser.DuplicateSectionError:
                pass
            for (k, v) in session.items():
                config.set('session', k, v)
            config.write(f)

    client.listen()

if __name__ == "__main__":
    main()
