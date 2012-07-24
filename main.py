#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.dist import use_library
use_library('django', '1.3')

import cgi
import logging
import uuid
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from basepages import BaseHandler
from swimapp import SwimHandler, SwimRegisterHandler, SwimReportHandler, get_swim_order_lookup, get_swim_order_by_gon, SwimFinalHandler
from util import NamoException, get_boat_types, send_email, get_event_price, verify_age
from request import make_gco_request
from data import RacersData
from google.appengine.ext import db


def get_race_order_lookup(xid):
    query = db.Query(RacersData)
    query.filter('transaction_id =', xid)
    orders = query.fetch(limit=10)
    if not orders:
        return None
    if len(orders) > 1:
        # raise error saying to refresh their page and delete anything bad from db
        logging.error("There are two orders with ID %s **BAD**" % (xid))
    return orders[0]

def get_race_order_by_gon(sn):
    query = db.Query(RacersData)
    query.filter('googleordernumber =', sn)
    orders = query.fetch(limit=10)
    if not orders:
        return None
    if len(orders) > 1:
        logging.error("There are two orders with SN %s **BAD**" % (sn))
    return orders[0]

def get_order_lookup(xid):
    funcs = [get_race_order_lookup, get_swim_order_lookup]
    for f in funcs:
        x = f(xid)
        if x:
            return x
    return None

def get_order_by_gon(gon):
    funcs = [get_race_order_by_gon, get_swim_order_by_gon]
    for f in funcs:
        x = f(gon)
        if x:
            return x
    return None


def process_rd_state(rd, state):
    if state == 'REVIEWING':
        # Google Checkout is reviewing the order.
        adminonly = True
        mail = False
    elif state == 'CHARGEABLE':
        # The order is ready to be charged.
        adminonly = True
        mail = True
    elif state == 'CHARGING':
        # The order is being charged; you may not refund or cancel an order until is the charge is completed.
        adminonly = True
    elif state == 'CHARGED':
        # The order has been successfully charged; if the order was only partially charged, the buyer's account page will reflect the partial charge.
        adminonly = False
        mail = True
    elif state == 'PAYMENT_DECLINED':
        # The charge attempt failed.
        adminonly = True
        mail = True
    elif state == 'CANCELLED':
        # Either the buyer or the seller canceled the order. An order's financial state cannot be changed after the order is canceled.
        adminonly = False
        mail = True
    elif state == 'CANCELLED_BY_GOOGLE':
        # Google canceled the order. Google may cancel orders due to a failed charge without a replacement credit card being provided within a set period of time or due to a failed risk check.
        adminonly = False
        mail = True
    else:
        mail = False
        logging.info("Unexpected state %s" % (str(state)))

    rd.payment_state = state
    rd.put()
    if mail:
        send_email(rd, adminonly=adminonly)



def get_all_orders():
    query = db.Query(RacersData)
    orders = query.fetch(limit=1000)
    return orders

class ReportHandler(BaseHandler):
    def page_logic(self):
        race_data_array = get_all_orders()
        self.template_values['race_data_array'] = race_data_array
        self.write_page('report.html')

class CallbackHandler(BaseHandler):
    def page_logic(self):
        try:
            self._page_logic()
        except Exception, ex:
            logging.error(ex)

    def _page_logic(self):
        #logging.info(str(self.request))

        logging.info(str(self.request.body))
        qs = cgi.parse_qs(self.request.body.strip())
        logging.info(str(qs))

        type = qs['_type'][0]
        logging.info(type)

        if type == 'new-order-notification':
            trans_id = qs['shopping-cart.items.item-1.merchant-item-id'][0]
            state = qs['financial-order-state'][0].upper()
            rd = get_order_lookup(trans_id)
            if not rd:
                logging.error("No data for transaction ID for %s" % (trans_id))
                logging.error(qs)
                raise Exception("That xid was not found %s"  % (trans_id))
            try:
                rd.serialnumber = qs['serial-number'][0]
                rd.googleordernumber = qs['google-order-number'][0]
                logging.info("adding rd with sn=%s and gon=%s" % (rd.serialnumber, rd.googleordernumber))
                process_rd_state(rd, state)
            except Exception, ex:
                logging.error("An exception occurred trying to set data for %s" % (trans_id))
                raise
        elif type == 'order-state-change-notification':
            logging.info("Order state changed")
            gon = qs['google-order-number'][0]
            logging.info("gon is %s" % (gon))
            state = qs['new-financial-order-state'][0].upper()
            rd = get_order_by_gon(gon)
            if not rd:
                raise NamoException("SN %s not found" % (gon))
            process_rd_state(rd, state)

