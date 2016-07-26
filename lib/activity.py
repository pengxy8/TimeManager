# -*- coding: utf-8 -*-
# name
# place
# week str eg:0001011110000
# day_of_week int
# start_time int
# span int
# is_course bool
# user_id

from api import db
from pymongo import MongoClient
import rescode

def getAllActivities(user_id):
    one = db.activity.find({'user_id': user_id})
    return list(one)

def importSysuActivities(user, activities):
    db.activity.remove()
    for activity in activities:
        activity['user_id'] = user['_id']
        _id = db.activity.insert(activity)
        activity.pop('user_id')
        activity['_id'] = str(_id)
        activity['user_account'] = user['account']
    return activities

def insertActivity(activity):
    return db.activity.insert(activity)

def removeActivity(activity):
    return db.activity.remove(activity)

def updateActivity(activityWhere, activitySet):
    return db.activity.update(activityWhere, {'$set': activitySet})
