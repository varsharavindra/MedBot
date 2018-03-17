from flask import Flask,request,session

from model import med_query,search_user,add_user
from uitemplates import button_template,text_template,quick_reply_type

import threading
import json
import requests
import os.path
import sys
import uuid

from nlp import apiai_query


app=Flask(__name__)
app.config['SECRET_KEY']="abcdefghijk"

def reply_for_query(fb_id,fb_text):

    number, med = apiai_query(fb_text)
    data = button_template(fb_id, fb_text, med, 1)
    reply(data)


def reply(data):
    json_data=json.dumps(data)
    print("What is this json data")
    print(json_data)
    req = requests.post("https://graph.facebook.com/v2.6/me/messages",params={"access_token": token}, headers={"Content-Type": "application/json"},data=json_data)
    print(req.content)



@app.route('/webhook',methods=['GET', 'POST'])
def hello_world():
    if request.method=='GET':
        if (request.args.get('hub.verify_token', '') == "varsha"):
            print("succefully verified")


            return request.args.get('hub.challenge', '')
    else:
        print("got a message")
        a=request.get_json()
        fb_id=a['entry'][0]['messaging'][0]['sender']['id']
        fb_text=a['entry'][0]['messaging'][0]['message']['text']
        print(fb_id)
        print(fb_text)
        if not search_user(fb_id):
            if (session[fb_id] == None):
                session[fb_id] = "adding_name"
                data = text_template(fb_id, "hey this is your first message,whats your name ?")
            elif session[fb_id] == "adding_name":
                user_name = fb_text
                session[fb_id + ":" + "user_name"] = user_name
                session[fb_id] = "adding_number"

                data = text_template(fb_id, "please give your phone number",quick_reply=True,type=[quick_reply_type.phone_number])
            elif session[fb_id] == "adding_nuber":
                user_number = fb_text
                session[fb_id + ":" + "user_number"] = user_number
                data = text_template(fb_id, "please give us your location",quick_reply=True,type=[quick_reply_type.location])
                session[fb_id] = "getting location"
            elif session[fb_id] == "getting location":
                session[fb_id] = "registration done"
                lat=a['entry'][0]['messaging'][0]['message']["attachments"][0]["payload"]["coordinates"]["lat"]
                long = a['entry'][0]['messaging'][0]['message']["attachments"][0]["payload"]["coordinates"]["long"]
                data = text_template(fb_id, "thank you for registering with us")
                user_name=session[fb_id + ":" + "user_name"]
                user_number=session[fb_id + ":" + "user_number"]
                add_user(user_name,user_number,lat,long)
            else:
                session.pop(fb_id)
                session.pop(fb_id + ":" + "user_name")
                session.pop(fb_id+":"+"user_number")
                session.clear()


            thread1 = threading.Thread(target=reply, args=(data,))
        else:
            thread1 = threading.Thread(target=reply_for_query, args=(fb_id, fb_text,))

        print("Starting thread")
        thread1.start()
    return "ok"



@app.route('/button',methods=['GET', 'POST'])
def button():
    return "done by vivek"



# @app.route('/varsha',methods=['GET', 'POST'])
# # def another():
# #     x=request.get_json()
# #     print(x)
# #     return "hello"



# print(data['res'])
#json.loads(var1)




if __name__ == '__main__':
    app.run(port=8000, debug=True)
