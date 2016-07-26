# -*- coding=utf-8 -*-
class User:
    '''
    用户类，用于flask-login
    '''
    def __init__(self,user):
        self.user=user
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return unicode(self.user['_id'])
