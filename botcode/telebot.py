# -*- coding: UTF-8 -*-
import pprint
import time
import apiai
import json

from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from collections import defaultdict

import gaiaDB

import telepot
import telepot.loop

MANUEL_ID = 45571984
CLIENT_ACCESS_TOKEN = 'bbb35a4d419f48ee84ae9800be4768f6'

user_handler = {}
user_answer = defaultdict(dict)


class Secretary(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Secretary, self).__init__(*args, **kwargs)
        self.db = gaiaDB.gaia_db()

        # def handle(msg):
        #     self.handle_message(msg)

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
        global user_handler

        ### new part ###

        message_user_tid = msg['from']['id']
        update_id = msg['message_id']
        user = self.db.find_by_tid(message_user_tid)

        if user == None: # if user is a new user
            self.bot.sendMessage(message_user_tid, "Hi! You are a new employee...nice to meet you!")
            self.bot.sendMessage(message_user_tid, "tell me something about you")

            # TODO: replace 4 different fucntions with a signle parametric one
            def handle_user_email(msg):
                message_user_tid = msg['from']['id']
                user['job'] = msg['text']
                user = self.db.create(message_user_tid)
                del user_handler[message_user_tid]
                bot.sendMessage(message_user_tid, "registered!")

            def handle_user_job(msg):
                message_user_tid = msg['from']['id']
                user = self.db.find_by_tid(message_user_tid)
                user['job'] = msg['text']
                user_handler[message_user_tid] = handle_user_email
                bot.sendMessage(message_user_tid, "your email:")

            def handle_user_rename(msg):
                message_user_tid = msg['from']['id']
                user = self.db.find_by_tid(message_user_tid)
                user['name'] = msg['text']
                self.db.update(user)
                user_handler[message_user_tid] = handle_user_job
                bot.sendMessage(message_user_tid, "your job title:")

            user_handler[message_user_tid] = handle_user_rename
            self.db.employees.insert_one({'tid': message_user_tid})
            bot.sendMessage(message_user_tid, "what's your name")


        elif user['tid'] in user_handler:
            print(user['name'], "was redirected by handler")
            return user_handler[user['tid']](msg)

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
            specialists_found = self.look_for_specialist(parameters['job'], querier=user)
            if specialists_found:
                self.bot.sendMessage(user['tid'], "{0} is/are available.".format(",".join(sp['name'] for sp in specialists_found)))
            else:
                self.bot.sendMessage(user['tid'], "I'm sorry, I didn't find any good match.")
        else:
            print("skipping", action)

    def look_for_specialist(self, job_title, querier):
        employees = []
        for employee in self.db.find_by_job(job_title):
            found = self.query_employee(querier, employee)
            if found:
                employees.append(employee)
                break
        return employees

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

            global user_answer
            user_answer[employee_id][querier['tid']] = employee_answer
            del user_handler[employee['tid']]

        while querier['tid'] in user_answer[employee['tid']]:
            print("you are asking too many questions fucktard")
            time.sleep(1)

        try:
            user_answer[employee['tid']][querier['tid']] = ""
        except KeyError:
            user_answer[employee['tid']] = {querier['tid']: ""}

        user_handler[employee['tid']] = query_response_handler
        self.bot.sendMessage(employee['tid'], query_msg, reply_markup=keyboard)

        while employee['tid'] in user_handler:
            print("querier sleeping")
            time.sleep(1)

        his_answer = user_answer[employee['tid']][querier['tid']]
        del user_answer[employee['tid']][querier['tid']]
        return his_answer == "yes"


if __name__ == "__main__":
    with open("api_key") as fin:
        KEY = fin.read()[:-1]

    bot = telepot.DelegatorBot(KEY, [
        pave_event_space()(
            per_chat_id(), create_open, Secretary, timeout=99999),
    ])
    MessageLoop(bot).run_forever()
