#! -*- coding: utf-8 -*-

def md5(str):
    import hashlib
    m = hashlib.md5()   
    m.update(str)
    return m.hexdigest()

def mySortKey(item):
    return item['span']

def sysuGetCodeImg():
    import requests
    from config import SYSU_IMG
    return requests.get(SYSU_IMG)

def sysuLogin(cookies,student_id,student_pwd,code):
    from config import SYSU_LOGIN,SYSU_PUBKEY
    import rsa
    import binascii
    import requests
    rawpwd = rsa.encrypt(md5(student_pwd).upper(),SYSU_PUBKEY)
    #返回的二进制数据的十六进制表示。每一个字节的数据转换成相应的2位十六进制表示
    pwd = binascii.b2a_hex(rawpwd)
    data = {'username': student_id, 'password': pwd, 'captcha': code}
    response = requests.post(url=SYSU_LOGIN, data=data, cookies=cookies)
    return response

def sysuCheckLogin(cookies):
    import requests
    from config import SYSU_GET_TABLE
    response = requests.get(url=SYSU_GET_TABLE, cookies=cookies, params = {'term': '', 'year': ''}, allow_redirects=False)
    return response.text != u'Empty'

def sysuGetSchedule(cookies,year,term):
    import requests
    from config import SYSU_GET_TABLE
    data = {'year': year, 'term': term}
    response = requests.get(url=SYSU_GET_TABLE, params=data, cookies = cookies)
    return response.text

def formatSchedule(s):
    import re
    from config import WEEK_NUM as WEEK
    #下面是用来标记节数
    week_num=7;
    week=[0 for i in range(week_num+1)]
    trs=re.findall("<tr.*?</tr>",s) #读取所有的节数信息
    i=0
    flag=0;
    trigger=0
    course_info=[] #存储这张课表上的所有的课程信息
    for tr in trs[1:]:
        i=i+1
        tds=re.findall("<td.*?</td>",tr) #匹配出每一行的所有的td
        bias=-1
        tmp_count=0;
        for td in tds[1:]:
            items=re.findall(">(.*?)<",td) #匹配出td中的所有内容
            bias=bias+1
            while week[bias]>0:
                bias=bias+1
            if len(items)<2:
                continue
            #大于2说明存放的是课程信息
            course={}.fromkeys(('name','place','week','day_of_week','start_time','span','is_course'))
            course['name']=items[0]
            course['place']=items[1]
            #下面是处理week信息
            week_strs=re.findall(u"(\d*-\d*)周",td)
            week_infos=re.findall("\d*",week_strs[0])
            s=''
            for i in range(1,int(week_infos[0])):
                s=s+'0'
            for i in range(int(week_infos[0]),int(week_infos[2])+1):
                s=s+'1'
            for i in range(int(week_infos[2])+1,WEEK+1):
                s=s+'0'
            course['week'] = s
            #下面是处理节数信息
            blocks=re.findall(u"(\d*-\d*)节",td)
            block_infos=re.findall("\d*",blocks[0])
            course['start_time']=int(block_infos[0])
            course['span']=int(block_infos[2])-int(block_infos[0])+1
            #是否是课程 是
            course['is_course']=True
            #下面处理星期问题
            if trigger==1:
                while (week[bias]>0):
                    bias=bias+1;
                course['day_of_week']=bias+1
                week[bias]=course['span']
            else:
                flag=1
                course['day_of_week']=bias+1
                week[bias]=course['span']
            #insert
            course_info.append(course)
            #debug
        for j in range(week_num):
            if week[j]>0:
                week[j]=week[j]-1
        if flag==1:
            trigger=1
    course_info.sort(key=mySortKey)
    return course_info

def sendMail(user_id, account, nickname, mail):
    from email.mime.text import MIMEText
    import smtplib
    import email.utils
    # import rsa
    from config import ADMIN_MAIL,URL# ,PUBKEY
    from lib import md5
    # msg = MIMEText(URL % (account,rsa.encrypt(md5(user_id), PUBKEY)))
    msg = MIMEText(URL % (account,md5(user_id)))
    msg['From'] = email.utils.formataddr(('TA is handsome', ADMIN_MAIL))
    msg['To'] = email.utils.formataddr((nickname, mail))
    msg['Subject'] = u'时间规划局帐号激活官方邮件'
    server = smtplib.SMTP('localhost')
    server.starttls()
    try:
        server.sendmail(ADMIN_MAIL, [mail], msg.as_string())
        return True
    except:
        return False
