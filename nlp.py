import uuid
import json
import os
import apiai
try:

    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

    )


CLIENT_ACCESS_TOKEN = ''


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
        return data1["result"]["fulfillment"]["speech"],"I0"
    else:
        if data1["result"]["metadata"]["intentName"] == "I1":
            return data1["result"]["parameters"]["number"]
        else:
            if data1["result"]["metadata"] == "I2":
                return None

# print(data['res'])
#json.loads(var1)

if __name__ == '__main__':
    msg=main("How to update my crocin tablets?")
    print (msg)