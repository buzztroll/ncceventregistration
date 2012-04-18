import logging
from data import GoogleCheckoutData
from util import get_site_url, NamoException
from gchecky.controller import Controller
from gchecky import model as gmodel
from google.appengine.ext import db

def get_merchant_info():
    query = db.Query(GoogleCheckoutData)
    merch = query.fetch(limit=1)
    if not merch:
        # add a blank entry so i can edit it later
        x = GoogleCheckoutData(merchant_id="X", merchant_key="X")
        x.put()
        raise NamoException("This website is not yet ready.  Please check back later.")
    return merch[0]


def make_gco_request(rd):

    merch_info = get_merchant_info()

    controller = Controller(str(merch_info.merchant_id), str(merch_info.merchant_key), is_sandbox=merch_info.sandbox)

    shopping_cart = gmodel.shopping_cart_t(items = [
        gmodel.item_t(merchant_item_id = rd.transaction_id,
                      name             = rd.event_name,
                      description      = rd.description,
                      unit_price       = gmodel.price_t(value    = rd.price,
                                                        currency = 'USD'),
                      quantity = 1)
       ])

    checkout_flow_support = gmodel.checkout_flow_support_t(
        continue_shopping_url = get_site_url(),
        request_buyer_phone_number = False)

    order = gmodel.checkout_shopping_cart_t(shopping_cart=shopping_cart, checkout_flow_support=checkout_flow_support)

    prepared = controller.prepare_order(order)

    logging.info(prepared.html)

    return prepared.html

