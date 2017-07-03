# -*- coding: UTF-8 -*-
import copy
import json
import time

import apiai
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from telepot.namedtuple import ReplyKeyboardRemove

CLIENT_ACCESS_TOKEN = 'bbb35a4d419f48ee84ae9800be4768f6'


def create_person(working_at, employee, name='', job='', team=[], mail='', working_on='', updates=1, office='', id=''):
    month = {str(m): {str(d): list() for d in range(1, 32)} for m in range(1, 13)}
    date = {'2017': copy.deepcopy(month)}
    Person = {'name': '', 'id': id, 'job': '', 'team': [], 'free_time': copy.deepcopy(date), 'mail': '',
              'working_on': '', 'updates': 1, 'office': ''}
    pers = copy.deepcopy(Person)
    pers['name'] = name
    pers['job'] = job
    pers['team'] = team
    pers['mail'] = mail
    pers['working_on'] = working_on
    pers['updates'] = 1
    pers['office'] = office
    pers['id'] = id
    if working_on in working_at:
        working_at[working_on].append(name)
    else:
        working_at[working_on] = [name]

    employee[name] = copy.deepcopy(pers)
    return working_at, employee, pers
def insert_time(person, year, month, day, time_start, time_end):
    person['free_time'][str(year)][str(month)][str(day)].append((str(time_start), str(time_end)))
def query_DB():
    working_at = {}
    employee = {}
    working_at, employee, Amy = create_person(working_at, employee, 'Amy', 'developer', ['Carl', 'Marc'],
                                              working_on='project Turing', office="4C", id='45571984')
    insert_time(Amy, 2017, 6, 28, '10:00:00', '12:00:00')
    working_at, employee, _ = create_person(working_at, employee, 'Carl', 'designer', ['Amy', 'Marc'],
                                            working_on='project Fermi', office="00", id='173644279')
    working_at, employee, _ = create_person(working_at, employee, 'Marc', 'data scientist', id='184508683',
                                            team=['Amy', 'Carl'], office="31")
    # working_at, employee, _ = create_person(working_at, employee, 'Kinker', 'professional API user', team=['Amy',
    # 'Carl', 'Marc'], working_on='project Y', office="05", id='435992141')
    return employee, working_at


employee, working_at = query_DB()


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
        if employee_answer["callback_query"]["data"] == "yes":
            his_answer = emp
    else:
        _, action_type, _ = analyze_request(bot_obj, employee_answer['message']['text'])
        if action_type == "affermative":
            his_answer = emp
    return his_answer, message_offset_id


def place(parameters):
    name = parameters['given-name']
    return employee[name]['office']


def get_one_message(offset):
    new_msgs = []
    while not new_msgs:
        new_msgs = sekretai.getUpdates(offset=offset + 1)
        time.sleep(0.5)
    if len(new_msgs) > 1:
        print("DROPPING")
    return new_msgs[-1], int(new_msgs[-1]['update_id'])


def analyze_request(bot, msg_txt):
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


manuel_id = 184508683  # norman

with open("api_key.txt") as fin:
    key = fin.read()[:-1]

sekretai = telepot.Bot(key)

last_id = -2


def whosdisguy(guy_id):
    for person in employee:
        if employee[person]['id'] == str(guy_id):
            return employee[person]


while True:
    msg, last_id = get_one_message(last_id)
    parameters, action, response = analyze_request(sekretai, msg['message']['text'])

    if response:
        sekretai.sendMessage(msg['message']['from']['id'], response)
    if action == "input.unknown":
        continue
    elif action == 'working_on':
        response = get_working_on(parameters)
        sekretai.sendMessage(msg['message']['from']['id'], str(response))
    elif action == 'look_for_specialist':
        asker_tid = msg['message']['from']['id']
        asker_name = whosdisguy(asker_tid)['name']

        last_id, result = look_for_specialist(sekretai, last_id, parameters, querier=asker_name)
        if result:
            sekretai.sendMessage(msg['message']['from']['id'], str(result) + " is available.")
        else:
            sekretai.sendMessage(msg['message']['from']['id'], "I'm sorry, I didn't find any good match.")
    elif action == 'place':
        place_id = place(parameters)
        sekretai.sendMessage(msg['message']['from']['id'], "The office is: {}".format(place_id))
    elif action == 'booking':
        asker_tid = msg['message']['from']['id']
        asker_name = whosdisguy(asker_tid)['name']
        team = employee[asker_name]['team']
        booking_time = ":".join(parameters['time'].split(":")[:-1])
        for other_employee in team:
            his_name = employee[other_employee]['name']
            was_he_avail, last_id = query_employee(last_id, other_employee, sekretai,
                                                   query_msg="Hello {}, are you available at {} for a meeting organized by {}?".format(
                                                       his_name, booking_time, asker_name))
            if not was_he_avail:
                break
        booking_time = parameters['time'].split(":")
        # add days
        booking_time[1] = str(min(59, int(booking_time[1]) + 25))
        booking_time = ":".join(booking_time[:-1])

        agreed, last_id = query_employee(last_id, asker_name, sekretai,
                                         query_msg="{} was not available. Do you want to reschedule the meeting to {}?".format(other_employee, booking_time))
        rspmsg = "The meeting was successfully organized, Room 3141 is booked for you at that time."
        for other_employee in team:
            was_he_avail, last_id = query_employee(last_id, other_employee, sekretai,
                                                   "what about meeting at {}?".format(booking_time))
            if not was_he_avail:
                rspmsg = "{} is not available at {}, please suggest another time.".format(other_employee, booking_time,)
                break
        sekretai.sendMessage(asker_tid, rspmsg)
        for other_employee in team:
            sekretai.sendMessage(employee[other_employee]['id'], rspmsg)
    else:
        print("skipping", action)
