from flask import Flask, request
from werkzeug.contrib.cache import SimpleCache
from model import med_query, insert_query_users, search_user_for_med, current_user, search_user
from uitemplates import button_template, text_template, quick_reply_type, quick_reply_template_class, \
    generic_template_class
from nlp import apiai_query, Query_medicine, Upload_medicine, General_Talk
from uitemplates import genereic_template_elements, buttons,button_template_class
from util import *
import threading
import json
import requests
import os.path
import sys
import uuid
import nlp
import util
import re

import gpxpy.geo
from math import radians

threshold = 0
token = ""
CLIENT_ACCESS_TOKEN = ''
google_places_api_key=""
session = dict()
# base_url = "https://localhost:8000/"
base_url="https://medecinebot.herokuapp.com/"
static_url = base_url + "static/"
user_url = static_url + "user.jpg"

util

app = Flask(__name__)
app.config['SECRET_KEY'] = ""


def get_location_url(lat, long):
    return "https://www.google.com/maps/search/?api=1&query=" + str(lat) + "," + str(long)



def query_medicine_responce_builder(fb_id, brand, quantity):
    potential_distance = []
    potential_vendor_information, impotential_vendor_information = search_user_for_med(fb_id, quantity,
                                                                                       brand)
    current_user_location = current_user(fb_id)
    latitude, longitude = current_user_location.split(":")
    if len(potential_vendor_information) > threshold:
        for obj in potential_vendor_information:
            potential_distance.append(nearest_location(latitude, longitude, obj.lat, obj.long))
    else:
        impotential_distance = []
        for obj in impotential_vendor_information:
            impotential_distance.append(nearest_location(latitude, longitude, obj.lat, obj.long))

    potential_dist = sorted(range(len(potential_distance)), key=lambda k: potential_distance[k])
    impotential_dist = sorted(range(len(impotential_distance)), key=lambda k: impotential_distance[k])
    elements = []
    for i in potential_dist:
        location = get_location_url(obj.lat, obj.long)
        user_name = potential_vendor_information[i].uname
        subtitle = "Phone: " + str(potential_vendor_information[i].phone) + "\nQuantity: " + str(
            potential_vendor_information[i].qty)
        btn = buttons("web_url", location, "go to location in maps")
        elements.append(genereic_template_elements(user_name, image_url=user_url, subtitle=subtitle,
                                                   buttons=[btn.__dict__]).__dict__)
    generic_data = generic_template_class(fb_id, elements)

    elements1 = []
    for i in impotential_dist:
        location1 = get_location_url(obj.lat,obj.long)
        user_name1 = impotential_vendor_information[i].uname
        subtitle1 = "Phone: " + str(impotential_vendor_information[i].phone) + "\nQuantity: " + str(
            impotential_vendor_information[i].qty)
        btn1 = buttons("web_url",location,"Go to location in maps")
        elements1.append(genereic_template_elements(user_name1,image_url=user_url, subtitle=subtitle1,
                                                   buttons=[btn1.__dict__]).__dict__)
    generic_data = generic_template_class(fb_id, elements)

    if not potential_vendor_information and impotential_vendor_information:
        request_pharmacy=requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?\
        location="+latitude+","+longitude+"&type=pharmacy&radius=1000&key="+google_places_api_key)
        print(request_pharmacy.content)
        pharmacy_data = request_pharmacy.json()
        # print(pharmacy_data['results'][0]['geometry']['location']['lat'])
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
            elements.append(genereic_template_elements(pharma_name, image_url=user_url, subtitle=False,
                                                       buttons=[btn1.__dict__]).__dict__)
        generic_data = generic_template_class(fb_id, elements)


    return generic_data


def nearest_location(lat1, long1, lat2, long2):
    latitude1 = radians(float(lat1))
    longitude1 = radians(float(long1))

    latitude2 = radians(float(lat2))
    longitude2 = radians(float(long2))

    dist = gpxpy.geo.haversine_distance(latitude1, longitude1, latitude2, longitude2)
    return dist


