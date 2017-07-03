import pymongo
import util
import json


class gaia_db:
    def __init__(self):

        with open('DB_keys') as f:
            DBKEY = f.read()[:-1]

        self.uri = DBKEY
        self.client = pymongo.MongoClient(self.uri)
        self.db = self.client['gaia_database']
        try:
            self.db.create_collection(name='employees')
            print('\nCollection created\n')
        except pymongo.errors.CollectionInvalid:
            print('\nCollection exists\n')
        self.employees = {}
        self.working_at = {}
        self.emp = util.Employees()

    def get_db(self):
        return self.db

    def get_employees(self):
        return self.employees

    def get_working_at(self):
        return self.working_at

    def create_insert(self):
        self.employees, self.working_at = self.emp.create_person(self.employees, self.working_at)

    def insert(self, users):
        for u in users:
            try:
                self.db.employees.insert_one(users[u])
                print('Adding', u, '\n')
            except pymongo.errors.DuplicateKeyError:
                print('Employee', u, 'yet present\n')

    def remove(self, value):
        return self.db.employees.remove({'name': value}, 1)

    def find_name(self, value):
        return self.db.employees.find_one({'name': value})

    def find_job(self, value):
        return self.db.employees.find_one({'job': value})['name']

    def find_work(self, d):
        return d['working_on']

    def meeting(self, list_time_data, name):
        timedata = util.dateTime(list_time_data)
        util.scheduling(timedata, self.employees, name)  # change
        ## write on calendar


##############################################################################


def main():
    gaia = gaia_db()

    ### create fake employees ###
    employees, working_at = util.put_data()

    ### add employees to database ###
    gaia.insert(employees)

    ### query database for a job
    gaia.find_job('data_scientist')

    ### query database for employee ###
    george = gaia.find_name('george')
    norman = gaia.find_name('norman')
    manuel = gaia.find_name('manuel')

    print(george['name'], george['free_time']['2017']['6']['24'])
    print(norman['name'], norman['free_time']['2017']['6']['24'])
    print(manuel['name'], manuel['free_time']['2017']['6']['24'])
    print('\n')

    ### convert date ###
    timedata = util.dateTime(['2017-06-24', '20:00:00/22:00:00'])

    ### check if employee is free for a meeting at timedate ###
    util.scheduling(timedata, employees, 'norman')

    print('all done')


if __name__ == "__main__":
    main()
