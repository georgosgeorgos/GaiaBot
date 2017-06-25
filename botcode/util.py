import telepot
import time
import requests
import hashlib
import pprint
from time import gmtime, strftime
import json
import copy
import apiai

CLIENT_ACCESS_TOKEN = 'bbb35a4d419f48ee84ae9800be4768f6'


def question(q):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()

    request.query = q

    if request.query == "exit":
        return 0

    response = request.getresponse()

    string = response.read()
    string = string.decode("utf-8")

    string_j = json.loads(string)

    return string_j


def dateTime(date_time):
    '''
    handle different date formats
    
    '''

    # format ['2017-06-24', '12:00:00/16:00:00']

    if (len(date_time) == 2):
        date, time = date_time[0], date_time[1]
        year, month, day = date.split("-")

        start_time, end_time = time.split("/")
        hour, minute, second = start_time.split(":")

        start = {"date": {"year": year, "month": month, "day": day},
                 "time": {"hour": hour, "minute": minute, "second": second}}

        hour, minute, second = end_time.split(":")

        end = {"date": {"year": year, "month": month, "day": day},
               "time": {"hour": hour, "minute": minute, "second": second}}

        return {"start": start, "end": end}

    start = date_time[0].split("/")[0]

    # format ['2017-06-24']

    if (start == date_time[0] and len(date_time) == 1):

        year, month, day = start.split("-")
        hour, minute, second = "00", "00", "00"
        start = {"date": {"year": year, "month": month, "day": day},
                 "time": {"hour": hour, "minute": minute, "second": second}}
        end = {"date": {"year": year, "month": month, "day": day},
               "time": {"hour": hour, "minute": minute, "second": second}}


    # format

    else:

        date, time = start.split("T")
        year, month, day = date.split("-")

        hour, minute, second = time.split("Z")[0].split(":")

        start = {"date": {"year": year, "month": month, "day": day},
                 "time": {"hour": hour, "minute": minute, "second": second}}

        end = date_time[0].split("/")[1]
        date, time = end.split("T")
        year, month, day = date.split("-")
        hour, minute, second = time.split("Z")[0].split(":")

        end = {"date": {"year": year, "month": month, "day": day},
               "time": {"hour": hour, "minute": minute, "second": second}}

    return {"start": start, "end": end}


def scheduling(timedate, employees, name):
    '''
    timedate : date and time to check
    Amy : object with person data
    
    
    '''

    # select date and time unavailable

    year = str(timedate["start"]["date"]["year"])
    month = str(timedate["start"]["date"]["month"])
    if list(month)[0] == '0':
        month = "".join(list(month)[1])
    day = str(timedate["start"]["date"]["day"])

    work_time = employees[name]["free_time"][year][month][day]

    hour = timedate["start"]["time"]["hour"]
    minute = timedate["start"]["time"]["minute"]
    second = timedate["start"]["time"]["second"]
    s = hour + ":" + minute + ":" + second

    hour = timedate["end"]["time"]["hour"]
    minute = timedate["end"]["time"]["minute"]
    second = timedate["end"]["time"]["second"]
    e = hour + ":" + minute + ":" + second

    d = year + "/" + month + "/" + day

    c = True
    # check all the booker dates
    print(name, (s, e), d)
    print()
    for w_t in work_time:
        print("Unavailable periods:", w_t)

    print()
    for w_t in work_time:

        work_hour_start, work_minute_start, work_second_start = w_t[0].split(":")
        work_hour_end, work_minute_end, work_second_end = w_t[1].split(":")

        # check if the unavailable period intersect my request

        if timedate["start"]["time"]["hour"] > work_hour_start and timedate["end"]["time"]["hour"] < work_hour_end:
            c = False

        if timedate["start"]["time"]["hour"] == work_hour_end:

            if timedate["start"]["time"]["minute"] > work_minute_end:
                c = False
            else:
                print(name, "Available Soon")
                break

        if timedate["end"]["time"]["hour"] == work_hour_start:

            if timedate["end"]["time"]["minute"] < work_minute_start:
                c = False
            else:
                print(name, "Available but no delay")
                break

    if c == False:
        print("No available")
    else:
        print("Available")

    return (name, (s, e), d)


####################################################################################################

