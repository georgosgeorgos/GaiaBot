# -*- coding: UTF-8 -*-
import sqliteshelve
import pprint
import sqlite3
import time

import telepot
import telepot.loop

MANUEL_ID = 45571984
CLIENT_ACCESS_TOKEN = 'bbb35a4d419f48ee84ae9800be4768f6'


class Secretary(object):
    def __init__(self, key, db):
        self.db = db
        self.sekretai = telepot.Bot(key)
        self.sekretai.notifyOnMessage(self.handle_message)

        def handle(msg):
            self.handle_message(msg)

        self.expected_answers = {}
        telepot.loop.MessageLoop(self.sekretai, handle).run_as_thread()

    def place(self, parameters):
        name = parameters['given-name']
        return self.db[name]['office']

    def log_message(self, msg):
        self.sekretai.sendMessage(MANUEL_ID, pprint.pformat(msg))

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

    def handle_message(self, msg):
        user_id = msg['from']['id']
        user = self.whosdisguy(user_id)

        if user_id in self.expected_answers:
            return self.expected_answers[user_id](msg)
        try:
            msg_txt = msg['text']
        except KeyError:
            self.log_message("failed to parse the message")
            self.log_message(msg)
            self.sendMessage(user_id, "i failed to understand that; admin noticed")
            return

        parameters, action, response = self.analyze_request(msg_txt)
        self.sendMessage(user_id, response)

        if action == "input.unknown":
            return

        elif action == 'working_on':
            response = get_working_on(parameters)
            self.sendMessage(user_id, response)

        elif action == 'look_for_specialist':
            found_specialist = self.look_for_specialist(parameters, querier=user['name'])
            if found_specialist:
                self.sendMessage(user_id, "{0} is available.".format(found_specialist))
            else:
                self.sendMessage(user_id, "I'm sorry, I didn't find any good match.")

        elif action == 'place':
            place_id = place(parameters)
            self.sendMessage(user_id, "The office is: {}".format(place_id))

        elif action == 'booking':
            asker_name = user['name']
            team = user['team']
            booking_time = ":".join(parameters['time'].split(":")[:-1])

            for other_user_key in team:
                his_name = employee[other_user_key]['name']
                was_he_avail, last_id = self.query_employee(last_id, other_user_key,
                                                            query_msg="Hello {}, are you available at {} for a meeting organized by {}?".format(
                                                                his_name, booking_time, asker_name))
                if not was_he_avail:
                    return
            booking_time = parameters['time'].split(":")
            # add days
            booking_time[1] = str(min(59, int(booking_time[1]) + 25))
            booking_time = ":".join(booking_time[:-1])

            agreed, last_id = self.query_employee(last_id, asker_name,
                                                  query_msg="{} was not available. Do you want to reschedule the meeting to {}?".format(
                                                      other_user_key, booking_time))
            rspmsg = "The meeting was successfully organized, Room 3141 is booked for you at that time."
            for other_user_key in team:
                was_he_avail, last_id = self.query_employee(last_id, other_user_key, "what about meeting at {}?".format(booking_time))
                if not was_he_avail:
                    rspmsg = "{} is not available at {}, please suggest another time.".format(other_user_key,
                                                                                              booking_time, )
                    break
            self.sendMessage(user_id, rspmsg)
            for other_user_key in team:
                self.sendMessage(self.employee[other_user_key]['id'], rspmsg)
        else:
            print("skipping", action)

    def sendMessage(self, user_id, message):
        self.sendMessage(user_id, message)

    def handle_knowledge(self):
        pass

    def spin(self):
        while True:
            self.sekretai.sendMessage(MANUEL_ID, "spinning")
            time.sleep(500)

    def whosdisguy(self, guy_id):
        for user in self.employee.values():
            if user['id'] == str(guy_id):
                return user


def working_on(Person):
    return Person['working_on']


def get_working_on(parameters):
    name = parameters['given-name']
    project = parameters['project']
    if name == '' and not project == '':
        return working_at[project]
    if not name == '' and project == '':
        return employee[name]['working_on']


def look_for_specialist(bot_obj, message_offset_id, params, querier=None):
    job = params['job']
    found = False
    for person in employee:
        if employee[person]['job'] == job:
            found, message_offset_id = query_employee(message_offset_id, person, bot_obj)
    if not found and querier:
        for person in employee:
            is_allowed = employee[querier]['office'] < employee[person]['office']
            if person == job:
                if is_allowed:
                    found, message_offset_id = query_employee(message_offset_id, person, bot_obj)
                else:
                    bot_obj.sendMessage(employee[querier]['id'], "I'm sorry {}, i cannot let you do that".format(asker_name))

    return message_offset_id, found


def query_employee(message_offset_id, person, bot_obj, query_msg=None):
    his_answer = False
    emp = employee[person]['name']
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[[
            KeyboardButton(text="yes", callback_data="yes"),
            KeyboardButton(text="no", callback_data="no")
        ], ])
    if not query_msg:
        query_msg = "{} needs a {}. Are you available?".format("Carl", employee[person]['job'])
    bot_obj.sendMessage(employee[person]['id'], query_msg, reply_markup=keyboard)
    employee_answer, message_offset_id = get_one_message(message_offset_id)

    if "callback_query" in employee_answer:
        markup = ReplyKeyboardRemove()
        bot_obj.sendMessage(employee[person]['id'], "Ok, got it", reply_markup=markup)
        if employee_answer["callback_query"]["data"] == "yes":y
            his_answer = emp
    else:
        _, action_type, _ = analyze_request(bot_obj, employee_answer['message']['text'])
        if action_type == "affermative":
            his_answer = emp
    return his_answer, message_offset_id



def analyze_request(bot, msg_txt):


if __name__ == "__main__":
    with open("api_key") as fin:
        key = fin.read()[:-1]
    db = sqlite3.connect('database.sqlite')
    bot = Secretary(key, db)
    try:
        bot.spin()
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
