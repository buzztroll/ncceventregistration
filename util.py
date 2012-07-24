import logging
from google.appengine.api import mail

def verify_age(age):
    try:
        age = int(age)
    except Exception, ex:
        logging.error("Invalid age %s" % (str(age)))
        raise NamoException("Invalid age description")
    if age < 1 or age > 110:
        raise NamoException("Invalid age")
    return age

def send_email(rd, adminonly=True, subject=""):
    sender = "buzztroll@gmail.com"
    recepient_list = []
    if not adminonly:
        recepient_list = ["john@bresnahan.me"]
    recepient_list.append(sender)

    subject = "Race payment status is now %s" % (rd.payment_state)
    message = "%s %s is not in the state %s.  SN=%s\n%s" % (rd.firstname, rd.lastname, rd.payment_state, rd.googleordernumber, rd.description)

    mail.send_mail(
        to=recepient_list,
        subject=subject,
        body=message,
        reply_to=sender,
        sender=sender)

g_events_dict = {"oc1" : 35.00, "surfski": 35.00, "sup": 35.00, "oc2": 40.00, "paddleboard": 35.00}

def get_boat_types():
    global g_events_dict
    return g_events_dict.keys()

def get_event_price(type):
    global g_events_dict
    return g_events_dict[type]

class NamoException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

def get_site_url():
    return 'http://www.namolokama.com/'
