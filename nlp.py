try:

    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

    )



def apiai_query(msg):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = str(uuid.uuid1())
    request.query = msg
    response = request.getresponse()
    data = response.read()

    data1 = json.loads(data)
    data2=data1["result"]["parameters"]["number"]
    data3=data1["result"]["parameters"]["medicines"]
    return data2,data3
