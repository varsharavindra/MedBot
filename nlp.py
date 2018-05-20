import uuid
import json
import os
import apiai
import sys
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger('stack')


try:

    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

    )


CLIENT_ACCESS_TOKEN = ''

General_Talk="I0"
Query_medicine= "I1"
Upload_medicine= "I2"

def apiai_query(msg):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = str(uuid.uuid1())
    request.query = msg
    response = request.getresponse()
    data = response.read()

    data1 = json.loads(data)
    print(data1)
    if data1["result"]["source"] == "domains":
        return General_Talk,data1["result"]["fulfillment"]["speech"],
    else:
        if data1["result"]["metadata"]["intentName"] == Query_medicine:
            return Query_medicine, data1["result"]["parameters"],
        else:
            if data1["result"]["metadata"]["intentName"] == Upload_medicine:
                return Upload_medicine, "None"

# print(data['res'])
#json.loads(var1)

if __name__ == '__main__':
    msg=apiai_query("hey i want 5 crocin")
    print (msg)