class Employees:
    def __init__(self):

        self.day = {str(i): list() for i in range(1, 32)}
        self.months = {str(i): copy.deepcopy(self.day) for i in range(1, 13)}
        self.date = {'2017': copy.deepcopy(self.months)}

        self.person = {'name': '', 'id': '', 'job': '', 'team': [], 'free_time': copy.deepcopy(self.date),
                       'mail': '', 'working_on': '', 'updates': 1, 'office': ''}

        # working_at={}
        # employees = {}

    def create_person(self, employees, working_at, name='', id='', job='', team=[], mail='', working_on='', updates=1,
                      office=''):

        # global working_at

        pers = {'name': '', 'id': '', 'job': '', 'team': [], 'free_time': copy.deepcopy(self.date),
                'mail': '', 'working_on': '', 'updates': 1, 'office': ''}

        pers['name'] = name
        pers['id'] = id
        pers['job'] = job
        pers['team'] = team
        pers['mail'] = mail
        pers['working_on'] = working_on
        pers['updates'] = 1
        pers['office'] = office

        if (working_on in working_at):
            working_at[working_on].append(name)
        else:
            working_at[working_on] = [name]

        employees[name] = copy.deepcopy(pers)

        return employees, working_at

    def insert_time(self, employees, person, year, month, day, time_start, time_end):

        employees[person]['free_time'][str(year)][str(month)][str(day)].append((str(time_start), str(time_end)))

        return employees

    def working_on(self, Person):
        return Person['working_on']


######################################################################################################

def put_data():
    working_at = {}
    employees = {}

    e = Employees()

    employees, working_at = e.create_person(employees, working_at, name='manuel', job='software_developer',
                                            id=184508683, team=['norman', 'george'], working_on='project_Y')
    employees = e.insert_time(employees, "manuel", 2017, 6, 24, '10:00:00', '12:00:00')

    employees, working_at = e.create_person(employees, working_at, name='george', job='data_scientist',
                                            team=['norman', 'manuel'],
                                            id=417193312, working_on='project_Y')
    employees = e.insert_time(employees, "george", 2017, 6, 24, '20:00:00', '22:00:00')

    employees, working_at = e.create_person(employees, working_at, name='norman', job='robotic_engineer',
                                            team=['george', 'manuel'],
                                            id=431333715, working_on='project_Y')
    employees = e.insert_time(employees, "norman", 2017, 6, 24, '18:00:00', '20:00:00')

    return employees


##########################################################################################################

# -*- coding: UTF-8 -*-

def time(data, employees, name):
    date_time = data["result"]["parameters"]["date-time"]

    timedate = dateTime(date_time)
    scheduling(timedate, employees, name)

    return None


def get_working_on(data, employees):
    parameters = data["result"]["parameters"]
    name = parameters['given-name']
    project = parameters['project']
    if name == '' and not project == '':
        return working_at[project]
    if not name == '' and project == '':
        return employees[name]['working_on']


def look_for_specialist(data, employees):
    parameters = data["result"]["parameters"]
    job = parameters['job']
    candidates = []
    for person in employees:
        if employees[person]['job'] == job:
            candidates.append(employees[person]['name'])
    # return candidates
    for cand in candidates:
        try_id = employees[cand]['id']
        wip_id = try_id
        waiting = 1
        print("ID da provare")
        print(try_id)
        print("persona che provo")
        print(employees[cand]['name'])

        list_id.append(try_id)
        print(list_id)

        self.sekretai.sendMessage(try_id, "Hello! Someone needs your assistance. Are you available?")
        print("messaggio inviato")


def place(data, employees):
    parameters = data["result"]["parameters"]
    name = parameters['given-name']
    return employees[name]['office']


def action_node(action, data, employees, name):
    if action == 'working_on':
        return get_working_on(data, employees)
    if action == 'look_for_specialist':
        return look_for_specialist(data, employees)
    if action == 'place':
        return place(data, employees)
    if action == 'check_free_time':
        return time(data, employees, name)
    else:
        return None


        # while(1):
        #    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        #    request = ai.text_request()
        #    request.query = input("Type here")
        #    if request.query == "exit":
        #        break
        #    response = request.getresponse()
        #    reply = response.read()
        #    parsed_json = json.loads(reply)
        #    action=parsed_json['result']['action']
        #    parameters=parsed_json['result']['parameters']
        #    response=parsed_json['result']['fulfillment']['speech']
        #    print(response)
        #    print(action_node(action,parameters))
