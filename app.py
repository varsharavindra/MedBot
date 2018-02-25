from flask import Flask,request
import threading
import json
import requests
print("starting server")

app=Flask(__name__)
token="EAACGHzJZBmDABAJH46EL4XMx90yxhdCXekg0tmvWFVnxWpYEp4nKCZCMvlySgQsCjVfZAZCzEoBvlAHsvJn08xNRVMcsMO828OFPLnakJ2jH9ES2w0eCYfJdMpGq8EXLZCaRWXUH6YYy75OAZB6rfZADIRK6moUuYZBN1GhhlECdnc3IWFrq1hYG"



def reply(fb_id,fb_text):

    data={
    "messaging_type": "RESPONSE",
     "recipient": {
    "id": fb_id
    },
    "message": {
      "text": fb_text
    }
    }
    aquired_data=json.dumps(data)
    print(aquired_data)

    req = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token="+token,json=r)
    print(req.content)

@app.route('/webhook',methods=['GET', 'POST'])
def hello_world():
    if request.method=='GET':
        if (request.args.get('hub.verify_token', '') == "varsha"):
            print("succefully verified")
            print(request.args.get('hub.challenge', ''))
            return request.args.get('hub.challenge', '')
    else:
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


if __name__ == '__main__':
    app.run(port=8000, debug=True)