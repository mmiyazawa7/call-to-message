# coding: utf-8

# for ipython
# get_ipython().magic('load_ext dotenv')
# get_ipython().magic('dotenv')

from flask import Flask,request, Response,session
from app_funcs import proc_inbound_msg
from pprint import pprint
import requests
import json
import nexmo
import datetime
import time
from base64 import urlsafe_b64encode
import os
import calendar
import jwt # https://github.com/jpadilla/pyjwt -- pip3 install PyJWT
import coloredlogs, logging
from uuid import uuid4

import os
from os.path import join, dirname

# for heroku, please put all env parameters to 'Config Vars` in heroku dashboard
# from dotenv import load_dotenv
# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)

api_key = os.environ.get("API_KEY") 
api_secret = os.environ.get("API_SECRET")
application_id = os.environ.get("APPLICATION_ID")
msg_application_id = os.environ.get("MSG_APPLICATION_ID")

# keyfile = os.environ.get("KEYFILE")
# keyfile_msg = os.environ.get("KEYFILE_MSG")

private_key = os.environ.get("PRIVATE_KEY")
private_key_msg = os.environ.get("PRIVATE_KEY_MSG")

webhook_url = os.environ.get("WEBHOOK_URL")
web_port = os.environ.get("WEB_PORT")
virtual_number = os.environ.get("LVN")

from_sms = os.environ.get("FROM_SMS")
from_whatsapp = os.environ.get("FROM_WHATSAPP")
operator = os.environ.get("OPERATOR")
video_url = os.environ.get("VIDEO")
wa_sandbox_url = os.environ.get("WA_SANDBOX")

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

url = "https://api.nexmo.com/v1/calls"

session={}
session['to']=""
session['from']=""

client_sms = nexmo.Client(key=api_key, secret=api_secret)

# client = nexmo.Client(application_id=application_id, private_key=keyfile)

client = nexmo.Client(application_id=application_id, private_key=private_key)

@app.route('/answer',methods=['GET', 'POST'])
def answer():

    session['to'] = request.args['to']
    session['from'] = request.args['from']

    # session['to'] = arg_to
    # session['from'] = arg_from

    logger.debug('From: %s', session['from'])
    logger.debug('To: %s', session['to'])

    ncco=[{
	        "action": "talk",
	        "text": "Nexmo急送便にお電話いただき、ありがとうございます。お客様への配送予定をテキストメッセージでお知らせするには１とシャープを、オペレータと音声でお話しするには２とシャープを押してください",
            "bargeIn": "true",
	        "voiceName": "Mizuki"
	      },
          {
            "action": "input",
            "timeOut": "60",
            "submitOnHash": "true",
            "eventUrl": [webhook_url+"/dtmfresponse"]
            }]
    js=json.dumps(ncco)
    resp=Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/dtmfresponse',methods=['GET', 'POST'])
def dtmfresponse():

    currentDT = datetime.datetime.now()
    date =currentDT.strftime("%Y-%m-%d %H:%M:%S")

    webhookContent = request.json
    try:
        result = webhookContent['dtmf']
    except:
        pass

    logger.debug("The User enter: " + str(result) + "\n")
    logger.debug(date)
    if result == '1':
        delivery_date = "明日の午前９時"
        ncco = [
            {
                "action": "talk",
                "text": "お客様のお荷物の配送予定日時は"+delivery_date+"です。メッセージを送信しましたのでそちらを参照してください。",
                "voiceName": "Mizuki"
            }
            ]
        js = json.dumps(ncco)
        resp = Response(js, status=200, mimetype='application/json')
        
        logger.debug('Start Call to message')
        change_request_msg = "日時変更されたいですか？ はい - 1, いいえ - 2"

        msg = "お客様のお荷物の配送予定日時は"+delivery_date+"です。" + change_request_msg

        if "from" in session:
            send_to = session['from']
            logger.debug(send_to)
            channel_type = "whatsapp"
            response_msg = send_msg_freeform (from_whatsapp, send_to, msg, channel_type)
        return resp
    
    elif result == '2':
        msg = "お客様からのお問い合わせです" + session['from'] + " on " + date
        channel_type = "whatsapp"
        response_msg = send_msg_freeform(from_whatsapp, operator, msg, channel_type)
        
        ncco = [
            {
                "action": "connect",
                "eventUrl": [webhook_url+"/event"],
                "eventType": "synchronous",
                "timeout": "45",
                "from": virtual_number,
                "endpoint": [
                    {
                        "type": "phone",
                        "number": operator
                    }
                ]
            }
        ]
        js = json.dumps(ncco)
        resp = Response(js, status=200, mimetype='application/json')
        logger.debug('Response NCCO with Operator number')
        return resp
    return "OK"

@app.route('/event', methods=['GET', 'POST', 'OPTIONS'])
def display():
    r = request.json
    return "OK"

