# -*- coding: UTF-8 -*-
import telepot.loop
import socket
import sqlite3
import sqliteshelve
import telepot
import time
import requests
import hashlib
import pprint

manuel_id = 45571984


class Secretary(object):
    def __init__(self, key):
        self.conn = sqlite3.connect('database.sqlite')
        c = self.conn.cursor()
        self.sekretai = telepot.Bot(key)
        # self.sekretai.notifyOnMessage(self.handle_message)

        def handle(msg):
            self.handle_message(msg)

        telepot.loop.MessageLoop(self.sekretai, handle).run_as_thread()

    def log_message(self, msg):
        self.sekretai.sendMessage(manuel_id, pprint.pformat(msg))

    def handle_message(self, msg):
        user_id = msg['from']['id']
        try:
            msg_txt = msg['text']
            intent = msg['intent']
            target = msg['target']
        except KeyError:
            self.log_message("failed to parse the message")
            self.log_message(msg)
            return

        msg_txt = msg_txt.split(maxsplit=1)

    def handle_knowledge(self):
        pass

    def spin(self):
        while True:
            self.sekretai.sendMessage(manuel_id, "spinning")
            time.sleep(500)


if __name__ == "__main__":
    with open("api_key") as fin:
        bot = Secretary(fin.read()[:-1])
    bot.spin()
