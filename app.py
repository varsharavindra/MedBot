from flask import Flask,request
import threading
from flaskext
import json
import requests
print("starting server")

app=Flask(__name__)
token="EAACGHzJZBmDABAJH46EL4XMx90yxhdCXekg0tmvWFVnxWpYEp4nKCZCMvlySgQsCjVfZAZCzEoBvlAHsvJn08xNRVMcsMO828OFPLnakJ2jH9ES2w0eCYfJdMpGq8EXLZCaRWXUH6YYy75OAZB6rfZADIRK6moUuYZBN1GhhlECdnc3IWFrq1hYG"



def reply(b,c):

    data={
    "messaging_type": "RESPONSE",
     "recipient": {
    "id": b
    },
    "message": {
      "text": c
    }
    }
    r=json.dumps(data)
    print(r)
    # req = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token="+token,json=r)
    # print(req.content)

@app.route('/',methods=['GET', 'POST'])
def hello_world():
    if request.method=='GET':
        if (request.args.get('hub.verify_token', '') == "varsha"):
            print("succefully verified")
            return request.args.get('hub.challenge', '')
    else:
        a=request.get_json()
        b=a['entry'][0]['messaging'][0]['sender']['id']
        c=a['entry'][0]['messaging'][0]['message']['text']
        print(b)
        print(c)
        thread1 = threading.Thread(target=reply, args=(b, c,))
        thread1.start()
    return "ok"

# @app.route('/varsha',methods=['GET', 'POST'])
# # def another():
# #     x=request.get_json()
# #     print(x)
# #     return "hello"


if __name__ == '__main__':
    app.run(port=8000, debug=True)