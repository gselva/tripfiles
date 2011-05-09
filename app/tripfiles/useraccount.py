import cgi
import os
from datetime import date, datetime, timedelta
from datetime import time as anothertime
import time
import uuid
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

#app imports
from app.tripfiles.model import TripFilesUser, UserProvisions, DayTrip
from app.tripfiles.view import ViewHelper
from app.tripfiles.subscriptions import SubscriptionManager
from app.tripfiles.accesscontrol import AccessController

accesscontroller = AccessController()

class UserRegister(webapp.RequestHandler):
    def get(self):
        logging.debug('In register->get')
        username = None
        user_logged_in = False
        user_registered = False
        notification = None
        url = users.create_login_url(self.request.uri)
        if users.get_current_user():
            url = users.create_logout_url('/')	
            user_logged_in = True
            username=users.get_current_user().nickname()
            tripuser = TripFilesUser.gql("WHERE who = :who",
                                who=users.get_current_user())
            if tripuser.count() > 0:
                self.redirect('/account/update')
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
        viewhelper = ViewHelper(self.request)
        template_values = viewhelper.get_navigation_options()
        template_values.update(viewhelper.get_menu_options())
        notification = 'Please fill your details and click Register to start your free trial'
        
        template_values.update({ 'app_notification': '{"app_notification": "'+notification+'", "app_notification_type": "app_tip"}'})
        subscriptionMgr = SubscriptionManager()
        
        #subscription data
        active_subscriptions = subscriptionMgr.get_all_active_subscriptions()
        
        template_values.update({'active_subscriptions': active_subscriptions})
                                   
        path = os.path.join(os.path.dirname(__file__), '../../templates', 'account.html')

        self.response.out.write(template.render(path, template_values))
        
    def post(self):     
        if not users.get_current_user():
            self.redirect('/')

        logging.debug('In register->post')
        first_name = middle_name = last_name = ' '
        work_title = home_address = office_base_address = ''
        work_id = work_department = ''
        vehicle_make = vehicle_cc = vehicle_registration = ''
        
        #if self.request.get('input_first_name'):
        first_name = self.request.get('input_first_name')
        #if self.request.get('input_middle_name'):
        middle_name = self.request.get('input_middle_name')
        #if self.request.get('input_last_name'):
        last_name = self.request.get('input_last_name')
            
        #if self.request.get('input_work_title'):
        work_title = self.request.get('input_work_title')
        #if self.request.get('input_work_id'):
        work_id = self.request.get('input_work_id')
        #if self.request.get('input_work_department'):
        work_department = self.request.get('input_work_department')
            
            
        #if self.request.get('input_mileage_template'):
        mileage_template = self.request.get('input_mileage_template')
            
            
        #if self.request.get('input_home_address'):
        home_address = self.request.get('input_home_address')
        #if self.request.get('input_office_base_address'):
        office_base_address = self.request.get('input_office_base_address')
        #if self.request.get('input_vehicle_make'):
        vehicle_make = self.request.get('input_vehicle_make')
        #if self.request.get('input_vehicle_cc'):
        vehicle_cc = self.request.get('input_vehicle_cc')
            
        #if self.request.get('input_vehicle_registration'):
        vehicle_registration = self.request.get('input_vehicle_registration')
        
       
        
        if users.get_current_user():
            #account registration
            tripuser = TripFilesUser()
            tripuser.who = users.get_current_user()
            tripuser.first_name = first_name
            tripuser.middle_name = middle_name
            tripuser.last_name = last_name
            tripuser.email = users.get_current_user().email()
            tripuser.work_title = work_title
            tripuser.work_id = work_id
            tripuser.work_department = work_department
            
            tripuser.mileage_template = mileage_template
            tripuser.home_address = home_address
            tripuser.office_base_address = office_base_address
            tripuser.vehicle_make = vehicle_make
            tripuser.vehicle_cc = vehicle_cc            
            tripuser.vehicle_registration = vehicle_registration

            userprovision = UserProvisions()            
            userprovision.user_id = uuid.uuid4().hex
            userprovision.who = users.get_current_user()
            userprovision.save_enabled = False
            userprovision.report_enabled = False
            userprovision.provisioned_for = ['WEB']
            #15 days validity
            userprovision.valid_until = datetime.combine(date.today(), anothertime()) + timedelta(days=15)
            
            tripuser.user_id = userprovision.user_id
            tripuser.save()
            userprovision.save()
            
            notifications = first_name+' '+last_name+ ', your details are now registered.'
        else:
            self.redirect('/')
            
        #spreedly url 
        subscriptionMgr = SubscriptionManager()
        subscription_url = subscriptionMgr.getNewSubscriberURL(self.request, 
                                                               users.get_current_user().nickname(), tripuser)
        logging.debug('Subs url: '+ subscription_url)
        self.redirect(subscription_url)
        
