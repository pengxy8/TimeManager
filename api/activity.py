# -*- coding=utf-8 -*-
# name
# place
# week
# day_of_week int
# start_time int
# span int
# iscourse bool
# user_id

from flask import g,request,jsonify,Response,session
from flask.ext.login import login_required
from api import app
import rescode
import requests

@app.route('/activity/update',methods=['GET','POST'])
def updateActivities():
    if request.method == 'GET':
        from lib import sysuGetCodeImg
        rep = sysuGetCodeImg()
        session['cookies'] = requests.utils.dict_from_cookiejar(rep.cookies)
        return Response(rep.content,
                mimetype='image/jpeg')
    else:
        if g.user is None:
            print 'user not login'
            return jsonify(rescode = rescode.USER_NOT_LOGIN)
        elif not g.user['binded']:
            print 'user not binded'
            return jsonify(rescode = rescode.USER_NOT_BINDED)
        form = request.form
        needs = ['code', 'year', 'term']
        for need in needs:
            if need not in form:
                print 'format error'
                return jsonify(rescode = rescode.FORMAT_ERROR)
        from lib import sysuLogin,sysuCheckLogin
        from lib import sysuGetSchedule
        from lib import formatSchedule
        rep = sysuLogin(session['cookies'],
                g.user['student_id'],
                g.user['student_pwd'],
                form['code'])
        session['cookies']['sno'] = g.user['student_id']
        if not sysuCheckLogin(session['cookies']):
            print 'user binded error'
            return jsonify(rescode=rescode.USER_BINDED_ERROR)
        html = sysuGetSchedule(session['cookies'],
                form['year'],
                form['term'])
        print html
        activities = formatSchedule(html)
        print activities
        from lib import importSysuActivities
        importSysuActivities(g.user,activities)
        print 'success'
        return jsonify(rescode = rescode.SUCCESS, activity = activities)

@app.route('/activity/add', methods = ['POST'])
def addActivity():
    if g.user is None:
        return jsonify(rescode = rescode.USER_NOT_LOGIN)
    form = request.form
    print form
    activity = {'user_id': g.user['_id'], 'is_course': False}
    needs = ['name', 'place', 'week', 'day_of_week', 'start_time', 'span']
    for need in needs:
        if need in form:
            activity[need] = form[need]
        else:
            return jsonify(rescode = rescode.FORMAT_ERROR)
    from lib import insertActivity
    activity_id = str(insertActivity(activity))
    return jsonify(rescode = rescode.SUCCESS, activity_id = activity_id)

@app.route('/activity/delete/<activity_id>')
def deleteActivity(activity_id=None):
    if not activity_id:
        return jsonify(rescode = rescode.FORMAT_ERROR)
    if g.user is None:
        return jsonify(rescode = rescode.USER_NOT_LOGIN)
    from bson import ObjectId
    activity = {'_id': ObjectId(activity_id)}
    from lib import removeActivity
    msg = removeActivity(activity)
    if msg['n']:
        return jsonify(rescode = rescode.SUCCESS)
    else:
        return jsonify(rescode = rescode.ACTIVITY_NOT_EXIST)

@app.route('/activity/edit/<activity_id>', methods = ['POST'])
def editActivity(activity_id=None):
    if not activity_id:
        print 'FORMAT_ERROR'
        return jsonify(rescode = rescode.FORMAT_ERROR)
    if g.user is None:
        print 'USER_NOT_LOGIN'
        return jsonify(rescode = rescode.USER_NOT_LOGIN)
    from bson import ObjectId
    activityWhere = {'_id': ObjectId(activity_id)}
    form = request.form
    print form
    print form['place']
    activitySet = {}
    needs = ['name', 'place', 'week', 'day_of_week', 'start_time', 'span', 'is_course']
    for need in needs:
        if need in form:
            activitySet[need] = form[need]
    from lib import updateActivity
    msg = updateActivity(activityWhere, activitySet)
    if msg['updatedExisting']:
        print 'SUCCESS'
        return jsonify(rescode = rescode.SUCCESS)
    else:
        print 'ACTIVITY_NOT_EXIST'
        return jsonify(rescode = rescode.ACTIVITY_NOT_EXIST)
