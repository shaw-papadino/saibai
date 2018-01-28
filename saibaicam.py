#!/usr/bin/python
#-*- coding: utf-8 -*-

import picamera
import datetime
import os,sys
import time

import dropbox

import smtplib
from email import Encoders
from email.Utils import formatdate
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

ADDRESS=""
PASSWARD = ""
SMTP="smtp.gmail.com"
PORT=587

def create_message(from_addr, to_addr, subject, body, mime=None, attach_file=None):
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Date"] = formatdate()
        msg["Subject"] = subject
        body = MIMEText(body)
        msg.attach(body)

        return msg
def send(from_addr, to_addrs, msg):
        smtpobj = smtplib.SMTP(SMTP, PORT)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(ADDRESS, PASSWARD)
        smtpobj.sendmail(from_addr, to_addrs, msg.as_string())
        smtpobj.close()

now = datetime.datetime.now()
nowf = "{0:%H%M%S}.png".format(now)
dir_name = now.strftime('%Y%m%d')
dir_path = '/home/pi/saibaicam/'+ dir_name
file_name = now.strftime("%H%M%S")

if not os.path.exists(dir_path):
    os.makedirs(dir_path)
    os.chmod(dir_path, 0777)

try:
    picamera = picamera.PiCamera()
    dbx = dropbox.Dropbox('')
    dbx.users_get_current_account()
    i = 0
    while i < 24:
        now = datetime.datetime.now()
        nowf = "{0:%H:%M:%S}.png".format(now)
        file_name = now.strftime("%H:%M:%S")
        base = os.path.basename(dir_path+'/'+ nowf)
        picamera.capture(dir_path +'/'+ base)

        dbx = dropbox.Dropbox('')
        dbx.users_get_current_account()
        with open(dir_path +'/'+  base,'rb') as f:
                dbx.files_upload(f.read(),"/saibaicam/"+dir_name+"/"+ nowf)
        f.close()
        i = i + 1
        if i ==1:
                #宛先
                to_addr = ""

                #件名,本文
                subject = "Cam"
                body = "SaibaiCam Go"
                #メッセージ作成
                msg = create_message(ADDRESS, to_addr, subject, body)
                #送信
                send(ADDRESS, [to_addr], msg)
        time.sleep(3600)

    to_addr = ""
    subject = "finish"
    body = "SaibaiCam finished"
    msg = create_message(ADDRESS, to_addr, subject, body)
    send(ADDRESS, [to_addr], msg)
    sys.exit()
except KeyboardInterrupt:

    pass
