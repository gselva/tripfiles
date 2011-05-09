import cgi
import os
from datetime import date, datetime, timedelta
from datetime import time as anothertime
import time
import uuid
import logging
#import json

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

#app imports
from app.tripfiles.model import TripFilesUser, UserProvisions, DayTrip
from app.tripfiles.report import ReportView, TripLegView, TripView
from app.tripfiles.view import ViewHelper

class TripSave(webapp.RequestHandler):
    def post(self):
        args = self.request.arguments()
        waypoints = []
        distances = []
        when = datetime.now()
        daytrip = DayTrip()

        if self.request.get('trip_key'):
            trip_key = self.request.get('trip_key')
            daytrip = db.get(db.Key(trip_key))
        else:
            if users.get_current_user():
                daytrip.who = users.get_current_user()

        daytrip.when = when

        total_distance = 0
        if self.request.get('total_miles'):
            try:
                total_distance = float(self.request.get('total_miles'))
            except:
                total_distance = 0
                
        daytrip.total_distance = total_distance
        
        cpm = 0	
        if self.request.get('cost_per_mile_pound'):
            cost_per_mile_pound = int(self.request.get('cost_per_mile_pound'))
            cpm = cost_per_mile_pound * 100

        if self.request.get('cost_per_mile_pence'):
            cost_per_mile_pence = int(self.request.get('cost_per_mile_pence'))
            cpm = cpm + cost_per_mile_pence

        daytrip.pence_per_mile = cpm

        if self.request.get('label_parking_expenses'):
            daytrip.other_expenses_label = self.request.get('label_parking_expenses')
        else:
            daytrip.other_expenses_label = ''

        other_expenses = 0	
        if self.request.get('other_expenses_charges_pound'):
            other_expenses_charges_pound = int(self.request.get('other_expenses_charges_pound'))
            other_expenses = other_expenses_charges_pound * 100

        if self.request.get('other_expenses_charges_pence'):
            other_expenses_charges_pence = int(self.request.get('other_expenses_charges_pence'))
            other_expenses = other_expenses + other_expenses_charges_pence

        daytrip.other_expenses_charge = other_expenses

        if self.request.get('mode_of_travel'):
            daytrip.trip_code = self.request.get('mode_of_travel')
        else:
            daytrip.trip_code = ''


        if self.request.get('other_no_passengers'):
            try:
                daytrip.passenger_count = int(self.request.get('other_no_passengers'))
            except:
                daytrip.passenger_count = 0
        else:
            daytrip.passenger_count = 0	 

        if self.request.get('other_passenger_miles'):
            try:
                daytrip.passenger_mileage = int(self.request.get('other_passenger_miles'))
            except:
                daytrip.passenger_mileage = 0
        else:
            daytrip.passenger_mileage = 0	    

        count = 0        
        for arg in args:
            argstr = 'input'+str(count)
            legstr = 'leg'+str(count)
            #google maps api only allows 10 addresses
            if count < 10:
                if self.request.get(argstr):
                    waypoints.append(self.request.get(argstr))
                    if self.request.get(legstr):
                        try:
                            distance = int(float(self.request.get(legstr)) * 1609.344)
                        except:
                            distance = 0
                    else:
                        distance = 0
                    distances.append(distance)
            count = count+1

        if self.request.get('tripdate'):
            tripdate = datetime.strptime(self.request.get('tripdate'), '%m/%d/%Y')
        else:
            tripdate = None


        if tripdate:
            daytrip.waypoints = waypoints
            daytrip.distances = distances
            daytrip.when = tripdate
            daytrip.put()
            notification = '{"app_notification_type": "app_tip", "app_notification": "Trip saved." }'
            logging.debug(notification)
        else:
            notification = '{"app_notification_type": "app_error", "app_notification": "Trip data incomplete. Please ensure a Trip date is set."}'

        self.response.out.write(notification)

