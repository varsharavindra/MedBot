from flask import Flask, request
from werkzeug.contrib.cache import SimpleCache
from model import med_query, insert_query_users, search_user_for_med, current_user, search_user, \
    search_by_phone, search_trade_for_drug, get_med_info,get_drug_trade,get_med_data, get_email, get_med_for_user, \
    update_quantity
from uitemplates import button_template, text_template, quick_reply_type, quick_reply_template_class, \
    generic_template_class,text_template_class
from nlp import apiai_query, Query_medicine, Upload_medicine, General_Talk
from uitemplates import genereic_template_elements, buttons,button_template_class,subscription
from util import *
import threading
from threading import Thread
import json
import requests
import os.path
import sys
import uuid
import nlp
import util
import re
import smtplib
import gpxpy.geo
from math import radians
import datetime

threshold = 0
token = "EAACGHzJZBmDABAOlZAEPVM2ikVWHx8hlMzmTZCO6l3s3kWMjQo5oywc0H8NK3IfMehFoEIHRS4W0w6REcfKWzxy7P9qAayTZBeVVZCpcU7KdSbC4rhiZBYMMryYLZCf0QEmEJSBqNSEZBJy7fEQmT7MQdoWYqTLEZBJOxKgkrioYhqv1AYTORC8Uu"
CLIENT_ACCESS_TOKEN = 'ab47593acb7f45c68ca4ffe296db1885'
google_places_api_key="AIzaSyCfbetwFSxJnIGfVy1j5Abh4z0xcNPQwNQ"
session = dict()

# base_url = "https://localhost:8000/"
base_url="https://medecinebot.herokuapp.com/"
static_url = base_url + "static/"
user_url = static_url + "user.jpg"



app = Flask(__name__)
app.config['SECRET_KEY'] = "abcdefghijn"


def get_location_url(lat, long):
    return "https://www.google.com/maps/search/?api=1&query=" + str(lat) + "," + str(long)

def time_limit(potential_dist,potential_vendor_information,brand,fb_text):
    for i in potential_dist:
        button1 = buttons("postback", title="Yes, proceed", payload="YES")
        button2 = buttons("postback", title="No, I'm not available", payload="NO")
        data = button_template_class("A request for " + brand + " has been made, would you like to share medicine?",
                                     buttons=[button1.__dict__, button2.__dict__]).__dict__
        now = datetime.datetime.now().time().minute
        print(now)
        limit = now + 1
        #while True:
         #   if not (datetime.datetime.now().time().minute <= limit and fb_text["postback"]["payload"]== "YES"):



        print("Time is up!")

    now = datetime.datetime.now().time().minute
    print(now)
    limit = now + 1
    while True:
        if datetime.datetime.now().time().minute == limit:
            break

    print("Time is up!")



def query_medicine_response_builder(fb_id, brand, quantity):
    potential_distance = []
    impotential_distance = []
    elements = []
    elements1 = []
    elements2 = []
    potential_vendor_information, impotential_vendor_information = search_user_for_med(fb_id, quantity,
                                                                                       brand)


    current_user_location = current_user(fb_id)
    latitude, longitude = current_user_location.split(":")
    if len(potential_vendor_information) > threshold:
        for obj in potential_vendor_information:
            potential_distance.append(nearest_location(latitude, longitude, obj.lat, obj.long))
    potential_dist = sorted(range(len(potential_distance)), key=lambda k: potential_distance[k])
    if len(impotential_vendor_information) > threshold:

        for obj in impotential_vendor_information:
            impotential_distance.append(nearest_location(latitude, longitude, obj.lat, obj.long))
    impotential_dist = sorted(range(len(impotential_distance)), key=lambda k: impotential_distance[k])



    for i in potential_dist:
        location = get_location_url(obj.lat, obj.long)
        user_name = potential_vendor_information[i].uname
        subtitle = "Phone: " + str(potential_vendor_information[i].phone) + "\nQuantity: " + str(
            potential_vendor_information[i].qty)
        btn = buttons("web_url", location, "go to location in maps")
        elements.append(genereic_template_elements(user_name, image_url=user_url, subtitle=subtitle,
                                                   buttons=[btn.__dict__]))
    generic_data = generic_template_class(fb_id, elements)





    for i in impotential_dist:
        location1 = get_location_url(obj.lat,obj.long)
        user_name1 = impotential_vendor_information[i].uname
        subtitle1 = "Phone: " + str(impotential_vendor_information[i].phone) + "\nQuantity: " + str(
            impotential_vendor_information[i].qty)
        btn1 = buttons("web_url",location1,"Go to location in maps")
        elements1.append(genereic_template_elements(user_name1,image_url=user_url, subtitle=subtitle1,
                                                   buttons=[btn1.__dict__]))
    #generic_data = generic_template_class(fb_id, elements1)

    #if not potential_vendor_information and impotential_vendor_information:
    request_pharmacy=requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+latitude+","+longitude+"&type=pharmacy&radius=500&key="+google_places_api_key)
    print(request_pharmacy.content)
    pharmacy_data = request_pharmacy.json()
    print(pharmacy_data['results'][0]['geometry']['location']['lat'])
    pharmacy_name = []
    pharmacy_latitude = []
    pharmacy_longitude = []
    for p in pharmacy_data['results']:
        pharmacy_latitude.append(p['geometry']['location']['lat'])
        pharmacy_longitude.append(p['geometry']['location']['lng'])
    print(pharmacy_latitude)
    print(pharmacy_longitude)
    print(pharmacy_name)
    for x,y,z in zip(pharmacy_latitude,pharmacy_longitude,pharmacy_name):
        print(x,y,z)
        pharmacy_location = get_location_url(x, y)
        pharma_name = z
        btn1 = buttons("web_url", pharmacy_location, "go to location")
        elements2.append(genereic_template_elements(pharma_name, image_url=user_url, subtitle=False,
                                                       buttons=[btn1.__dict__]))
    #generic_data = generic_template_class(fb_id, elements2)
    return generic_data


