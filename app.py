from flask import Flask,request,session
from model import med_query,search_user
from uitemplates import button_template,text_template
import threading
import json
import requests
import os.path
import sys
import uuid


print("starting server")

app=Flask(__name__)


def reply_for_query(fb_id,fb_text):
    number, med = main(fb_text)
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
            print(request.args.get('hub.challenge', ''))
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
                data = text_template(fb_id, "please give your phone number")
            elif session[fb_id] == "adding_nuber":
                user_number = fb_text
                session[fb_id + ":" + "user_number"] = user_number
                data = text_template(fb_id, "thanks for registering")
            reply(data)
        else:
            thread1 = threading.Thread(target=reply, args=(fb_id, fb_text,))
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

try:

    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

    )



def main(msg):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = str(uuid.uuid1())
    request.query = msg
    response = request.getresponse()
    data = response.read()

    data1 = json.loads(data)
    data2=data1["result"]["parameters"]["number"]
    data3=data1["result"]["parameters"]["medicines"]
    return data2,data3
# print(data['res'])
#json.loads(var1)




if __name__ == '__main__':
    app.run(port=8000, debug=True)
