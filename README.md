# Call-To-Message

This is sample application demo how to make Simple Voice IVR and 2-way Messaging service with Nexmo Voice/Message API

This app is built using [Flask framework](http://flask.pocoo.org/) and require [Python3](https://www.python.org/)

## Prerequisite

You will need a few thins to get going with this app: 

- A [Nexmo](https://nexmo.com) Account
- A Nexmo Messages & Dispatch App [[set one up here]](https://dashboard.nexmo.com/messages/create-application)
- A Nexmo Voice App [[set one up here]](https://dashboard.nexmo.com/voice/create-application)
- To buy Phone Number for Voice App [[set one up here]](https://dashboard.nexmo.com/buy-numbers)
- A WhatsApp Business Account or SMS 2way Number

To install the Python client library using pip:

    pip install nexmo

To upgrade your installed client library using pip:

    pip install nexmo --upgrade

To rename .env_sample to .env and set parameter

## Running the demo


For demo, to run ngrok for webhook

    $ ngrok http 3000

    Forwarding                    https://xxxxxx.ngrok.io -> localhost:3000
    
Please set "https://xxxxxx.ngrok.io" to "WEBHOOK_URL" in .env file

    WEBHOOK_URL = "Your Base Webhook URL"

To run application

$ python3 call-to-whatsapp.py
    
Webhook will be up and running using PORT:3000

## To deploy heroku

Install Heroku CLI Tool

    $ brew install heroku-toolbelt
    $ heroku login
    Enter your Heroku credentials.
    Email: [email]
    Password (typing will be hidden)
    Logged in as [email]
    
Deploy this App to Heroku

    git clone https://github.com/mmiyazawa7/call-to-message.git
    $ heroku create
    $ git push heroku master
    
Setup env parameters to Config Vars in heroku

    Open 'https://dashboard.heroku.com/apps/(your heroku app name)/settings'
    Set `Concig Vars`
    
    API_KEY
    API_SECRET
    APPLICATION_ID      (Your Nexmo Voice Application ID)
    MSG_APPLICATION_ID  (Your Nexmo Message Application ID)
    FROM_WHATSAPP       (Your WhatsApp Business Number)
    LVN                 (Your Nexmo Voice LVN)
    OPERATOR            (Operator's Phone Number)
    PRIVATE_KEY         (Your Private Key for your Voice Aapp)
    PRIVATE_KEY_MSG     (Your Private Key for your Message App)
    WA_SANDBOX          (WhatsApp Sandbox Endpoint, Contact Us)
    WHEBHOOK_URL        (Webhook URL on heroku)
    WEB_PORT            
    
Monitor heroku logs

    $ heroku logs
    $ heroku logs --tail
    