def nearest_location(lat1, long1, lat2, long2):

    latitude1 = radians(float(lat1))
    longitude1 = radians(float(long1))

    latitude2 = radians(float(lat2))
    longitude2 = radians(float(long2))

    dist = gpxpy.geo.haversine_distance(latitude1, longitude1, latitude2, longitude2)
    return dist


def reply_for_query(fb_id, fb_text):
    data = text_template(fb_id, "i didnt understand!")
    print(data)
    context=util.get_context(fb_id)
    print(context)
    if context is None:
        text = fb_text['message']["text"]
        intent, parameter = apiai_query(text)

        if intent == General_Talk:
            button1=buttons("postback",title="Need Medicine",payload="NEED")
            button2 = buttons("postback", title="Upload Medicine", payload="UPDATE")
            data = button_template_class(fb_id, "How may I help you?", buttons=[button1.__dict__,button2.__dict__]).__dict__
            print("printing data")
            print(data)
            create_context(fb_id,"intent_type",None)
        #     TODO:set the context to need or update medicine
        elif intent == Query_medicine:
            if not parameter.get("drug", None) is None:
                drug = parameter["drug"]
                # TODO GET BRAND NAME IF DRUGNAME IS GIVEN
                trade_name = search_trade_for_drug(fb_id, drug)
                create_context(fb_id,"MISSING_QTY", (trade_name))

            else:
                #Todo : brand not present in json
                brand = parameter["brand"]
                create_context(fb_id, "MISSING_QTY", (brand))

            if not parameter.get("number", None) is None:
                quantity = parameter["number"]
                generic_data = query_medicine_response_builder(fb_id, brand, quantity)
                data = generic_data.__dict__
            else:
                # TODO Handle case when user texts only with medicine name
                util.create_context(fb_id, "MISSING_QTY", (brand))
                data = text_template(fb_id, "How much quantity do you need?")
        else:
            #TODO:handle case for update medicine
            list_of_med = get_med_for_user(fb_id)
            display_msg = "Medicine quantity can only be reduced here.\nTo update new medicine, kindly contact your" \
                         "pharmacy\nGiven below is the list of medicines whose quantity you may reduce\n"
            for med_list in list_of_med:
                display_msg+="\n"+med_list+"\n"
            data = text_template(fb_id,display_msg+"\nWhich medicine's quantity do you want to reduce?")
            create_context(fb_id,"reduce_qty",None)


    elif context =="intent_type":
        util.remove_context(fb_id)
        if fb_text["postback"]["payload"]=="NEED":
            data = text_template(fb_id,"Which medicine do you need?")

            create_context(fb_id, "need_med", None)
        elif fb_text["postback"]["payload"]=="UPDATE":
            data = text_template(fb_id,"Which medicine do you want to update?")
            create_context(fb_id, "update_med", None)

    elif context == "need_med":
            util.remove_context(fb_id)
            med_name = fb_text['message']['text']
            data = text_template(fb_id, "How much quantity?")
            create_context(fb_id, "MISSING_QTY", (med_name))

    elif context == "update_med":
            util.remove_context(fb_id)
            med_name = fb_text['message']['text']
            data = text_template(fb_id,"How much quantity of "+med_name+" is left?")
            #Todo: Mention previous quantity
            create_context(fb_id, "reduce_qty", (med_name))



    elif context == "MISSING_QTY":
        brand = util.get_context_data(fb_id)
        util.remove_context(fb_id)
        quantity = fb_text['message']['text']
        generic_data = query_medicine_response_builder(fb_id, brand, quantity)
        data = generic_data.__dict__


    elif context == "reduce_qty":
        util.remove_context(fb_id)
        name_of_med = fb_text['message']['text']
        data = text_template(fb_id, "What quantity of "+name_of_med+" medicine is left?")
        create_context(fb_id, "upload_qty", (name_of_med))

    elif context == "upload_qty":
        medi_name = util.get_context_data(fb_id)
        util.remove_context(fb_id)
        qty_of_med = fb_text['message']["text"]
        #Todo: med_id is unique for every batch id?
        update_quantity(fb_id, medi_name, qty_of_med)
        button1 = buttons("postback", title="YES", payload="YES")
        button2 = buttons("postback", title="NO", payload="NO")
        data = button_template_class(fb_id, "The quantity of "+medi_name+" has been successfully updated, want to"
                                            "update more medicine?", buttons=[button1.__dict__, button2.__dict__]).__dict__
        create_context(fb_id,"more_updation",None)


    elif context == "more_updation":
        util.remove_context(fb_id)
        if fb_text["postback"]["payload"]=="YES":
            data = text_template(fb_id, "Which medicine do you want to update?")
            create_context(fb_id, "reduce_qty", None)
        else:
            data = text_template(fb_id, "Thank you for updating!")

    reply(data)


