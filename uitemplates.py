from enum import Enum

class quick_reply_type(Enum):
    text=0
    phone_number=1
    location=2
    email=3


def number_of_buttons(type, url, title):
    var = {
        "type": type,
        "url": url,
        "title": title
    }

    return var


def button_template(fb_id,fb_text,med,n):
    button_data = {
        "messaging_type": "RESPONSE",
        "recipient": {
            "id": fb_id
        },
        "message": {

            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": med,
                    "buttons": [
                        number_of_buttons("web_url", "https://medecinebot.herokuapp.com/button", "coming soon") for i in range(0,n)

                    ]

                }
            }
        }
    }
    return button_data

def text_template(fb_id, reply_message,quick_reply=False,**kargs):
    text_data = {
        "messaging_type": "RESPONSE",
        "recipient": {
            "id": fb_id
        },
        "message": {

            "text": reply_message,

        }

    }
    quick_replies=[]
    if quick_reply:
        for t in kargs[type]:
            quick_replies.append(quick_reply(t,kargs))

    text_data["message"]["quick_replies"]=quick_replies
    return text_data


def quick_reply(type,**kwargs):
    reply=None
    if type==quick_reply_type.text:
        reply={
            "content_type": "text",
            "title":kwargs[text],
            "payload":kwargs[payload],
            "image_url":kwargs[image_url]
        }
    elif type==quick_reply_type.location:
        reply={
        "content_type":"location",
        }
    elif type==quick_reply_type.phone_number:
        reply={
                "content_type":"user_phone_number"
              }
    else:
        reply={

        }
    return reply