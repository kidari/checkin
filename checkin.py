# -*- coding: UTF-8 -*-
import requests,base64,json,hashlib
from Crypto.Cipher import AES
import os, re,time,smtplib
from email.mime.text import MIMEText
from email.header import Header
def encrypt(key, text):
    cryptor = AES.new(key.encode('utf8'), AES.MODE_CBC, b'0102030405060708')
    length = 16                    
    count = len(text.encode('utf-8'))     
    if (count % length != 0):
        add = length - (count % length)
    else:
        add = 16             
    pad = chr(add)
    text1 = text + (pad * add)    
    ciphertext = cryptor.encrypt(text1.encode('utf8'))          
    cryptedStr = str(base64.b64encode(ciphertext),encoding='utf-8')
    return cryptedStr
def md5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()
def protect(text):
    return {"params":encrypt('TA3YiYCfY2dDJQgg',encrypt('0CoJUm6Qyw8W8jud',text)),"encSecKey":"84ca47bca10bad09a6b04c5c927ef077d9b9f1e37098aa3eac6ea70eb59df0aa28b691b7e75e4f1f9831754919ea784c8f74fbfadf2898b0be17849fd656060162857830e241aba44991601f137624094c114ea8d17bce815b0cd4e5b8e2fbaba978c6d1d14dc3d1faf852bdd28818031ccdaaa13a6018e1024e2aae98844210"}

'''run'''
if __name__ == '__main__':
    userphone = os.environ["NETEASE_PHONE"]
    password = os.environ["NETEASE_PASSWORD"]
    s=requests.Session()
    header={}
    url="https://music.163.com/weapi/login/cellphone"
    url2="https://music.163.com/weapi/point/dailyTask"
    url3="https://music.163.com/weapi/v1/discovery/recommend/resource"
    logindata={
        "phone": userphone,
        "countrycode":"86",
        "password":md5(password),
        "rememberLogin":"true",
    }
    headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            "Referer" : "http://music.163.com/",
            "Accept-Encoding" : "gzip, deflate",
            }
    headers2 = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            "Referer" : "http://music.163.com/",
            "Accept-Encoding" : "gzip, deflate",
            "Cookie":"os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=2.0.3.131777; channel=netease; __remember_me=true;"
            }

    res=s.post(url=url,data=protect(json.dumps(logindata)),headers=headers2)
    tempcookie=res.cookies
    object=json.loads(res.text)
    if object['code']==200:
        print("登录成功！")
    else:
        print("登录失败！请检查密码是否正确！"+str(object['code']))
        exit(object['code'])

    res=s.post(url=url2,data=protect('{"type":0}'),headers=headers)
    object=json.loads(res.text)
    str1,str2 = '',''
    if object['code']!=200 and object['code']!=-2:
        str1+= ("手机端签到时发生错误："+object['msg'])
    else:
        if object['code']==200:
            str1+= ("手机端签到成功，经验+"+str(object['point']))
        else:
            str1+= ("手机端重复签到")

    res=s.post(url=url2,data=protect('{"type":1}'),headers=headers)
    object=json.loads(res.text)
    if object['code']!=200 and object['code']!=-2:
        str2+= ("PC端签到时发生错误："+object['msg'])
    else:
        if object['code']==200:
            str2+= ("PC端签到成功，经验+"+str(object['point']))
        else:
            str2+= ("PC端重复签到")
    #设置服务器所需信息
    #163邮箱服务器地址
    mail_host = 'smtp.126.com'  
    #163用户名
    mail_user = os.environ["SENDER_USERNAME"]
    #密码(部分邮箱为授权码) 
    mail_pass = os.environ["SENDER_KEY"]
    #邮件发送方邮箱地址
    sender = os.environ["SENDER_USERNAME"]
    #邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = os.environ["RECEIVERS_NAMES"].split(",")
    #设置email信息
    #邮件内容设置
    content = str1+' '+str2+time.strftime('%H:%M:%S', time.localtime())
    message = MIMEText(content,'plain','utf-8')
    #邮件主题       
    message['Subject'] = Header('网易云音乐签到', 'utf-8')
    #发送方信息
    message['From'] = sender 
    #接受方信息     
    message['To'] = receivers[0]
    #登录并发送邮件
    try:
        smtpObj = smtplib.SMTP() 
        # 连接到服务器
        smtpObj.connect(mail_host,25)
        #######替换为########
        # smtpObj = smtplib.SMTP_SSL(mail_host)
        #登录到服务器
        smtpObj.login(mail_user,mail_pass) 
        #发送
        smtpObj.sendmail(
            sender,receivers,message.as_string()) 
        #退出
        smtpObj.quit() 
        print('success')
    except smtplib.SMTPException as e:
        print('error',e) #打印错误
