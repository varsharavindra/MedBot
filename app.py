from flask import Flask,request
import threading
import json
import requests
import os.path
import sys
import uuid

print("starting server")

app=Flask(__name__)
token="EAACGHzJZBmDABAOlZAEPVM2ikVWHx8hlMzmTZCO6l3s3kWMjQo5oywc0H8NK3IfMehFoEIHRS4W0w6REcfKWzxy7P9qAayTZBeVVZCpcU7KdSbC4rhiZBYMMryYLZCf0QEmEJSBqNSEZBJy7fEQmT7MQdoWYqTLEZBJOxKgkrioYhqv1AYTORC8Uu"



def reply(fb_id,fb_text):

    number,med=main(fb_text)
    data={
    "messaging_type": "RESPONSE",
     "recipient": {
    "id": fb_id
    },
    "message": {
      "text": med
    }
    }
    json_data=json.dumps(data)
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
        thread1 = threading.Thread(target=reply, args=(fb_id, fb_text,))
        print("Starting thread")
        thread1.start()
    return "ok"

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

CLIENT_ACCESS_TOKEN = 'ab47593acb7f45c68ca4ffe296db1885'

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