class UserAccount(webapp.RequestHandler):
    def get(self, action=None):
        '''
        Shows account details.  
        This is also the callback for spreedly - /account/subscription-update
        '''
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))

        notification = None
        tripuser = None
        if users.get_current_user():
            user_logged_in = True
            username=users.get_current_user().nickname()
            tripusers = TripFilesUser.gql("WHERE who = :who",
                                who=users.get_current_user())
            if tripusers.count() != 1:
                notification = '{"app_notification_type": "app_error", "app_notification": "We found a minor glitch in your account! Please contact Customer Support if you have a subscription with us" }'
                viewhelper = ViewHelper(self.request)
                template_values = viewhelper.get_navigation_options()
                template_values.update(viewhelper.get_menu_options())
                template_values.update({'notification': notification})
                path = os.path.join(os.path.dirname(__file__), '../../templates', 'error.html')
                self.response.out.write(template.render(path, template_values))                       
                return
            else:
                tripuser = tripusers.get()
                
                subscriptionMgr = SubscriptionManager()
                #retrieve subscription info
                if action=='subscription-update':
                    notification_msg = subscriptionMgr.updateUserProvisions(tripuser.user_id)
                    notification = '{"app_notification_type": "app_tip", "app_notification": "'+notification_msg+'" }'
                elif action=='update':
                    notification = '{"app_notification_type": "app_tip", "app_notification": "Account updated" }'
                    
               #spreedly url 
                subscription_url = subscriptionMgr.getNewSubscriberURL(self.request, 
                                                                       users.get_current_user().nickname(), tripuser)
                
                #subscription data
                active_subscriptions = subscriptionMgr.get_all_active_subscriptions()
                user_subscription = None
                valid_until = None
                valid_subscription = False
                subscription_expired = False
                userprovisions = UserProvisions.gql("WHERE user_id = :user_id", user_id=tripuser.user_id)
                if userprovisions.count() == 1:
                    logging.debug('User provision is valid')
                    userprovision = userprovisions.get()
                    valid_until = userprovision.valid_until.strftime('%a, %d %b %Y') if userprovision.valid_until else None
                    subscription_expired = accesscontroller.subscription_expired(users.get_current_user())
                    if subscription_expired:
                        notification_str = 'Your subscription has expired. Please follow the link below to renew your subscription'
                        notification =  '{"app_notification": "'+notification_str+'", "app_notification_type": "app_error"}'
                    elif userprovision.valid_until < datetime.combine(date.today(), anothertime()) + timedelta(days=3):
                        notification_str = 'Your subscription will expire in a few days. Please follow the link below to renew your subscription'
                        notification =  '{"app_notification": "'+notification_str+'", "app_notification_type": "app_error"}'

                    if userprovision.subscription_token:
                        subscription_url = subscriptionMgr.getSubscriptionUpdateURL(userprovision.subscription_token, self.request)
                        valid_subscription = True
                    for subscription in active_subscriptions:
                        logging.debug('Subscription =', subscription.name)
                        if subscription.code==userprovision.subscription_code:
                            user_subscription = subscription
                else:
                    logging.debug('User not provisioned')                    
                    valid_subscription = False 
                
       
            viewhelper = ViewHelper(self.request)
            template_values = viewhelper.get_navigation_options()
            template_values.update(viewhelper.get_menu_options())
 
            template_values.update({'tripuser': tripuser})
            template_values.update({'subscription_url': subscription_url})
            template_values.update({'valid_subscription': valid_subscription})
            
            template_values.update({'app_notification': notification, 
                                   'active_subscriptions': active_subscriptions,
                                   'user_subscription': user_subscription,
                                   'subscription_expired': subscription_expired,
                                   'subscription_valid_until': valid_until})
            
            if template_values.get('app_notification'):
                logging.debug('Notification='+template_values.get('app_notification'))
            
            path = os.path.join(os.path.dirname(__file__), '../../templates', 'account.html')
            self.response.out.write(template.render(path, template_values))                
        else:
            self.redirect('/')
            

            
    def post(self, action=None):       
        '''
        Updates user account - /account/update
        '''
        if not users.get_current_user():
            self.redirect('/')

        tripusers = TripFilesUser.gql("WHERE who = :who",
                    who=users.get_current_user())
        tripuser = tripusers.get()
        
        #if self.request.get('input_first_name'):
        tripuser.first_name = self.request.get('input_first_name').strip()
        #if self.request.get('input_middle_name'):
        tripuser.middle_name = self.request.get('input_middle_name').strip()
        #if self.request.get('input_last_name'):
        tripuser.last_name = self.request.get('input_last_name').strip()
            
        #if self.request.get('input_work_title'):
        tripuser.work_title = self.request.get('input_work_title').strip()

        #if self.request.get('input_work_id'):
        tripuser.work_id = self.request.get('input_work_id').strip()
        #if self.request.get('input_work_department'):
        tripuser.work_department = self.request.get('input_work_department').strip()
            
            
        #if self.request.get('input_mileage_template'):
        tripuser.mileage_template = self.request.get('input_mileage_template').strip()
            
            
        #if self.request.get('input_home_address'):
        tripuser.home_address = self.request.get('input_home_address').strip()
        #if self.request.get('input_office_base_address'):
        tripuser.office_base_address = self.request.get('input_office_base_address').strip()
        #if self.request.get('input_vehicle_make'):
        tripuser.vehicle_make = self.request.get('input_vehicle_make').strip()
        #if self.request.get('input_vehicle_cc'):
        tripuser.vehicle_cc = self.request.get('input_vehicle_cc').strip()
            
        #if self.request.get('input_vehicle_registration'):
        tripuser.vehicle_registration = self.request.get('input_vehicle_registration').strip()

        #tripuser.work_organization = 'Hillingdon PCT'
        tripuser.save()
            
        self.redirect('/account/update')
        
