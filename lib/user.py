# -*- coding: utf-8 -*-
# account
# password
# nickname
# mail
# binded bool
# student_id
# student_pwd
# active bool

from api import db
from pymongo import MongoClient
import rescode

# for login
def checkForLogin(account, password):
    one = db.user.find_one({'account': account})
    if one == None:
        return rescode.USER_NOT_EXIST
    if one['password'] != password:
        return rescode.USER_NOT_MATCH
    if 'active' in one and one['active'] == False:
        return rescode.USER_NOT_ACTIVE
    return rescode.USER_MATCH

def getUserInfo(account):
    one = db.user.find_one({'account': account})
    return one

def getUserById(_id):
    one = db.user.find_one({'_id': _id})
    return one


# for register
def checkDuplicateUser(account):
    one = db.user.find_one({'account': account})
    return one == None

def checkDuplicateMail(mail):
    one = db.user.find_one({'mail': mail})
    return one == None

def addUser(user):
    user['active'] = False
    user['binded'] = bool(user['binded'])
    return db.user.insert(user)

def removeUser(user):
    return db.user.remove(user)

def activeUser(account, code):
    # import rsa
    # from config import PRIVKEY
    from lib import md5
    one = db.user.find_one({'account': account})
    if one == None:
        return False
    # elif md5(str(one['_id'])) != rsa.decrypt(code, PRIVKEY):
    elif md5(str(one['_id'])) != code:
        return False
    else:
        db.user.update({'account': account}, {'$set':{'active': True}})
        return True


def updateUser(userWhere, userSet):
    return db.user.update(userWhere,{'$set': userSet})
