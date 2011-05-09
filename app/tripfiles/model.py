from google.appengine.ext import db

class UserProvisions(db.Model):
    user_id = db.StringProperty()
    who = db.UserProperty()    
    registration_date = db.DateTimeProperty(auto_now_add=True)
    
    #user must be provisioned (i.e, he should have paid) to save, get report 
    save_enabled = db.BooleanProperty()
    report_enabled = db.BooleanProperty()
    valid_until = db.DateTimeProperty()
    provisioned_for =  db.StringListProperty() #WEB, MOBILE, pigeons
    subscription_token = db.StringProperty()
    subscription_code = db.StringProperty()

class SubscriptionPlan(db.Model):
    code = db.StringProperty()
    name = db.StringProperty()
    description = db.StringProperty()
    active = db.BooleanProperty()
    
class TripFilesUser(db.Model):
    who = db.UserProperty()
    user_id = db.StringProperty()    
    email = db.EmailProperty()
    first_name = db.StringProperty()
    middle_name = db.StringProperty()
    last_name = db.StringProperty()
    work_title = db.StringProperty()
    home_address = db.StringProperty(multiline=True)
    office_base_address = db.StringProperty(multiline=True)
    vehicle_make = db.StringProperty()
    vehicle_cc = db.StringProperty()
    vehicle_registration = db.StringProperty()
    mileage_template = db.StringProperty() #which PCT, organization
    work_id = db.StringProperty() #employee number
    work_group = db.StringProperty()         
    work_department = db.StringProperty() 
    work_organization = db.StringProperty() 
    work_geography = db.StringProperty() #supported geographies: uk, us, etc. 
    preferred_currency = db.StringProperty() #USD, GBP, INR
    preferred_metric = db.StringProperty() #MILES, KM
    
class UserAccess(db.Model):
    who = db.UserProperty()
    user_id = db.StringProperty()
    access_tokens = db.StringListProperty() #TRIPCRUD, TRIPREPORT, TRIPAGGREGATE
    
    #if TRIPAGGREGATE token is present, this field will have the scopes listed, 
    #scopes : USER, GROUP, DEPARTMENT, ORGANIZATION, GEOGRAPHY
    aggregation_scope = db.StringListProperty() 
    
    #the actual scopes, such as FALLS TEAM (which is the GROUP), HIGH WYCOMBE HOSPITAL (which is the DEPARTMENT)
    #BUCKS (geography), NHS (organization). Not all these scopes will be listed. Access is granted to listed scopes.
    scopes = db.StringListProperty() 
    
class DayTrip(db.Model):
    who = db.UserProperty()
    when = db.DateTimeProperty()
    waypoints = db.StringListProperty()
    distances = db.ListProperty(int) #in metres
    total_distance = db.FloatProperty() #in miles
    remarks = db.StringProperty(multiline=True)
    trip_code = db.StringProperty()
    passenger_count = db.IntegerProperty()
    passenger_mileage = db.IntegerProperty() #in metres
    pence_per_mile = db.IntegerProperty() #we are going to avoid floats to save cpu time
    other_expenses_label = db.StringProperty()
    other_expenses_charge = db.IntegerProperty()  #again, this is an integer (in pence) rather than a float
