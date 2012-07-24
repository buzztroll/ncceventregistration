from google.appengine.ext.webapp import template
import os
import logging
from google.appengine.ext import webapp
from google.appengine.api import mail
from util import NamoException, send_email


class BaseHandler(webapp.RequestHandler):
    logged_in = True

    def post(self):
        self.do_page()

    def get(self):
        self.do_page()

    def validate_parameters(self, d):
        for param_name in d:
            (must, label) = d[param_name]
            self.get_request_value_normalized(param_name, must=must, label=label)

    def get_request_value_normalized(self, key, must=False, label=None):
        if label is None:
            label = key

        x = self.request.get(key)
        if x:
            x = x.strip().lower()
        if must and not x:
            raise NamoException("You just enter a value for %s" % (label))
        return x

    def do_page(self):
        try:
            self.template_values = {}
            self.page_logic()
        except NamoException, nex:
            self.template_values['error_message'] = str(nex)
            self.write_page("error.html")
        except Exception, ex:
            logging.log(logging.ERROR, "Error %s." % (str(ex)))
            raise

    def page_logic(self):
        pass


    def write_page(self, template_filename, autoescape=True):
        path = os.path.join(os.path.dirname(__file__), "templates/" + template_filename)
        self.response.out.write(template.render(path, self.template_values))


