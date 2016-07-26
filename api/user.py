# -*- coding=utf-8 -*-
from flask import g,request,jsonify
from flask.ext.login import current_user,logout_user,login_required,login_user
from api import app,lm
import rescode

@lm.user_loader
def load_user(id):
    from model import User
    from lib import getUserById
    from bson import ObjectId
    return User(getUserById(ObjectId(id)))

@app.before_request
def before_request():
    g.user = None
    if hasattr(current_user,'user'):
        g.user = current_user.user

@app.route('/user/logout')
def logout():
    logout_user()
    return jsonify(rescode=rescode.SUCCESS)

@app.route('/user/login', methods=['POST'])
def login():
    form = request.form
    needs = ['account', 'password']
    for need in needs:
        if need not in form and form[need].strip() != '':
            return jsonify(rescode=rescode.FORMAT_ERROR)
    account = form['account']
    pwd = form['password']
    from lib import checkForLogin,getUserInfo
    res = checkForLogin(account, pwd)
    if res == rescode.USER_MATCH:
        from model import User
        login_user(User(getUserInfo(account)))
        print('success')
        return jsonify(rescode=rescode.USER_MATCH)
    elif res == rescode.USER_NOT_EXIST:
        print('not exist')
        return jsonify(rescode=rescode.USER_NOT_EXIST)
    elif res == rescode.USER_NOT_ACTIVE:
        print('not active')
        return jsonify(rescode=rescode.USER_NOT_ACTIVE)
    elif res == rescode.USER_NOT_MATCH:
        print('password error')
        return jsonify(rescode=rescode.USER_NOT_MATCH)

@app.route('/user/register', methods=['POST'])
def register():
    form = request.form
    print form['account']
    needs = ['account', 'password', 'nickname', 'mail']
    if 'binded' in form and form['binded'].strip() != '':
        needs.append('student_id')
        needs.append('student_pwd')
    for need in needs:
        if need not in form and form[need].strip() != '':
            return jsonify(rescode=rescode.FORMAT_ERROR)
    account = form['account']
    mail = form['mail']
    nickname = form['nickname']
    from lib import checkDuplicateUser
    from lib import checkDuplicateMail
    from lib import addUser,sendMail
    if not checkDuplicateUser(account):
        return jsonify(rescode=rescode.USER_EXIST)
    if not checkDuplicateMail(mail):
        return jsonify(rescode=rescode.USER_MAIL_EXIST)
    user_id = addUser(form.to_dict())

    if not sendMail(str(user_id), account, nickname, mail):
        from lib import removeUser
        removeUser({'account': form['account']})
        return jsonify(rescode=rescode.MAIL_FORMAT_ERROR)

    return jsonify(rescode=rescode.REGISTER_SUCCESS)

@app.route('/user/activate')
def activate():
    args = request.args
    if 'a' not in args or 'c' not in args:
        return '404'
    from lib import activeUser
    res = activeUser(args['a'],args['c'])
    if res:
        return u'你已成功激活，请返回手机登陆'
    else:
        return u'激活失败'

@app.route('/user/getinfo')
#@login_required
def userInfo():
    if g.user is None:
        return jsonify(rescode=rescode.USER_NOT_LOGIN)
    from lib import getUserById,getAllActivities
    user = getUserById(g.user['_id'])
    user.pop('_id')
    user.pop('account')
    user.pop('password')
    activity = getAllActivities(g.user['_id'])
    for one in activity:
        one['_id'] = str(one['_id'])
        one.pop('user_id')
        one['user_account'] = g.user['account']
    print user
    print activity
    return jsonify(rescode=rescode.SUCCESS,user=user,activity=activity)

@app.route('/user/edit', methods = ['POST'])
def editUser():
    if g.user is None:
        return jsonify(rescode = rescode.USER_NOT_LOGIN)
    form = request.form
    userWhere = {'_id': g.user['_id']}
    userSet = {}
    needs = ['password', 'nickname', 'binded', 'student_id', 'student_pwd']
    for need in needs:
        if need in form:
            userSet[need] = form[need]
    from lib import updateUser
    msg = updateUser(userWhere, userSet)
    if msg['updatedExisting']:
        return jsonify(rescode = rescode.SUCCESS)
    else:
        return jsonify(rescode = rescode.USER_NOT_EXIST)
