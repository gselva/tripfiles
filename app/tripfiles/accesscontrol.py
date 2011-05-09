#python core
import logging
from datetime import date, datetime, timedelta
from datetime import time as anothertime
import time

#tripfiles
from app.tripfiles.model import UserProvisions, TripFilesUser

#constants

class AccessController(object):
    '''
    Provides APIs for user access control
    '''
    def is_registered(self, user):
        tripusers = TripFilesUser.gql("WHERE who = :who", who=user)
        if tripusers.count()==1:
            return True
        else:
            return False
            
    def can_save_trip(self, user):
        userprovisions = UserProvisions.gql("WHERE who = :who",who=user)
        
        if userprovisions.count()<1:
            return False;
        
        userprovision = userprovisions.get()
        
        return (userprovision.save_enabled and userprovision.valid_until>datetime.utcnow())
        
    def can_view_report(self, user):
        userprovisions = UserProvisions.gql("WHERE who = :who",who=user)
        
        if userprovisions.count()<1:
            return False;
        
        userprovision = userprovisions.get()
        
        return (userprovision.report_enabled and userprovision.valid_until>datetime.utcnow())
    
    def can_download_report(self, user):
        return False
    
    def subscription_expired(self, user):
        userprovisions = UserProvisions.gql("WHERE who = :user",user=user)
        if userprovisions.count()==1:
            provision = userprovisions.get()
            try:
                if provision.valid_until < datetime.utcnow():
                    return True
                else:
                    return False
            except:
                #we won't penalize user for our screw-ups
                return False
        else:
            return False         
    
    def subscription_expires_soon(self, user):
        userprovisions = UserProvisions.gql("WHERE who = :user",user=user)
        logging.debug('In subscription_expires_soon')
        if userprovisions.count()==1:
            provision = userprovisions.get()
            try:
                if provision.valid_until < datetime.combine(date.today(), anothertime()) + timedelta(days=3):
                    notification_str = 'Your subscription will expire in a few days. Please click on Account button and follow the link to renew your subscription'
                    notification =  '{"app_notification": "'+notification_str+'", "app_notification_type": "app_error"}'
                    logging.debug(notification)
                    return notification
            except Exception, e:
                logging.error('Exception in subscription_expires_soon' + e.message)
                return None
        return None
    
    def has_subscription(self, user):
        userprovisions = UserProvisions.gql("WHERE who = :user",user=user)
        logging.debug('In has_subscription')
        if userprovisions.count()<1:
            return False
        else:
            return True
        
        
    