from google.appengine.dist import use_library
use_library('django', '1.3')
import logging
import uuid
from basepages import BaseHandler
from data import SwimmerData
from request import make_gco_request
from util import NamoException, verify_age
from google.appengine.ext import db
import datetime
from django.utils.safestring import mark_safe

def get_swim_event_price(swim_event):
    prices_early = {'keiki' : 10.00,
                    'half mile': 25.00,
                    '1 mile': 30.00,
                    '2 mile': 30.00}
    prices_late = {'keiki' : 15.00,
                    'half mile': 35.00,
                    '1 mile': 40.00,
                    '2 mile': 40.00}

    n = datetime.datetime.now()
    cutoff = datetime.datetime(year=2012, month=7, day=16)
    if n < cutoff:
        d = prices_early
    else:
        d = prices_late

    try:
        return d[swim_event]
    except Exception:
        return 0.0

def get_swim_events():
    return ['keiki', 'half mile', '1 mile', '2 mile']

def get_swim_order_lookup(xid):
    query = db.Query(SwimmerData)
    query.filter('transaction_id =', xid)
    orders = query.fetch(limit=2)
    if not orders:
        return None
    if len(orders) > 1:
        # raise error saying to refresh their page and delete anything bad from db
        logging.error("There are two orders with ID %s **BAD**" % (xid))
    return orders[0]

def get_swim_order_by_gon(sn):
    query = db.Query(SwimmerData)
    query.filter('googleordernumber =', sn)
    orders = query.fetch(limit=10)
    if not orders:
        return None
    if len(orders) > 1:
        logging.error("There are two orders with SN %s **BAD**" % (sn))
    return orders[0]


def get_all_swim_orders():
    query = db.Query(SwimmerData)
    query.order("lastname")
    orders = query.fetch(limit=1000)
    return orders

class SwimReportHandler(BaseHandler):
    def page_logic(self):
        swim_data_array = get_all_swim_orders()
        self.template_values['swim_data_array'] = swim_data_array
        self.write_page('swimreport.html')

class SwimFinalHandler(BaseHandler):
    def page_logic(self):
        swim_data_array = get_all_swim_orders()
        self.template_values['swim_data_array'] = swim_data_array
        self.write_page('swimfinal.html')

class SwimRegisterHandler(BaseHandler):

    def page_logic(self):
        first_name = self.get_request_value_normalized('ncc_firstname', must=True, label="First Name")
        last_name = self.get_request_value_normalized('ncc_lastname', must=True, label="Last Name")
        swim_event = self.get_request_value_normalized('ncc_swim_event', must=True, label="Swim Event")
        email = self.get_request_value_normalized('ncc_emailaddr')
        phone = self.get_request_value_normalized('ncc_phone')
        agree = self.get_request_value_normalized('ncc_agreement')
        transaction = str(uuid.uuid4())
        gender = self.get_request_value_normalized('ncc_gender', must=True, label="Gender")
        age = self.get_request_value_normalized('ncc_age', must=True, label="Age")
        shirt_size = self.get_request_value_normalized('ncc_shirtsize', must=True, label="Shirt Size")

        if not agree:
            raise NamoException("You must read and agree to the release form.")

        if gender not in ["male", "female"]:
            raise NamoException("Invalid gender")
        age = verify_age(age)
        if swim_event not in get_swim_events():
            raise NamoException("Invalid event name.")
        if agree != "agree":
            raise NamoException("You must agree to the wavier in order to participate in the event.")
        swim_data = get_swim_order_lookup(transaction)
        if swim_data:
            logging.error("The transaction ID already exists, what to do?")
            raise NamoException("The transaction ID already exists, what to do?")

        description = "Namolokama Swim Race.  Course %s." % (swim_event)
        event_name = swim_event

        price = get_swim_event_price(swim_event)
        swim_data = SwimmerData(description=description, event_name=event_name, phone=phone, swim_event=swim_event,
                                firstname=first_name, lastname=last_name, gender=gender, age=age, agreed=True,
                                emailaddress=email, transaction_id=transaction, price=price, shirt_size=shirt_size)
        swim_data.put()

        html = make_gco_request(swim_data)
        button_value = html()

        button_value = mark_safe(button_value)
        logging.error("html button | %s" % (button_value))

        self.template_values['button'] = button_value
        self.write_page('checkout.html')

class SwimHandler(BaseHandler):
    def page_logic(self):
        n = datetime.datetime.now()
        cutoff = datetime.datetime(year=2012, month=7, day=24)

        if n > cutoff:
            self.write_page('swimclosed.html')
            return

        self.template_values['events'] = get_swim_events()
        self.template_values['price'] = get_swim_event_price("")
        self.write_page('swim.html')
