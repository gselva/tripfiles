#python core
import logging

#appengine
from google.appengine.ext import webapp
from google.appengine.api import users

#tripfiles
from app.tripfiles.accesscontrol import AccessController

#constants
##alphabets for digits
digit_alpha_dict = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E', '5': 'F', '6': 'G', '7': 'H', '8': 'I', '9': 'J', '10': 'K' }

#module vars
accesscontroller = AccessController()

class SubscriptionView(object):
    def __init__(self, code, name, description):
        self.code = code
        self.name = name
        self.description = description
        
class TripLegView(object):
    def __init__(self, start=None, end=None, distance='0.0', date=None, sequence=0):
        self.start=start
        self.end=end
        self.distance=distance
        self.date = date 
        self.sequence = sequence
        self.sequence_label = digit_alpha_dict.get(str(sequence))

class TripView(object):
    def __init__(self, date=None, legs=[], distance=0, trip_code=None, id=None, addresses=[], 
                 other_expense_label='', 
                 other_expense_pound = 0,
                 other_expense_pence = 0,                 
                 other_no_passengers=0,
                 other_passenger_miles=0):
        self.legs = legs
        self.code = trip_code
        self.distance = distance
        self.date = date
        self.id = id
        self.addresses = addresses   
        self.other_expense_label = other_expense_label
        self.other_expense_pound = other_expense_pound if other_expense_pound >0 else ''
        #print 0 for pence if other expenses is a whole pound, if not print nothing for pence
        if other_expense_pound >0:
            self.other_expense_pence = other_expense_pence if other_expense_pence>0 else 0
        else:
            self.other_expense_pence = other_expense_pence if other_expense_pence>0 else ''

        self.other_no_passengers = other_no_passengers if other_no_passengers>0 else ''
        self.other_passenger_miles = other_passenger_miles if other_no_passengers>0 and other_passenger_miles >0 else ''


class ReportView(object):
    def __init__(self, startdate=None, enddate=None, trip_pages=[], distance=0, 
                 other_expense_pound=0, other_expense_pence=0, 
                 report_total_passenger_mileage=0):


        self.firstpage_trips = trip_pages[0]
        self.nextpages = []
        if len(trip_pages) > 1:
            self.nextpages = trip_pages[1]

        self.page_count = len(trip_pages)
        self.distance = distance
        self.startdate = startdate
        self.enddate = enddate
        self.total_other_expense_pound = other_expense_pound if other_expense_pound >0 else ''
        #print 0 for pence if other expenses is a whole pound, if not print nothing for pence
        if other_expense_pound >0:
            self.total_other_expense_pence = other_expense_pence if other_expense_pence>0 else 0
        else:
            self.total_other_expense_pence = other_expense_pence if other_expense_pence>0 else ''

        if report_total_passenger_mileage>0:
            self.report_total_passenger_mileage = report_total_passenger_mileage
        else:
            self.report_total_passenger_mileage = ''
            
class ViewHelper(object):
    def __init__(self, request):
        self.request = request
        
    def get_navigation_options(self):
        '''
        Top navigation menu options: login/logout, username, user_registered
        '''
        username = 'Dear Guest'
        user_logged_in = False
        user_registered = False
        notification = ''
        
        if users.get_current_user():
            username=users.get_current_user().nickname()
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
            user_logged_in = True
            user_registered = accesscontroller.is_registered(users.get_current_user())
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            notification = "Please login with your google login to view your trip reports"
            
        options = {
            'user_logged_in': user_logged_in,
            'username': username,
            'url': url,
            'url_linktext': url_linktext,
            'user_registered': user_registered,
            'app_notification': '{"app_notification": "'+notification+'", "app_notification_type": "app_tip"}'
            }
        
        return options
        
    def get_menu_options(self):
        save_enabled = False
        report_enabled = False
        logging.debug('In get_menu_options')
        if users.get_current_user():
            save_enabled = accesscontroller.can_save_trip(users.get_current_user())      
            report_enabled = accesscontroller.can_view_report(users.get_current_user())
            
        options = {
            'save_enabled': save_enabled,
            'report_enabled': report_enabled,
            }

        if users.get_current_user() and not accesscontroller.has_subscription(users.get_current_user()):
            notification = 'You do not have a subscription at the moment. Please click on Register/Account button and follow the link to start your free trial or renew your subscription'
            options.update({ 'app_notification': '{"app_notification": "'+notification+'", "app_notification_type": "app_error"}'})
            return options

        
        if accesscontroller.subscription_expired(users.get_current_user()):
            notification = 'Your subscription has expired. Please click on Register/Account button and follow the link to start your free trial or renew your subscription'
            options.update({ 'app_notification': '{"app_notification": "'+notification+'", "app_notification_type": "app_error"}'})
        else:
            notification = accesscontroller.subscription_expires_soon(users.get_current_user())
            if notification:
                logging.debug(notification)
                options.update({ 'app_notification':  notification})
            
        return options
        

    def get_placeholder_trips(self):
        #create 10 legs
        triplegs = []
        for i in range(10):
            tripleg = TripLegView('', None, 0, '', i)
            triplegs.append(tripleg)

        options = {'triplegs': triplegs}
        return options
    