class TripDelete(webapp.RequestHandler):
    def post(self):
        trip_key = self.request.get('trip_key').strip()
        if users.get_current_user():
            trip = db.get(db.Key(trip_key))
            if trip and trip.who == users.get_current_user():
                when = trip.when.strftime('%a, %d %b %Y')
                trip.delete()
                
                notification = '{"app_notification_type": "app_tip", "app_notification": "Deleted Trip dated '+when+'" }'
                logging.debug(notification)
                self.response.out.write(notification)
            else:
                notification = '{"app_notification_type": "app_error", "app_notification": "Cannot locate trip" }'
                self.response.out.write(notification)

        else:
            self.redirect('/')

class TripModify(webapp.RequestHandler):
    def post(self):
        trip_key = self.request.get('trip_key').strip()
        if users.get_current_user():
            trip = db.get(db.Key(trip_key))
            viewhelper = ViewHelper(self.request)
            template_values = viewhelper.get_navigation_options()
            template_values.update(viewhelper.get_menu_options())

            if trip and trip.who == users.get_current_user():
                count = 0
                triplegs = []
                total_distance = 0
                for waypoint, distance in zip(trip.waypoints, trip.distances):
                    distance_miles = '%.1f' % (distance * 0.000621371192)
                    tripleg = TripLegView(waypoint, None, distance_miles, trip.when, count)
                    triplegs.append(tripleg)
                    count=count+1
                    total_distance = total_distance + distance
                
                #fill triplegs with blank i it is less than 10
                if len(triplegs) < 10:
                    extras = 10-len(triplegs)
                    trips_length = len(triplegs)
                    for i in range(extras):
                        tripleg = TripLegView('', None, 0, '', trips_length+i)
                        logging.debug('Added filler tripleg #' +str(trips_length+i))
                        triplegs.append(tripleg)
            
                if trip.total_distance and trip.total_distance > 0:
                    total_miles = '%.1f' % trip.total_distance
                else:
                    total_miles = '%.1f' % (total_distance * 0.000621371192)
                    
                tripdate = trip.when.strftime('%m/%d/%Y')

                try:
                    cost_per_mile_pound = int(trip.pence_per_mile/100)
                except:
                    cost_per_mile_pound = 0

                if cost_per_mile_pound > 0:
                    cost_per_mile_pence = trip.pence_per_mile - (cost_per_mile_pound*100)
                else:
                    cost_per_mile_pence = 0

                label_parking_expenses = trip.other_expenses_label or ''

                try:
                    other_expenses_charges_pound = int(trip.other_expenses_charge/100)
                except:
                    other_expenses_charges_pound = 0

                if trip.other_expenses_charge > 0:
                    other_expenses_charges_pence = trip.other_expenses_charge - (other_expenses_charges_pound*100)
                else:
                    other_expenses_charges_pence = 0

                other_no_passengers = trip.passenger_count if trip.passenger_count else 0
                other_passenger_miles = trip.passenger_mileage if trip.passenger_mileage else 0

                mode_of_travel = trip.trip_code.strip() if trip.trip_code else ''

                template_values.update({'triplegs': triplegs, 
                                        'total_miles': total_miles,
                                        'tripdate': tripdate, 
                                        'trip_key': trip_key,
                                        'cost_per_mile_pound': cost_per_mile_pound,
                                        'cost_per_mile_pence': cost_per_mile_pence,
                                        'label_parking_expenses': label_parking_expenses,
                                        'other_expenses_charges_pound': other_expenses_charges_pound,
                                        'other_expenses_charges_pence': other_expenses_charges_pence,
                                        'mode_of_travel': mode_of_travel,
                                        'other_no_passengers': other_no_passengers,
                                        'other_passenger_miles': other_passenger_miles})

            else:
                template_values.update({'app_notification': 'Cannot find the trip.', 'app_notification_type': 'app_error'})

            path = os.path.join(os.path.dirname(__file__), '../../templates', 'index.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
