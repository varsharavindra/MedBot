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

def text_template(fb_id,fb_text):
    text_data = {
        "messaging_type": "RESPONSE",
        "recipient": {
            "id": fb_id
        },
        "message": {

            "text": fb_text
        }
    }
    return text_data
