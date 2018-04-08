from flask import Flask, request
from werkzeug.contrib.cache import SimpleCache
from model import med_query, insert_query_users, search_user_for_med, current_user, search_user
from uitemplates import button_template, text_template, quick_reply_type, quick_reply_template_class, \
    generic_template_class
from nlp import apiai_query, Query_medicine, Upload_medicine, General_Talk
from uitemplates import genereic_template_elements, button
import threading
import json
import requests
import os.path
import sys
import uuid
import nlp
import util
from geopy.distance import vincenty
import gpxpy.geo
from math import radians

threshold = 0
token = "EAACGHzJZBmDABAOlZAEPVM2ikVWHx8hlMzmTZCO6l3s3kWMjQo5oywc0H8NK3IfMehFoEIHRS4W0w6REcfKWzxy7P9qAayTZBeVVZCpcU7KdSbC4rhiZBYMMryYLZCf0QEmEJSBqNSEZBJy7fEQmT7MQdoWYqTLEZBJOxKgkrioYhqv1AYTORC8Uu"
CLIENT_ACCESS_TOKEN = 'ab47593acb7f45c68ca4ffe296db1885'
session = dict()
# base_url = "https://localhost:8000/"
base_url="https://medecinebot.herokuapp.com/"
static_url = base_url + "static/"
user_url = static_url + "user.jpg"

util

app = Flask(__name__)
app.config['SECRET_KEY'] = "abcdefghijn"


def get_location_url(lat, long):
    return "https://www.google.com/maps/search/?api=1&query=" + str(lat) + "," + str(long)



def query_medicine_responce_builder(fb_id, brand, quantity):
    distance = []
    potential_vendor_information, impotential_vendor_information = search_user_for_med(fb_id, quantity,
                                                                                       brand)
    current_user_location = current_user(fb_id)
    latitude, longitude = current_user_location.split(":")
    if len(potential_vendor_information) > threshold:
        for obj in potential_vendor_information:
            distance.append(nearest_location(latitude, longitude, obj.lat, obj.long))
    else:
        # TODO : HANDLE CASE WHEN NOBODYA HAS REQUIRED AMOUNT OF MEDICIN
        pass
    dist = sorted(range(len(distance)), key=lambda k: distance[k])
    elements = []
    for i in dist:
        location = get_location_url(obj.lat, obj.long)
        user_name = potential_vendor_information[i].uname
        subtitle = "Phone: " + str(potential_vendor_information[i].phone) + "\nQuantity: " + str(
            potential_vendor_information[i].qty)
        btn = button("web_url", location, "got to location")
        elements.append(genereic_template_elements(user_name, image_url=user_url, subtitle=subtitle,
                                                   button=[btn.__dict__]).__dict__)
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
        intent, parameter = apiai_query(fb_text)

        if intent == General_Talk:
            text1 = quick_reply_template_class("type", title="need medicine", image_url="", payload="medicine.need")
            text2 = quick_reply_template_class("type", title="update medicine", image_url="", payload="medicine.update")
            data = text_template(fb_id, "How can i help you", quick_reply=True,
                                 type=[quick_reply_type.text, quick_reply_type.text], data=[text1, text2])
        #     TODO:set the context to need or update medicine
        elif intent == Query_medicine:
            if not parameter.get("drug", None) is None:
                drug = parameter["drug"]
            else:
                brand = parameter["drug"]

            brand = drug  # TODO GET BRAND NAME IF DRUGNAME IS GIVEN
            if not parameter.get("number", None) is None:
                quantity = parameter["number"]

                generic_data = query_medicine_responce_builder(fb_id, brand, quantity)
                data = generic_data.__dict__
            else:
                # TODO Handle case when user texts only with medicine name
                util.create_context(fb_id, "MISSING_QTY", (brand))
                data = text_template(fb_id, "How mcuh quantity you need", quick_reply=False)
        else:
            data = text_template(fb_id, "this feature is yet to be implimented", quick_reply=False)



    elif util.get_context(fb_id) == "MISSING_QTY":
        brand = util.get_context_data(fb_id)
        util.remove_context(fb_id)
        quantity = fb_text
        generic_data = query_medicine_responce_builder(fb_id, brand, quantity)
        data = generic_data.__dict__

    reply(data)





def reply(data):
    json_data = json.dumps(data)
    print("What is this json data")
    print(json_data)
    # req = requests.post("https://graph.facebook.com/v2.6/me/messages",params={"access_token": token}, headers={"Content-Type": "application/json"},data=json_data)
    # print(req.content)


@app.route('/webhook', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        if (request.args.get('hub.verify_token', '') == "varsha"):
            print("succefully verified")

            return request.args.get('hub.challenge', '')
    else:
        print("got a message")
        a = request.get_json()
        fb_id = a['entry'][0]['messaging'][0]['sender']['id']

        print(fb_id)

        if not search_user(fb_id):
            file_names = os.listdir(os.path.dirname(__file__))
            if str(fb_id) + ".txt" in file_names:
                with open(str(fb_id) + "_status" + ".txt", "r") as f:
                    status = f.readline()

                if status == "adding_name":
                    name = a['entry'][0]['messaging'][0]['message']['text']
                    with open(str(fb_id) + ".txt", "a") as f:
                        f.write(name + "\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("adding_number")
                    phone_number_data = quick_reply_template_class(quick_reply_type.phone_number)
                    data = text_template(fb_id, "please give your phone number", quick_reply=True,
                                         type=[quick_reply_type.phone_number], data=[phone_number_data.__dict__])

                if status == "adding_number":
                    number = a['entry'][0]['messaging'][0]['message']['quick_reply']['payload']
                    with open(str(fb_id) + ".txt", "a") as f:
                        f.write(number + "\n")
                    with open(str(fb_id) + "_status" + ".txt", "w") as f:
                        f.write("getting email")
                    email_data = quick_reply_template_class(quick_reply_type.email)
                    data = text_template(fb_id, "please give us your email", quick_reply=True,
                                         type=[quick_reply_type.email], data=[email_data.__dict__])

                if status == "getting email":
                    email = a['entry'][0]['messaging'][0]['message']['quick_reply']['payload']
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


def reply_for_request():
    a = request.get_json()
    fb_id = a['entry'][0]['messaging'][0]['sender']['id']
    with open(str(fb_id) + "_requested_full_qty" + ".txt", "r") as f:
        uploader_cust_id = f.readline()
        uploader_uname = f.readline()
        uploader_location = f.readline()
        uploader_phoneno = f.readline()
        uploader_email = f.readline()
        uploader_qty = f.readline()
    os.remove(str(fb_id) + "_requested_full_qty" + ".txt")
    data_name = text_template(fb_id, uploader_uname)
    json_data_name = json.dumps(data_name)
    print(json_data_name)

    with open(str(fb_id) + "_requested_less_qty" + ".txt", "r") as f:
        uploader_cust_id_1 = f.readline()
        uploader_uname_1 = f.readline()
        uploader_location_1 = f.readline()
        uploader_phoneno_1 = f.readline()
        uploader_email_1 = f.readline()
        uploader_qty_1 = f.readline()
    os.remove(str(fb_id) + "_requested_less_qty" + ".txt")
    data_name_1 = text_template(fb_id, uploader_uname_1)
    json_data_name_1 = json.dumps(data_name)
    print(json_data_name_1)


# @app.route('/varsha',methods=['GET', 'POST'])
# # def another():
# #     x=request.get_json()
# #     print(x)
# #     return "hello"


# print(data['res'])
# json.loads(var1)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
