
from enum import Enum
import json
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





def button_template(fb_id,med,n):
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



class base_reply_template:

    def init(self,messaging_type,fb_id,message):
        self.messaging_type=messaging_type
        self.recipient={"id":fb_id}
        self.message=message




class buttons:
    def __init__(self,type,**kwargs):
        self.type=type
        for key, value in kwargs.items():
                setattr(self, key, value)


class genereic_template_elements:
    def __init__(self,title,**kwargs):
        self.title=title
        for key, value in kwargs.items():
                setattr(self, key, value)

class payload_template:
    def __init__(self,template_type,**kwargs):
        self.template_type=template_type
        for key, value in kwargs.items():
                setattr(self, key, value)

class attachment_template:
    def __init__(self,type,**kwargs):
        self.type=type
        for key, value in kwargs.items():
            setattr(self, key, value)


class message:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class button_template_class(base_reply_template):
    def __init__(self,title,buttons):
        attachment = attachment_template("template", payload=payload_template("button",text=title,buttons=buttons).__dict__)
        msg = message(attachment=attachment.__dict__)


class generic_template_class(base_reply_template):
    def __init__(self,fb_id,elements):
        attachment=attachment_template("template", payload=payload_template("generic", elements=elements).__dict__)
        msg=message(attachment=attachment.__dict__)
        super(generic_template_class, self).init("RESPONSE", fb_id=fb_id, message=msg.__dict__)





# def generic_template(fb_id,bill_info_url):
#
#     generic_data = {
#         "messaging_type": "RESPONSE",
#         "recipient": {
#             "id": fb_id
#         },
#         "message": {
#             "attachment": {
#                 "type": "template",
#                 "payload": {
#                     "template_type": "generic",
#                     "elements": [
#                         {
#                             "title": "Welcome!",
#                             "image_url": "http://szzljy.com/assets/download.php?file=/images/medicine/medicine2.jpg",
#                             "subtitle": "Location of user",
#                             "default_action": {
#                                 "type": "web_url",
#                                 "url": bill_info_url,
#                             },
#                             "buttons": [
#                                 {
#                                     "type": "web_url",
#                                     "url": "www.google.com",
#                                     "title": "View location"
#                                 }
#                             ]
#                         }
#                     ]
#                 }
#
#         }
#
#
#     }
#     }
#     return generic_data


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
        for t in kargs["data"]:

            quick_replies.append(t)

        text_data["message"]["quick_replies"]=quick_replies
    print(text_data)
    return text_data



class quick_reply_template_class():

    def  __init__(self,type,**kwargs):
        if type==quick_reply_type.text:
           self.content_type="text"
           self.title=kwargs["title"]
           self.payload=kwargs["payload"]
           self.image_url=kwargs["image_url"]

        elif type==quick_reply_type.phone_number:
            self.content_type="user_phone_number"
        elif type==quick_reply_type.location:
            self.content_type="location"
        else:
            self.content_type = "user_email"



def quick_reply_template(type,kwargs):
    reply=None

    if type==quick_reply_type.text:
        reply={
            "content_type": "text",
            "title":kwargs["title"],
            "payload":kwargs["payload"],
            "image_url":kwargs["image_url"]
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

if __name__== "__main__":
    # dict=text_template("10","hi",quick_reply=True,type=[quick_reply_type.text],title="Sending text",payload="Extra info",image_url="example.com/xyz.jpg")
    # print(dict)
    # user_data = quick_reply_template_class(quick_reply_type.phone_number)
    #
    # data = json.dumps(user_data.__dict__)
    elements=[genereic_template_elements(title="varsha",image_url="fdf",sub_title="5tab",buttons=buttons("web_url","www.google.com","location").__dict__).__dict__]
    print(elements)
    obj=generic_template_class("100",elements)
    print(obj.__dict__)