@app.route('/webhooks/inbound', methods=['POST'])
def inbound_message():
    logger.debug("** inbound_message **")
    data = request.get_json()
 
    input_msg = proc_inbound_msg(data['from']['type'], data)
    if input_msg == '1':
        reschedule_menu = "希望の配達予定時間帯を指定してください。a-明日の午前中  b-明日の午後12時から18時　c-夜間18時から21時。d-オペレータとビデオ通話"
        
        channel_type = data['from']['type']
        
        if channel_type == "whatsapp":
            response_msg = send_msg_freeform (from_whatsapp, data['from']['number'], reschedule_menu, channel_type)
        return("inbound_message", 200)

    if input_msg == '2':
        schedule_fixed = "かしこまりました。予定通りお届けいたします"
            
        channel_type = data['from']['type']
        if channel_type == "whatsapp":
            response_msg = send_msg_freeform (from_whatsapp, data['from']['number'], schedule_fixed, channel_type)
        return ("inbound_message", 200)
    
    if input_msg == 'a':
        rescheduled_time = "かしこまりました。お荷物は明日の午前中にお届けいたします。"
        channel_type = data['from']['type']
        response_msg = send_msg_freeform (from_whatsapp, data['from']['number'], rescheduled_time, channel_type)
            
    elif input_msg == 'b':
        rescheduled_time = "かしこまりました。明日の午後12時から18時にお届けいたします。"
        channel_type = data['from']['type']
        response_msg = send_msg_freeform (from_whatsapp, data['from']['number'], rescheduled_time, channel_type)
    elif input_msg == 'c':
        rescheduled_time = "かしこまりました。夜間18時から21時にお届けいたします。"
        channel_type = data['from']['type']
        response_msg = send_msg_freeform (from_whatsapp, data['from']['number'], rescheduled_time, channel_type)
    elif input_msg == 'd':
        connect_operator = "オペレータとビデオ通話するにはこちらのリンクをクリックしてください" + video_url
        channel_type = data['from']['type']
        response_msg = send_msg_freeform (from_whatsapp, data['from']['number'], connect_operator, channel_type)
        response_msg2 = send_msg_freeform (from_whatsapp, operator, data['from']['number']+"のお客様からのお問い合わせです。　"+ video_url, channel_type) 
        return ("inbound_message", 200)
    return ("inbound_message", 200)

@app.route('/webhooks/status', methods=['POST'])
def message_status():
    logger.debug("** message_status **")
    data = request.get_json()
    if "to" in data:
        logger.debug(data)
        send_to = data['to']['number']
        channel_type = data['to']['type']
    if "error" in data:
        logger.debug(data)
        if data['error']['code'] == 1340:     # Sent Outside Allowed Window
            wa_optin = "https://wa.me/" + from_whatsapp + "?text=OPTIN"
            sms_text = "WhatsAppにメッセージを送ってよろしければ、こちらのリンクをクリックしてWhatsAppでOPTINしてください。 " + wa_optin
            response_SMS = client_sms.send_message({'from': 'Nexmo', 'to': send_to, 'type':'unicode','text': sms_text},)
            logger.debug(response_SMS)
            return ("message_status", 200)
    return ("message_status", 200)

@app.route('/webhooks/inbound-sms', methods=['POST'])
def inbound_sms():
    logger.debug("** inbound_sms **")
    values = request.values
    proc_inbound_msg('sms', values)
    return ("inbound_sms", 200)

@app.route('/webhooks/delivery-receipt', methods=['POST'])
def delivery_receipt():
    logger.debug("** delivery_receipt **")
    data = request.get_json()
    logger.debug(data)
    return ("delivery_receipt", 200)

def send_msg_freeform(sender, recipient, text_msg, channel_type):
    
    logger.debug('Send Message')
    logger.debug(channel_type)
    logger.debug(text_msg)
    logger.debug(recipient)
    
    expiry = 1*60*60 # JWT expires after one hour (default is 15 minutes)
    
#    f = open(keyfile_msg, 'r')
#    private_key_msg = f.read()
#    f.close()

    data_body = json.dumps({
           "from": {
               "type": channel_type,
               "number": sender
               },
           
           "to":{
               "type": channel_type,
               "number": recipient
           },
           "message":{
               "content":{
                   "type": "text",
                   "text": text_msg
               }
           }
       }
       )
    payload = {
        'application_id': msg_application_id,
        'iat': int(time.time()),
        'jti': str(uuid4()),
        'exp': int(time.time()) + expiry,
    }
    gen_jwt  = jwt.encode(payload, private_key_msg, algorithm='RS256')
    auth = b'Bearer '+gen_jwt
    headers = {'Authorization': auth, 'Content-Type': 'application/json'}
    
   
    if channel_type == 'whatsapp':
        r = requests.post(wa_sandbox_url, headers=headers, data=data_body)
        # r = requests.post('https://api.nexmo.com/v0.1/messages', headers=headers, data=data_body)
        return r.json
    elif channel_type == 'sms':
        r = requests.post('https://api.nexmo.com/v0.1/messages', headers=headers, data=data_body)
        return r.json()

    

if __name__ == '__main__':
    app.run(port=web_port)

