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
from google.appengine.ext import db

#app imports
from app.tripfiles.model import TripFilesUser, UserProvisions, SubscriptionPlan
from app.tripfiles.view import ViewHelper, SubscriptionView
from app.tripfiles.spreedly import Spreedly, SITE_NAME, SPREEDLY_TEST_PLAN_CODE

#spreedly

spreedlyinterface = Spreedly()

class SubscriptionManager(webapp.RequestHandler):
        
    def post(self):  
        subscriber_ids = self.request.get('subscriber_ids')
        logging.debug('Subs ids', subscriber_ids)
        if subscriber_ids:
            ids = subscriber_ids.split(',')
            for subscriber_id in ids:
                self.updateUserProvisions(subscriber_id)
        else:
            return
    
    def get_all_active_subscriptions(self):
        subscriptions = SubscriptionPlan.gql('WHERE active = True')
        logging.debug('Subsciptions #%s' % subscriptions.count())
        viewable_subscriptions = []
        for subscription in subscriptions:
            viewable_subscriptions.append(SubscriptionView(subscription.code, 
                                                           subscription.name, 
                                                           subscription.description))
        return viewable_subscriptions
        
    def getNewSubscriberURL(self, request, nickname, tripuser):
        logging.debug('user id ' + tripuser.user_id)
        
        subscription_url = ''.join(['https://spreedly.com/', SITE_NAME, '/subscribers/', tripuser.user_id
        , '/subscribe/',SPREEDLY_TEST_PLAN_CODE,'/', nickname
        , '?email=', tripuser.email
        , '&first_name=', tripuser.first_name
        , '&last_name=', tripuser.last_name
        , '&return_url=', request.scheme, '://', request.host, '/account/subscription-update'])
        return subscription_url
        
    def getSubscriptionUpdateURL(self, subscription_token, request):
        subscription_url = ''.join(['https://spreedly.com/', SITE_NAME, '/subscriber_accounts/',
                                    subscription_token, 
                                    '?return_url=',
                                    request.scheme, '://', request.host, '/account/subscription-update'])
        return subscription_url
    
    def updateUserProvisions(self, subscriber_id):
        userprovisions = UserProvisions.gql("WHERE user_id = :user_id",user_id=subscriber_id)
        if userprovisions.count()!=1:
            logging.error('User not provisioned but has created subscription?! Provisioning now...')
            userprovision = UserProvisions()            
            userprovision.user_id = subscriber_id
            userprovision.who = users.get_current_user()
            userprovision.save_enabled = True
            userprovision.report_enabled = True
            userprovision.provisioned_for = ['WEB']
            #default 15 days validity
            userprovision.valid_until = datetime.combine(date.today(), anothertime()) + timedelta(days=15)
            #return False, '', 'Could not update subscription data. Please contact customer support.'
        else:
            userprovision = userprovisions.get()
            
        subscription_valid=True
        subscription_valid_until=userprovision.valid_until 
        
        subscriber_details = spreedlyinterface.subscriber_details(subscriber_id)
        logging.debug('Fetched Subscriber details %s' % str(subscriber_details))
  
        if subscriber_details and subscriber_details['customer-id']==subscriber_id:
            logging.debug('updating tripfiles userprovisions...')                    
            valid_until_str = subscriber_details['active-until'] if subscriber_details.has_key('active-until') else None
            if valid_until_str:
                valid_until = datetime.strptime(valid_until_str,  '%Y-%m-%dT%H:%M:%SZ') #u'2010-11-22T16:45:13Z', 
                userprovision.valid_until = valid_until

            subscription_valid = True if subscriber_details.has_key('active') and subscriber_details['active']=='true' else False
            notification_msg = 'Subscription active'  if subscription_valid else 'Subscription inactive'
            userprovision.save_enabled = subscription_valid
            userprovision.report_enabled = subscription_valid
            userprovision.subscription_token = subscriber_details['token'] if subscriber_details.has_key('token') else None
            userprovision.subscription_code = subscriber_details['feature-level'] if subscriber_details.has_key('feature-level') else None
            userprovision.save()

            
        return notification_msg
