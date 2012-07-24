from google.appengine.ext import db

class GoogleCheckoutData(db.Model):
    merchant_id = db.StringProperty(required=True)
    merchant_key = db.StringProperty(required=True)
    sandbox = db.BooleanProperty(required=True, default=True)

class EventBaseData(db.Model):
    googleordernumber = db.StringProperty(required=False)
    firstname = db.StringProperty(required=True)
    lastname = db.StringProperty(required=True)
    payment_state = db.StringProperty(required=True, default="INITIAL")
    emailaddress = db.StringProperty()
    transaction_id = db.StringProperty(required=True)
    gender = db.StringProperty(required=True)
    age = db.IntegerProperty(required=True)
    agreed = db.BooleanProperty(default=False, required=True)
    price = db.FloatProperty(required=True)
    description = db.StringProperty(required=True)
    event_name = db.StringProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add=True)

class SwimmerData(EventBaseData):
    phone = db.StringProperty()
    swim_event = db.StringProperty(required=True)
    shirt_size = db.StringProperty(required=False)

class RacersData(EventBaseData):
    second_paddler_firstname = db.StringProperty(required=False)
    second_paddler_lastname = db.StringProperty(required=False)
    second_paddler_age = db.IntegerProperty(required=False)
    second_paddler_gender = db.StringProperty(required=False)
    boatnumber = db.StringProperty(required=True)
    boattype = db.StringProperty(required=True)

