# -*- coding: UTF-8 -*-
import pprint
import time
import json

from telepot.delegate import per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

import gaiaDB

import telepot
import telepot.loop

MANUEL_ID = 45571984
CLIENT_ACCESS_TOKEN = 'bbb35a4d419f48ee84ae9800be4768f6'



class MessageCounter(telepot.helper.ChatHandler):

class Secretary(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Secretary, self).__init__(seed_tuple, timeout)
        self.db = gaiaDB.gaia_db()

        # def handle(msg):
        #     self.handle_message(msg)

        self.user_handler = {}
        self.user_answer = {}
        # telepot.loop.MessageLoop(self.bot, handle).run_as_thread()

    def log_message(self, msg):
        self.bot.sendMessage(MANUEL_ID, pprint.pformat(msg))

    def analyze_request(self, msg_txt):
        ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        request = ai.text_request()
        request.query = msg_txt
        response = request.getresponse()
        reply = response.read()
        reply = reply.decode("utf-8")
        parsed_json = json.loads(reply)
        action = parsed_json['result']['action']
        parameters = parsed_json['result']['parameters']
        response = parsed_json['result']['fulfillment']['speech']
        return parameters, action, response

    def on_message(self, msg):
        message_user_tid = msg['from']['id']
        user = self.db.find_by_tid(message_user_tid)

        if user['tid'] in self.user_handler:
            return self.user_handler[user['tid']](msg)

        try:
            msg_txt = msg['text']
        except KeyError:
            self.log_message("failed to parse the message")
            self.log_message(msg)
            self.bot.sendMessage(user['tid'], "i failed to understand that; admin noticed")
            return

        parameters, action, response = self.analyze_request(msg_txt)
        self.bot.sendMessage(user['tid'], response)

        if action == 'look_for_specialist':
            found_specialist = self.look_for_specialist(parameters['job'], querier=user['name'])
            if found_specialist:
                self.bot.sendMessage(user['tid'], "{0} is available.".format(found_specialist))
            else:
                self.bot.sendMessage(user['tid'], "I'm sorry, I didn't find any good match.")
        else:
            print("skipping", action)

    def look_for_specialist(self, job_title, querier):
        found = False
        for employee in self.db.find_by_job(job_title):
            found = self.query_employee(querier, employee)
            if found:
                break
        return found

    def query_employee(self, querier, employee, query_msg=None):
        his_answer = False

        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=[[
                KeyboardButton(text="yes", callback_data="yes"),
                KeyboardButton(text="no", callback_data="no")
            ], ])

        if not query_msg:
            query_msg = "{} needs a {}. Are you available?".format(querier['name'], employee['job'])

        def query_response_handler(msg):
            markup = ReplyKeyboardRemove()
            employee_id = msg['from']['id']
            self.bot.sendMessage(employee_id, "Ok, got it", reply_markup=markup)
            _, action_type, _ = self.analyze_request(msg["text"])

            # TODO: handle callback from keyboard button
            if msg["text"] == "yes" or action_type == "affermative":
                # change employee status
                employee_answer = "yes"
            else:
                # TODO: handle random answers
                employee_answer = "false"

            self.user_answer[employee_id][querier['id']] = employee_answer
            del self.user_handler[employee['tid']]

        self.user_handler[employee['tid']] = query_response_handler
        self.bot.sendMessage(employee['tid'], query_msg, reply_markup=keyboard)

        while self.user_handler[employee['tid']] is not None:
            time.sleep(1)

        his_answer = self.user_answer[employee['tid']][querier['id']]
        del self.user_answer[employee['tid']][querier['id']]
        return his_answer


if __name__ == "__main__":
    with open("api_key") as fin:
        KEY = fin.read()[:-1]

    bot = telepot.DelegatorBot(KEY, [
        (per_chat_id(), create_open(Secretary, timeout=9999999)),
    ])
    bot.notifyOnMessage(run_forever=True)