class OC1Handler(BaseHandler):
    def page_logic(self):
        #self.template_values['boat_types'] = get_boat_types()
        #self.template_values['ncc_transaction_reference'] = str(uuid.uuid4())
        #self.write_page('oc1registration.html')
        self.write_page('closed.html')

class RegisterHandler(BaseHandler):

    def page_logic(self):
        first_name = self.get_request_value_normalized('ncc_firstname', must=True, label="First Name")
        last_name = self.get_request_value_normalized('ncc_lastname', must=True, label="Last Name")
        boat_number = self.get_request_value_normalized('ncc_boat_number', must=True, label="Boat Number")
        boat_type = self.get_request_value_normalized('ncc_boat_type', must=True, label="Boat Type")
        email = self.get_request_value_normalized('ncc_emailaddr')
        agree = self.get_request_value_normalized('ncc_agreement')
        transaction = str(uuid.uuid4())
        gender = self.get_request_value_normalized('ncc_gender', must=True, label="Gender")
        age = self.get_request_value_normalized('ncc_age', must=True, label="Age")

        second_first_name = self.get_request_value_normalized('ncc_second_firstname', must=False)
        second_last_name = self.get_request_value_normalized('ncc_second_lastname', must=False)
        second_age = self.get_request_value_normalized('ncc_second_age', must=False)
        second_gender = self.get_request_value_normalized('ncc_second_gender', must=False)

        if not agree:
            raise NamoException("You must read and agree to the release form.")

        if gender not in ["male", "female"]:
            raise NamoException("Invalid gender")
        age = verify_age(age)

        if boat_type not in get_boat_types():
            raise NamoException("Invalid boat type")
        if agree != "agree":
            raise NamoException("You must agree to the wavier in order to participate in the event.")
        rd = get_race_order_lookup(transaction)
        if rd:
            logging.error("The transaction ID already exists, what to do?")
            raise NamoException("The transaction ID already exists, what to do?")

        description = "Namolokama canoe race.  Watercraft %s" % (boat_type)
        event_name = boat_type
        price = get_event_price(boat_type)
        rd = RacersData(firstname=first_name, lastname=last_name, boatnumber=boat_number, boattype=boat_type,
                        agreed=True,transaction_id=transaction, price=price, emailaddress=email,
                        age=age, gender=gender, description=description, event_name=event_name)

        if boat_type == 'oc2':
            if not second_first_name:
                raise NamoException("For the OC2 event you must register both paddlers")
            if not second_last_name:
                raise NamoException("For the OC2 event you must register both paddlers")
            if not second_age:
                raise NamoException("For the OC2 event you must register both paddler's age")
            if not second_gender:
                raise NamoException("For the OC2 event you must register both paddler's gender")
            second_age = verify_age(second_age)

            rd.second_paddler_firstname = second_first_name
            rd.second_paddler_lastname = second_last_name
            rd.second_paddler_age = second_age
            rd.second_paddler_gender = second_gender

        rd.put()

        html = make_gco_request(rd)

        button_value = html()

        logging.error("html button | %s" % (button_value))

        self.template_values['button'] = button_value
        self.write_page('checkout.html')


def main():
    application = webapp.WSGIApplication([
        ('/', OC1Handler),
        ('/oc1', OC1Handler),
        ('/swim', SwimHandler),
        ('/callback', CallbackHandler),
        ('/report/oc1', ReportHandler),
        ('/report/swim', SwimReportHandler),
        ('/report/swimfinal', SwimFinalHandler),
        ('/oc1/register', RegisterHandler),
        ('/swim/register', SwimRegisterHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
