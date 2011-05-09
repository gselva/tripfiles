#python
import cgi
import os
from datetime import date, datetime, timedelta
from datetime import time as anothertime
import time
import uuid

#appengine
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

#tripfiles
from app.tripfiles.view import ViewHelper
from app.tripfiles.useraccount import UserAccount, UserRegister
from app.tripfiles.trip import TripDelete, TripModify, TripSave
from app.tripfiles.subscriptions import SubscriptionManager    
from app.tripfiles.setup import BaseDataInitializer
from app.tripfiles.report import TripReport

class MainPage(webapp.RequestHandler):
    def get(self):
        viewhelper = ViewHelper(self.request)
        
        template_values = viewhelper.get_navigation_options()
        template_values.update(viewhelper.get_menu_options())
        template_values.update(viewhelper.get_placeholder_trips())
        
        path = os.path.join(os.path.dirname(__file__), '../../templates', 'index.html')
        self.response.out.write(template.render(path, template_values))

class SupportPage(webapp.RequestHandler):
    def get(self):
        viewhelper = ViewHelper(self.request)
        
        template_values = viewhelper.get_navigation_options()
        template_values.update(viewhelper.get_menu_options())
        template_values.update(viewhelper.get_placeholder_trips())
        
        path = os.path.join(os.path.dirname(__file__), '../../templates', 'help.html')
        self.response.out.write(template.render(path, template_values))

        
        
application = webapp.WSGIApplication(
    [('/', MainPage),
     ('/setup/(.*)', BaseDataInitializer),
     ('/register', UserRegister),
      ('/support', SupportPage),
     ('/account/(.*)', UserAccount),
     ('/save', TripSave),     
     ('/modify', TripModify),
     ('/deletetrip', TripDelete),
     ('/report', TripReport),
     ('/report/(.*)', TripReport),     
     ('/subscriptions-changed', SubscriptionManager)],
    debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
