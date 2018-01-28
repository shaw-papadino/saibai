#!/usr/bin/python
#-*- coding: utf-8 -*-

import smbus
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
import os,sys
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

try:
    bus = smbus.SMBus(1)
    i=1
    humidity2 = []
    cTemp2 = []
    times = []
    fig = plt.figure()
    fig,  ax1 = plt.subplots()
    while  i < 145:
        bus.write_byte(0x40 , 0xF5)
        time.sleep(0.3)

        data0 = bus.read_byte(0x40)
        data1 = bus.read_byte(0x40)

        humidity = ((data0 * 256 + data1 ) * 125 / 65536.0) - 6
        time.sleep(0.3)

        if humidity < 55 :
                #宛先
                to_addr = ""
                #件名,本文
                subject = "alert"
                body = "Saibai Humid Low"
                #メッセージ作成
                msg = create_message(ADDRESS, to_addr, subject, body)
                #送信
                send(ADDRESS, [to_addr], msg)

        bus.write_byte(0x40, 0xF3)
        time.sleep(0.3)

        data0 = bus.read_byte(0x40)
        data1 = bus.read_byte(0x40)

        cTemp = ((data0 * 256 + data1) * 175.72 / 65536.0)  - 46.85

        humidity2.append(humidity)
        cTemp2.append(cTemp)
        now = datetime.datetime.now().time()
        now = now.strftime("%H:%M:%S")
        t = datetime.datetime.strptime(now,'%H:%M:%S')
        times.append(t)

        if i % 6 == 0 :
                fig,  ax1 = plt.subplots()
                ax2 = ax1.twinx()
                p1, = ax1.plot(times[-6:],humidity2[-6:],color ="blue")
                p2, = ax2.plot(times[-6:],cTemp2[-6:],color ="red")
                plt.legend([p1,p2],[u"湿度",u"温度"])
                ax1.set_xlabel(u"時間" )
                ax1.set_xticks(times[-6:])
                ax1.set_xticklabels(times[-6:],rotation=30 , fontsize = 8)
                ax2.set_ylim(0,40)
                ax1.set_ylim(0,100)
                ax2.set_ylabel(u"温度" ,color = "red")
                ax1.set_ylabel(u"湿度",color = "blue")
                plt.title(u"水槽内の温度/湿度")
                plt.tight_layout()
                now = datetime.datetime.now()
                nowf = "{0:%Y%m%d%H%M%S}.png".format(now)
                base = os.path.basename("/home/pi/saibai/"+nowf)
                plt.savefig("/home/pi/saibai/"+nowf)

        if i ==1:
                #宛先
                to_addr = ""
                #件名,本文
                subject = "HS"
                body = "Saibai Go"
                #メッセージ作成
                msg = create_message(ADDRESS, to_addr, subject, body)
                #送信
                send(ADDRESS, [to_addr], msg)
        i  = i + 1
        time.sleep(600)
    fig,  ax1 = plt.subplots()
    p1, = ax1.plot(times,humidity2,color ="blue", label =u"湿度")
    ax2 = ax1.twinx()
    p2, = ax2.plot(times,cTemp2,color ="red", label  = u"温度" )
    plt.legend([p1,p2],[u"湿度",u"温度"])
    ax1.set_xlabel(u"時間" )
    ax1.set_xticks(times)
    ax1.set_xticklabels(times,rotation=30 , fontsize = 8)
    ax2.set_ylim(0,40)
    ax1.set_ylim(0,100)
    ax2.set_ylabel(u"温度" ,color ="red")
    ax1.set_ylabel(u"湿度",color = "blue")
    plt.title(u"水槽内の温度/湿度")
    plt.tight_layout()

    now = datetime.datetime.now()
    nowf = "{0:%Y%m%d%H%M%S}.png".format(now)
    base = os.path.basename("/home/pi/saibai/"+nowf)
    plt.savefig("/home/pi/saibai/"+nowf)

    dbx = dropbox.Dropbox('')
    dbx.users_get_current_account()
    with open('/home/pi/saibai/'+base,'rb') as f:
            dbx.files_upload(f.read(),"/saibaigraph/"+nowf,mute=True)
    f.close()

    to_addr = ""
    subject = "finish"
    body = "Saibai finished"
    msg = create_message(ADDRESS, to_addr, subject, body)
    send(ADDRESS, [to_addr], msg)
    sys.exit()
except KeyboardInterrupt:

    pass
