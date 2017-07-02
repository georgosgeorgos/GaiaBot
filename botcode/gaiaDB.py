import pymongo
import sys
import json
import importlib
import util; importlib.reload(util)


class gaiaDB:
    
    def __init__(self):

        with open("DB_keys") as f:
            DBKEY = f.read()
        
        self.uri = DBKEY
        self.client = pymongo.MongoClient(self.uri)
        self.db = client['gaia_database']
        try:
            self.db.create_collection(name='employees')
        except:
            None
        self.employees = {}
        #self.employees = util.put_data()
        self.working_at = {}
        self.emp = Employees()
        
    def get_employees(self):
        return self.employees
    
    def get_working_at(self):
        return self.working_at
        
    def gaia_create_insert(self):
        self.employees, self.working_at = self.emp.create_person(self.employees, self.working_at)
           
    def gaia_insert(self, users):
        for u in users:
            try:
                self.db.employees.insert_one(users[u])
                print("Adding", u)
            except:
                continue
        
                
    def gaia_remove(self, value):
        return self.db.employees.remove({'name': value}, 1)
                
    def gaia_find_name(self, value):
        return self.db.employees.find_one({'name': value})
    
    def gaia_find_job(self, value):
        return self.db.employees.find_one({'job': value})['name']
    
    def gaia_find_work(self, d):
        return d['working_on']
    
    def gaia_meeting(self, list_time_data, name):
        timedata = util.dateTime(list_time_data)
        util.scheduling(timedata, self.employees, name)  # change
        ## write on calendar





gaia_db = gaiaDB()

users, working_at = util.put_data()

gaia_db.gaia_insert(users)


gaia_db.gaia_find_job("data_scientist")


george = db.employees.find_one({'name': 'george'})
norman = db.employees.find_one({'name': 'norman'})
manuel = db.employees.find_one({'name': 'manuel'})

george["free_time"]["2017"]["6"]["24"]
norman["free_time"]["2017"]["6"]["24"]
manuel["free_time"]["2017"]["6"]["24"]


timedata = util.dateTime(['2017-06-24', '20:00:00/22:00:00'])

util.scheduling(timedata, employees, 'norman')