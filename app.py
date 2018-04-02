from flask import Flask,request
from werkzeug.contrib.cache import SimpleCache
from model import med_query,insert_query_users,search_user
from uitemplates import button_template,text_template,quick_reply_type,quick_reply_template_class

import threading
import json
import requests
import os.path
import sys
import uuid
import nlp

from nlp import apiai_query

token="hero"
CLIENT_ACCESS_TOKEN = 'ab47593acb7f45c68ca4ffe296db1885'
session=dict()


app=Flask(__name__)
app.config['SECRET_KEY']="abcdefghijn"

def reply_for_query(fb_id,fb_text):

    # number, med = apiai_query(fb_text)
    # data = button_template(fb_id, fb_text, med, 1)
    data=None
    reply(data)


def reply(data):
    json_data=json.dumps(data)
    print("What is this json data")
    print(json_data)
    # req = requests.post("https://graph.facebook.com/v2.6/me/messages",params={"access_token": token}, headers={"Content-Type": "application/json"},data=json_data)
    # print(req.content)



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

        print(fb_id)

        if not search_user(fb_id):
            file_names = os.listdir(os.path.dirname(__file__))
            if str(fb_id) + ".txt" in file_names:
                with open(str(fb_id) + "_status" + ".txt", "r") as f:
                    status = f.readline()

                if status == "adding_name":
                    name = a['entry'][0]['messaging'][0]['message']['text']
                    with open(str(fb_id)+".txt","a") as f:
                        f.write(name+"\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("adding_number")
                    phone_number_data = quick_reply_template_class(quick_reply_type.phone_number)
                    data = text_template(fb_id, "please give your phone number", quick_reply=True,type=[quick_reply_type.phone_number],data=[phone_number_data.__dict__])


                if status == "adding_number":
                    number = a['entry'][0]['messaging'][0]['message']['quick_reply']['payload']
                    with open(str(fb_id)+".txt","a") as f:
                        f.write(number+"\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("getting email")
                    email_data = quick_reply_template_class(quick_reply_type.email)
                    data = text_template(fb_id, "please give us your email", quick_reply=True,type=[quick_reply_type.email],data=[email_data.__dict__])


                if status == "getting email":
                    email = a['entry'][0]['messaging'][0]['message']['quick_reply']['payload']
                    with open(str(fb_id)+".txt","a") as f:
                        f.write(email+"\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("getting location")
                    location_data = quick_reply_template_class(quick_reply_type.location)
                    data = text_template(fb_id, "please give your location", quick_reply=True,type=[quick_reply_type.email],data=[location_data.__dict__])

                if status == "getting location":
                    lat = a['entry'][0]['messaging'][0]['message']["attachments"][0]["payload"]["coordinates"]["lat"]
                    long = a['entry'][0]['messaging'][0]['message']["attachments"][0]["payload"]["coordinates"]["long"]
                    location=str(lat)+":"+str(long)


                    with open(str(fb_id) + ".txt","r") as f:
                        user_name = f.readline()
                        user_phone = f.readline()
                        user_email=f.readline()
                        user_location = f.readline()
                    insert_query_users(user_name, location, user_phone, user_email, fb_id )
                    os.remove(str(fb_id) + ".txt")
                    os.remove(str(fb_id) + "_status" + ".txt")
                    data = text_template(fb_id, "thank you for registering with us")

            else:
                fd = open(str(fb_id) + ".txt", "w")
                fd.close()
                with open(str(fb_id) + "_status" + ".txt", "w") as f:
                    status = f.write("adding_name")
                data = text_template(fb_id, "hey this is your first message,whats your name ?")

            thread1 = threading.Thread(target=reply, args=(data,))
        else:
            fb_text = a['entry'][0]['messaging'][0]['message']['text']
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
