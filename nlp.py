import uuid
import json
import os
import apiai
import sys


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
    if data1["result"]["source"] == "domains":
        return General_Talk,data1["result"]["fulfillment"]["speech"],
    else:
        if data1["result"]["metadata"]["intentName"] == Query_medicine:
            return Query_medicine, data1["result"]["parameters"]
        else:
            if data1["result"]["metadata"] == Upload_medicine:
                return Upload_medicine, "None"

# print(data['res'])
#json.loads(var1)

if __name__ == '__main__':
    msg=apiai("How to update my crocin tablets?")
    print (msg)