def reply_for_query(fb_id, fb_text):
    distance = []
    if util.get_context(fb_id) is None:
        text = fb_text["text"]
        intent, parameter = apiai_query(fb_text)

        if intent == General_Talk:
            button1=buttons("postback",title="Need Medicine",payload="NEED")
            button2 = buttons("postback", title="Upload Medicine", payload="UPDATE")
            data = button_template_class("How may I help you?",buttons=[button1,button2])
            create_context(fb_id,"intent_type",None)
        #     TODO:set the context to need or update medicine
        elif intent == Query_medicine:
            if not parameter.get("drug", None) is None:
                drug = parameter["drug"]
                brand = drug
            else:
                brand = parameter["brand"]

              # TODO GET BRAND NAME IF DRUGNAME IS GIVEN
            if not parameter.get("number", None) is None:
                quantity = parameter["number"]

                generic_data = query_medicine_responce_builder(fb_id, brand, quantity)
                data = generic_data.__dict__
            else:
                # TODO Handle case when user texts only with medicine name
                util.create_context(fb_id, "MISSING_QTY", (brand))
                data = text_template(fb_id, "How much quantity do you need?")
        else:
            data = text_template(fb_id, "This feature is yet to be implemented", quick_reply=False)


    elif util.get_context(fb_id) =="intent_type":
        util.remove_context(fb_id)
        if fb_text["postback"]["payload"]=="NEED":
            data = text_template(fb_id,"Which medicine do you need?")
            need_med = fb_text["text"]
            create_context(fb_id, "need_med", (need_med))
        elif fb_text["postback"]["payload"]=="UPDATE":
            data = text_template(fb_id,"Which medicine do you want to update?")
            update_med = fb_text["text"]
            create_context(fb_id, "update_med", (update_med))

        if util.get_context(fb_id) == "need_med":
            med_name = util.get_context_data(fb_id)
            util.remove_context(fb_id)
            data = text_template(fb_id, "How much quantity?")
            create_context(fb_id, "MISSING_QTY", (med_name))

        elif util.get_context(fb_id) == "update_med":
            med_name = util.get_context_data(fb_id)
            util.remove_context(fb_id)
            data = text_template(fb_id,"How much quantity?")
            create_context(fb_id, "qty", (med_name))



        elif util.get_context(fb_id) == "MISSING_QTY":
            brand = util.get_context_data(fb_id)
            util.remove_context(fb_id)
            quantity = fb_text["text"]
            generic_data = query_medicine_responce_builder(fb_id, brand, quantity)
            data = generic_data.__dict__


        elif util.get_context(fb_id) == "qty":
            trade_name = util.get_context_data(fb_id)
            util.remove_context(fb_id)
            quantity = fb_text["text"]







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
                    while True:
                        if re.match("^[[A-Za-z_]+[ ']*[A-Za-z_]*]+$", name):
                            break
                        else:
                            data = text_template(fb_id,"Please enter a valid name")
                    with open(str(fb_id) + ".txt", "a") as f:
                        f.write(name + "\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("adding_number")
                    phone_number_data = quick_reply_template_class(quick_reply_type.phone_number)
                    data = text_template(fb_id, "please give your phone number", quick_reply=True,
                                         type=[quick_reply_type.phone_number], data=[phone_number_data.__dict__])

                if status == "adding_number":
                    number = a['entry'][0]['messaging'][0]['message']['text']
                    while True:
                        if re.match("^[789]\d{9}$", number):
                            break
                        else:
                            data = text_template(fb_id,"Please enter a valid phone number")
                    with open(str(fb_id) + ".txt", "a") as f:
                        f.write(number + "\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("getting email")
                    email_data = quick_reply_template_class(quick_reply_type.email)
                    data = text_template(fb_id, "please give us your email", quick_reply=True,
                                         type=[quick_reply_type.email], data=[email_data.__dict__])

                if status == "getting email":
                    email = a['entry'][0]['messaging'][0]['message']['text']
                    while True:
                        if re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email):
                            break
                        else:
                            data = text_template(fb_id,"Please enter a valid email")
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
                    while True:
                        if ((re.match("^[-+]?[0-9]*\.?[0-9]+$", lat)) and (re.match("^[-+]?[0-9]*\.?[0-9]+$", lat))):
                            break
                        else:
                            data = text_template(fb_id,"Please enter a valid location")
                    location = str(lat) + ":" + str(long)

                    with open(str(fb_id) + ".txt", "r") as f:
                        user_name = f.readline()
                        user_phone = f.readline()
                        user_email = f.readline()
                        user_location = f.readline()
                    insert_query_users(user_name, location, user_phone, user_email, fb_id)
                    os.remove(str(fb_id) + ".txt")
                    os.remove(str(fb_id) + "_status" + ".txt")
                    data = text_template(fb_id, "thank you for registering with us")
                    f = open('welcome_message.txt','r')
                    file_contents=f.read()
                    data = text_template(fb_id, file_contents)

            else:
                fd = open(str(fb_id) + ".txt", "w")
                fd.close()
                with open(str(fb_id) + "_status" + ".txt", "w") as f:
                    status = f.write("adding_name")
                data = text_template(fb_id, "hey this is your first message,whats your name ?")

            thread1 = threading.Thread(target=reply, args=(data,))
        else:
            fb_text = a['entry'][0]['messaging'][0]['message']
            thread1 = threading.Thread(target=reply_for_query, args=(fb_id, fb_text,))

        print("Starting thread")
        thread1.start()

    return "ok"

def receive_bill_data(fb_id):
    bill_request = requests.get("")
    bill_json = bill_request.json()


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


# print(data['res'])
# json.loads(var1)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