def reply(data):
    json_data = json.dumps(data)
    print("What is this json data")
    print(json_data)
    req = requests.post("https://graph.facebook.com/v2.6/me/messages",params={"access_token": token}, \
                        headers={"Content-Type": "application/json"},data=json_data)
    print(req.content)


@app.route('/webhook', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        if (request.args.get('hub.verify_token', '') == "varsha"):
            print("succefully verified")

            return request.args.get('hub.challenge', '')
    else:
        print("got a message")
        a = request.get_json()
        print(a)
        fb_id = a['entry'][0]['messaging'][0]['sender']['id']

        if not search_user(fb_id):
            file_names = os.listdir(os.path.dirname(__file__))
            if str(fb_id) + ".txt" in file_names:
                with open(str(fb_id) + "_status" + ".txt", "r") as f:
                    status = f.readline()

                if status == "adding_name":
                    name = a['entry'][0]['messaging'][0]['message']['text']
                    #v_name = validate_name(fb_id,name)
                    with open(str(fb_id) + ".txt", "a") as f:
                        f.write(name + "\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("adding_number")
                    phone_number_data = quick_reply_template_class(quick_reply_type.phone_number)
                    data = text_template(fb_id, "please give your phone number", quick_reply=True,
                                         type=[quick_reply_type.phone_number], data=[phone_number_data.__dict__])

                if status == "adding_number":
                    number = a['entry'][0]['messaging'][0]['message']['text']
                    #number = validate_phone(fb_id, number)

                    with open(str(fb_id) + ".txt", "a") as f:
                        f.write(number + "\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("getting email")
                    email_data = quick_reply_template_class(quick_reply_type.email)
                    data = text_template(fb_id, "please give us your email", quick_reply=True,
                                         type=[quick_reply_type.email], data=[email_data.__dict__])

                if status == "getting email":
                    email = a['entry'][0]['messaging'][0]['message']['text']
                    #email = validate_email(fb_id, email)
                    with open(str(fb_id) + ".txt", "a") as f:
                        f.write(email + "\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("getting location")
                    location_data = quick_reply_template_class(quick_reply_type.location)
                    data = text_template(fb_id, "please give your location", quick_reply=True,
                                         type=[quick_reply_type.email], data=[location_data.__dict__])

                if status == "getting location":
                    lat = a['entry'][0]['messaging'][0]['message']["attachments"][0]["payload"]["coordinates"]["lat"]
                    long = a['entry'][0]['messaging'][0]['message']["attachments"][0]["payload"]["coordinates"]["long"]
                    #v_lat, v_long = validate_location(fb_id, lat, long)
                    location = str(lat) + ":" + str(long)

                    with open(str(fb_id) + ".txt", "r") as f:
                        user_name = f.readline()
                        user_phone = f.readline()
                        user_email = f.readline()
                        user_location = f.readline()
                    insert_query_users(user_name, location, user_phone, user_email, fb_id)
                    os.remove(str(fb_id) + ".txt")
                    os.remove(str(fb_id) + "_status" + ".txt")
                    data = text_template(fb_id, "Thank you for registering with us")
                    f = open('welcome_message.txt','r')
                    file_contents=f.read()
                    data = text_template(fb_id, file_contents)

            else:
                fd = open(str(fb_id) + ".txt", "w")
                fd.close()
                with open(str(fb_id) + "_status" + ".txt", "w") as f:
                    status = f.write("adding_name")
                data = text_template(fb_id, "Hey! This is your first message, what's your name ?")

            thread1 = threading.Thread(target=reply, args=(data,))
        else:
            fb_text = a['entry'][0]['messaging'][0]
            thread1 = threading.Thread(target=reply_for_query, args=(fb_id, fb_text,))

        print("Starting thread")
        thread1.start()

    return "ok"

def validate_name(fb_id,name):
    while True:
        if not re.match("^[[A-Za-z_]+[ ']*[A-Za-z_]*]+$", name):
            data = text_template(fb_id, "Please enter a valid name")
        else:
            break
    return name

def validate_phone(fb_id, number):
    while True:
        if not re.match("^[789]\d{9}$", number):
            data = text_template(fb_id, "Please enter a valid phone number")
        else:
            break
    return number

def validate_email(fb_id, email):
    while True:
        if not re.match(
                "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                email):
            data = text_template(fb_id, "Please enter a valid email")
        else:
            break
    return email


def validate_location(fb_id, lat, long):
    while True:
        if not ((re.match("^[-+]?[0-9]*\.?[0-9]+$", lat)) and (re.match("^[-+]?[0-9]*\.?[0-9]+$", long))):
            data = text_template(fb_id, "Please enter a valid location")
        else:
            break
    return lat, long

def get_shop_name(xyz):
    return "pass"

def send_bill_information(cust_id,**kwargs):
    mydict={'username': 'vivek', 'phone': '8088432316', 'email': 'vivekstarstar', 'data': [{'batch_id': 'p302', 'qty': '1', 'med_id': '202'}, {'batch_id': 'p302', 'qty': '1', 'med_id': '202'}]}

    phone_number = mydict['phone']
    shop_name=get_shop_name(cust_id)

    recipient_id = search_by_phone(phone_number)

    text="Hey thanks for billing at "+shop_name+"! Following is your bill information \n"
    display_bill = []
    total_cost=0
    for medicine in mydict['data']:
        batch_id=medicine['batch_id']
        med_id=medicine['med_id']
        (mfg,exp,cost) = get_med_data(batch_id,med_id)
        drug,trade=get_drug_trade(med_id)
        qty=medicine["qty"]
        tcost=int(qty)*int(cost)
        temp="tablate:"+trade+",qty:"+qty+",cost:"+str(tcost)+",exp:"+str(exp)+"\n"
        total_cost+=tcost
        text+=temp
    text+="total cost:"+str(total_cost)+"\n"
    print(text)
    if not recipient_id is None:
        data = text_template_class(recipient_id,text,subscription_message=True).__dict__
        print(data)
        reply(data)
    else:
        # Todo:send mail to this new user
        gmail_user = ''
        gmail_password = ''
        #TODO: how to get email of this customer
        customer_email = mydict['email']
        sent_from = gmail_user
        to = [customer_email]
        subject = 'Medicine Bot to share medicines!'
        body = "Dear Customer,\nIf you would like to share the extra medicines bought by you now, kindly like our" \
               "facebook page, In Zone drug remedy\n" \
               "Thanks!"

        email_text = """\  
        %s
        """ % (sent_from, ", ".join(to), subject, body)
        message = 'Subject: {}\n\n{}'.format(subject, email_text)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(sent_from, to, message)
            server.close()

            print('Email sent!')
        except:
            print('Something went wrong...')


# def reply_for_request():
#     a = request.get_json()
#     fb_id = a['entry'][0]['messaging'][0]['sender']['id']
#     with open(str(fb_id) + "_requested_full_qty" + ".txt", "r") as f:
#         uploader_cust_id = f.readline()
#         uploader_uname = f.readline()
#         uploader_location = f.readline()
#         uploader_phoneno = f.readline()
#         uploader_email = f.readline()
#         uploader_qty = f.readline()
#     os.remove(str(fb_id) + "_requested_full_qty" + ".txt")
#     data_name = text_template(fb_id, uploader_uname)
#     json_data_name = json.dumps(data_name)
#     print(json_data_name)

    # with open(str(fb_id) + "_requested_less_qty" + ".txt", "r") as f:
    #     uploader_cust_id_1 = f.readline()
    #     uploader_uname_1 = f.readline()
    #     uploader_location_1 = f.readline()
    #     uploader_phoneno_1 = f.readline()
    #     uploader_email_1 = f.readline()
    #     uploader_qty_1 = f.readline()
    # os.remove(str(fb_id) + "_requested_less_qty" + ".txt")
    # data_name_1 = text_template(fb_id, uploader_uname_1)
    # json_data_name_1 = json.dumps(data_name)
    # print(json_data_name_1)


#@app.route('/varsha',methods=['GET', 'POST'])
 # def another():
 #     x=request.get_json()
 #     print(x)
 #     return "hello"



if __name__ == '__main__':
    # send_bill_information(1835953359813263)
    app.run(port=8000, debug=True)

