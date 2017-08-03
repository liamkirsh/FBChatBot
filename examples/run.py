#!/usr/bin/python
import os
import sys

import ConfigParser

from leona import LeonaBot

LEONA_CFG = "settings.cfg"


def main():
    l_config = ConfigParser.RawConfigParser()
    l_session = l_admins = l_protected = l_name = None
    l_user = l_pass = None

    if os.path.exists(LEONA_CFG):
        with open(LEONA_CFG, 'rb') as f:
            l_config.readfp(f)
            if l_config.has_section('session'):
                # If a session was opened, try to reuse it
                l_session = dict(l_config.items('session'))
            if l_config.has_section('roles'):
                l_admins = l_config.get('roles', 'admins')
                l_admins = l_admins.split(',')
                l_protected = l_config.get('roles', 'protected')
                l_protected = l_protected.split(',')
            if l_config.has_section('login'):
                l_user = l_config.get('login', 'user')
                l_pass = l_config.get('login', 'pass')
            if l_config.has_section('bot'):
                l_name = l_config.get('bot', 'name')

    if not l_name:
        raise Exception("You must set the bot's name in the settings file.")
    l_client = LeonaBot(l_user, l_pass, l_name,
                        admins=l_admins, protected=l_protected,
                        session_cookies=l_session)

    if not l_session:
        l_session = l_client.getSession()
        with open(LEONA_CFG, 'wb') as f:
            try:
                l_config.add_section('session')
            except ConfigParser.DuplicateSectionError:
                pass
            for (k, v) in l_session.items():
                l_config.set('session', k, v)
            l_config.write(f)

    l_client.listen()

if __name__ == "__main__":
    main()
