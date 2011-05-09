import cgi
import os
from datetime import date, datetime, timedelta
from datetime import time as anothertime
import time
import uuid
import logging
import cStringIO as StringIO

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api.users import User
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from sx.pisa3 import pisaDocument

#app imports
from app.tripfiles.model import TripFilesUser, UserProvisions, DayTrip
from app.tripfiles.view import TripLegView, TripView, ReportView, ViewHelper

FIRSTPAGE_TRIPS_COUNT = 13
TRIPS_PER_PAGE = 10

class TripReport(webapp.RequestHandler):
    def post(self, action=None):
        if not users.get_current_user():
            self.redirect('/')
        
        startparam = self.request.get('startdate').strip()
        endparam = self.request.get('enddate').strip()
        dateformat = '%m/%d/%Y'

        if startparam!='' or endparam!='':
            startdate = time.strptime(startparam, dateformat)
            enddate = time.strptime(endparam, dateformat)

        if not startparam or not endparam:
            startdate = time.gmtime() #time.strftime(dateformat, time.gmtime())
            enddate = time.gmtime() #time.strftime(dateformat, time.gmtime())

        startdate = time.strftime('%Y-%m-%d %H:%M:%S', startdate)
        enddate = time.strftime('%Y-%m-%d %H:%M:%S', enddate)

        trips = []
        userdata = None
        #AND when >= :start AND when <= :end 
        if users.get_current_user():
            user = users.get_current_user()
            trip_user = TripFilesUser.gql("WHERE who =:who", who=user)
            userdata = trip_user.get()
            #if admin user is getting report for another user
            if self.request.get('user_email'):
                user_email = self.request.get('user_email').strip()
                logging.debug('user_email='+user_email)
                user = User(email=self.request.get('user_email').strip())
                trip_users = TripFilesUser.gql("WHERE who =:who", who=user)
                logging.debug("Count="+str(trip_users.count()))
                trip_user = trip_users.get()
                logging.debug('Report user='+trip_user.first_name)
                userdata = trip_user
                
            trips = DayTrip.gql("WHERE who = :who AND when >= DATETIME(:start) AND when <= DATETIME(:end) ORDER BY when ASC",
                                who=user, start=startdate, end=enddate)
            
        else:
            self.redirect('/')


        viewtrips = []
        report_total_distance = 0.0
        report_total_other_pound = 0
        report_total_other_pence = 0
        report_total_passenger_mileage = 0

        tripcount = 0
        firstpage_trips = []
        middlepage_trips = [] #trips in each middlepage
        for trip in trips:
            viewlegs = []
            trip_total_distance = 0.0
            count = len(trip.waypoints)
            waypoints_description = ''
            for i in xrange(count-1):
                distance = (trip.distances[i+1]) * 0.000621371192
                distance = round(distance, 2)
                viewleg = TripLegView(trip.waypoints[i], trip.waypoints[i+1], 
                                      distance, trip.when.strftime('%a, %d %b %Y'), i+1)
                viewlegs.append(viewleg)
                trip_total_distance = trip_total_distance + distance
                if i==0:
                    waypoints_description =  trip.waypoints[i].upper() +' - '+ trip.waypoints[i+1].upper()
                else:
                    waypoints_description = waypoints_description.upper() + ' - '+trip.waypoints[i+1].upper()

            #if we have total_distance saved, use it since the user may have updated the total manually
            if trip.total_distance and trip.total_distance > 0:
                trip_total_distance = trip.total_distance

            other_expense_label= trip.other_expenses_label
            try:
                other_charges_pound = int(trip.other_expenses_charge/100)
            except:
                other_charges_pound = 0

            if trip.other_expenses_charge > 0:
                other_charges_pence = trip.other_expenses_charge - (other_charges_pound*100)
            else:
                other_charges_pence = 0

            report_total_other_pence = report_total_other_pence + other_charges_pence + (other_charges_pound*100)

            other_expense_pound = other_charges_pound if other_charges_pound>0 else 0
            other_expense_pence = other_charges_pence if other_charges_pence>0 else 0

            viewtrip = TripView(trip.when.strftime('%a, %d %b %Y'), viewlegs, 
                                round(trip_total_distance,2), trip.trip_code, trip.key(), waypoints_description, 
                                other_expense_label, other_expense_pound, other_expense_pence,
                                trip.passenger_count,
                                trip.passenger_mileage)

            #add viewtrip to report pages
            if tripcount < FIRSTPAGE_TRIPS_COUNT:
                firstpage_trips.append(viewtrip)

            if tripcount >= FIRSTPAGE_TRIPS_COUNT: 
                middlepage_trips.append(viewtrip)

            report_total_distance = report_total_distance + trip_total_distance


            report_total_passenger_mileage = report_total_passenger_mileage + (trip.passenger_mileage if trip.passenger_mileage else 0) 

            tripcount = tripcount +1


        #split middle pages for report paging
        nextpages = []
        apage = []
        logging.debug('#middlepage_trips ' + str(len(middlepage_trips)))
        for (counter, atrip) in enumerate(middlepage_trips):
            apage.append(atrip)
            if (((counter+1) % TRIPS_PER_PAGE) == 0): #counter!= 0 and 
                logging.debug('nextpage counter' + str(counter))
                nextpages.append(apage)
                apage = []
        #append all remaining trips
        if apage:
            nextpages.append(apage)


        startdate = time.strptime(startdate, '%Y-%m-%d %H:%M:%S')
        enddate = time.strptime(enddate, '%Y-%m-%d %H:%M:%S')
        startparam = time.strftime('%a, %d %b %Y', startdate)
        endparam = time.strftime('%a, %d %b %Y', enddate)

        try:
            report_other_charges_pound = int(report_total_other_pence/100)
        except:
            report_other_charges_pound = 0

        if report_total_other_pence > 0:
            report_other_charges_pence =report_total_other_pence - (report_other_charges_pound*100)
        else:
            report_other_charges_pence = 0

        viewreport = ReportView(startparam, endparam, [firstpage_trips, nextpages], round(report_total_distance, 2), 
                                report_other_charges_pound, report_other_charges_pence,
                                report_total_passenger_mileage)

        #reusing date for display
        template_values = {
            'reportview': viewreport,
            'userdata': userdata,
        }

        
        if action=='download':
            path = os.path.join(os.path.dirname(__file__), '../../templates/', 'printable-tripreport.html')
            if userdata.mileage_template=='BUCKS NHS TRUST':
                path = os.path.join(os.path.dirname(__file__), '../../templates/reports/', 'bucks_nhs_trust.html')
            elif userdata.mileage_template=='HILLINGDON PRIMARY CARE TRUST':
                path = os.path.join(os.path.dirname(__file__), '../../templates/', 'printable-tripreport.html')
            html = template.render(path, template_values)
            logging.debug('Generating pdf...')
            self.pdf(html)
        else:
            path = os.path.join(os.path.dirname(__file__), '../../templates', 'tripreport.html')
            html = template.render(path, template_values)
            self.response.out.write(template.render(path, template_values))                

    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        viewhelper = ViewHelper(self.request)
        
        template_values = viewhelper.get_navigation_options()
        template_values.update(viewhelper.get_menu_options())
        if users.get_current_user():
            if users.get_current_user().email()=='tripfiles.cs@gmail.com' or  users.is_current_user_admin():
                template_values.update({'adminEnabled': True, 'user_email': users.get_current_user().email()})
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
        path = os.path.join(os.path.dirname(__file__), '../../templates', 'reporthome.html')
        self.response.out.write(template.render(path, template_values))

        
    def pdf(self, html):
        #logging.debug(html)
        result = StringIO.StringIO()
        path = os.path.join(os.path.dirname(__file__), '../../')
        css_file = ''.join([path, 'fs-resources/pdfreport.css'])
       
        css = file(css_file, 'r').read()
        #logging.debug('css %s' % css)        
        pdf = pisaDocument(StringIO.StringIO(html), result, default_css=css)
        
        if not pdf.err:
            logging.debug('PDF generated. Sending it to browser...')
            #logging.debug(result.getvalue())
            self.response.headers['Content-Disposition'] = 'attachment; filename=MyTripReport.pdf'
            
            self.response.out.write(result.getvalue())
        else:
            self.response.out.write('We had some errors generating pdf report. Please try again after a few minutes.')
    