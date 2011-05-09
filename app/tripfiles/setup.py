#python core
import logging

#google appengine
from google.appengine.ext import webapp
from google.appengine.api import users

#tripfiles
from app.tripfiles.model import SubscriptionPlan, TripFilesUser, UserProvisions

#constants
SUBSCRIPTION_PLAN_MONTHLY = 'COFFEE-MONTHLY'

class BaseDataInitializer(webapp.RequestHandler):
    def get(self, entity=None, action=None):
        if users.get_current_user() and  users.get_current_user().email()=='selvakumar@gmail.com':
            if entity=='subscriptions':
                result = self.add_subscriptions()
                self.response.out.write(result)
            if entity=='users':
                self.fix_user_id()
        else:
            self.response.out.write('<html><body>User '+users.get_current_user().nickname()+' not authorized to add subscriptions</body></html>')
   
    def fix_user_id(self):
        tripusers = TripFilesUser.gql('')
        logging.debug('User ids #'+str(tripusers.count()))
        ids=''
        for tripuser in tripusers:
            provisions = UserProvisions.gql('WHERE who = :who', who=tripuser.who)
            if provisions.count()==1:
                provision = provisions.get()
                tripuser.user_id = provision.user_id
                tripuser.save()
                logstr = ''.join([tripuser.who.nickname(), ' - ', tripuser.user_id, ' <br />'])
                logging.debug('Updated '+logstr)
                ids = ids+logstr
                
        self.response.out.write('<html><body>User ids updated<br /> '+ids+'</body></html>');
        
    def add_subscriptions(self):
        plans = SubscriptionPlan.gql("WHERE code = :code",
                            code=SUBSCRIPTION_PLAN_MONTHLY)
        if plans.count() > 0:
            logging.debug('Subscription %s exists', SUBSCRIPTION_PLAN_MONTHLY)
            return '<html><body>Subscription exists</body></html>'
        
        subs = SubscriptionPlan()
        subs.code = SUBSCRIPTION_PLAN_MONTHLY
        subs.name = 'Cup of Coffee - Monthly Plan'
        subs.description = 'Unlimited trip creation and report generation every month for the price of a coffee. Try it free for first 15 days. Cancel anytime. No setup fees. No cancellation charges. No hidden fees.'
        subs.active = True
        subs.save()
        logging.debug('Subscription %s added', SUBSCRIPTION_PLAN_MONTHLY)
        return '<html><body>Added subscription</body></html>'
