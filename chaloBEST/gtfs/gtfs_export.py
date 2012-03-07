from mumbai.models import *
import json
from settings import *
from os.path import join
import csv
import sys
import datetime

def routeWithLocationData(route):
    '''
    Tests a  route if it has stop location data for each stop on the route.    
    '''
    # get the route detail
    routeDetails = RouteDetail.objects.filter(route_code=route.code).order_by('serial')
    #unrlist = UniqueRoute.objects.filter('route'=route)
    #for unr in unrlist:
    
    for rd in routeDetails :        
        if rd.stop.point is None:
            return False
        else:
            pass
    return True

def getRoutesHavingAllLocs():
    '''
    Gets routes having stop location data for each stop on the route.
    '''
    filteredroutes = []
    for route in Route.objects.all():
        if routeWithLocationData(route):
            filteredroutes.append(route)

    return filteredroutes
"""
def getCompleteRoutes():
    #rs = getRoutesHavingAllLocs()
    rs =  Route.objects.all()
    filteredroutes = []
    for route in rs:
        #a2s selected_related():
        if routeWithLocationData(route):
             
            filteredroutes.append(route)

    return filteredroutes

"""


def getCompleteRoutes(routelist):
    #get routes having all stop locaions
    filteredroutes = []
    isComplete = True
        
    for route in routelist:
        # check if all stops have locs
        isComplete = True
        if routeWithLocationData(route):
            # check if Unique Routes have distance
            unrs = route.uniqueroute_set.all()
            for unr in unrs:
                if unr.distance:
                    rsset= unr.routeschedule_set.all()
                    for rs in rsset:
                        if rs.runtime1 and rs.runtime2 and rs.runtime3 and rs.runtime4 and rs.headway1 and rs. headway2 and rs.headway3 and rs.headway4 and rs.headway5 and rs.first_from and rs.first_to and rs.last_from and rs.last_to:
                            filteredroutes.append(route)
                        else:
                            isComplete = False
                            continue
                else:
                    isComplete = False
                    continue
        

    return list(set(filteredroutes))


def routeWithSomeLocationData(route,limit):
    '''
    Gets stoplist for a route which has at most <limit> no of stops without location data.
    '''    
    # Get the route details
    routeDetails = RouteDetail.objects.filter(route_code=route.code).order_by('serial')
    # check for routes having less than three errors in stops, and send stops back.
    stoplist =[]
    errs = 0    
    for rd in routeDetails:        
        if rd.stop.point is None:
            # stop does not have point
            errs+=1
            if errs <= limit :
                stoplist.append(rd.stop.code)
        else:
            pass        

    if errs <=limit:
        return dict({'route':route, 'neededstops':len(stoplist) })
    else:
        return None

def getRoutesHavingSomeLocs(limit):
    '''
    Gets those routes which have at most <limit> no of stops without location data.
    '''    
    filteredroutes = []
    no_of_routes = 0
    for route in Route.objects.all():
        data= routeWithSomeLocationData(route, limit)
        if data:
            no_of_routes+=1
            filteredroutes.append(data)

    print "No of routes::",no_of_routes
    return filteredroutes


def export_routes(routebeer):        
    #routebeer = getRoutesHavingAlLocs()     

    f = make_csv_writer("routes.txt")
    f.writerow(["route_id" ,"route_short_name","route_long_name","route_type"])

    for route in routebeer:
        try:
            # data checks here
            f.writerow([route.code,route.alias[0:3],route.from_stop_txt + " - " + route.to_stop_txt,3])
        except:
            pass

def make_csv_writer(filename):
    return csv.writer(open(join(PROJECT_ROOT, "gtfs", "gtfs_mumbai_bus", filename), "w"), delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

def export_stops(routelist):
    stoplist = []
    for route in routelist:
        rds = RouteDetail.objects.filter(route=route).select_related()
        stoplist.extend(rd.stop for rd in rds)
            
    stoplist = list(set(stoplist))
    f = make_csv_writer("stops.txt")
    f.writerow(["stop_id" ,"stop_name","stop_lat","stop_lon"])
    for stop in stoplist:
        try:
            # data checks here 
            # stop_code is used for stop_id as its BEST specfic..
            # 
            f.writerow([stop.code,stop.name,stop.point.coords[1],stop.point.coords[0]])
        except:
            pass

def export_agency():
    f = make_csv_writer("agency.txt")

    # also
    f.writerow(["agency_id", "agency_name","agency_url","agency_timezone","agency_lang"])
    f.writerow(["BEST","BrihanMumbai Electric Supply & Transport Undertaking","http://www.bestundertaking.com/","Asia/Kolkata","en"])

    #f.writerow(["agency_id" ,"agency_name","agency_url","agency_timezone"])
    #f.writerow([1 ,"BEST","www.chalobest.in","Asia/Kolkata"])


            # stop_code is used for stop_id as its BEST specfic..

SERVICE_SCHEDULE = [
    {'id':0,'code':'MS','days':[1,2,3,4,5,6]},
    {'id':1,'code':'HOL','days':[7,8]}, # should be only 8
    {'id':2,'code':'SUN','days':[7]},
    {'id':3,'code':'MF&HOL','days':[1,2,3,4,5,8]},
    {'id':4,'code':'SAT','days':[6]},
    {'id':5,'code':'MF','days':[1,2,3,4,5]},
    {'id':6,'code':'SH','days':[7,8]},
    {'id':7,'code':'AD','days':[1,2,3,4,5,6,7,8]},
    {'id':8,'code':'SAT&SUN','days':[6,7]},
    {'id':9,'code':'MS&HOL','days':[1,2,3,4,5,6,8]},
    {'id':10,'code':'FW','days':[1,2,3,4,5,6,7]},
    {'id':11,'code':'SAT/SH','days':[6,7,8]},
    {'id':12,'code':'SAT&HOL','days':[6,8]},
    {'id':13,'code':'SAT&SH','days':[6,7,8]},
    {'id':14,'code':'SAT/SUND&HOL','days':[6,7,8]},
    {'id':15,'code':'S/H','days':[7,8]},
    {'id':16,'code':'SAT,SUN&HOL','days':[6,7,8]},
    {'id':17,'code':'FH','days':[6,8]}
    ]
# FH indicates what? full week + holidays??
# HOL holidays means only the exceptions as defined in calendar_dates.txt. this needs to be converted separately. 
# done here only to get the other components of gtfs up.

def export_calendar():
    f = make_csv_writer("calendar.txt")
    f.writerow(["service_id" ,"monday","tuesday","wednesday","thursday","friday","saturday","sunday","start_date","end_date"])

    start_date="20000101" #YYYYMMDD format
    end_date="20500101" #YYYYMMDD format

    schedule = SERVICE_SCHEDULE

    for ss in schedule:
        try:
            # data checks here 
            running = [1 if day in ss['days'] else 0 for day in range(1,8)]
            # ternary operation :::: ('false','true')[condition]
            f.writerow([ss['code']] + running + [start_date,end_date])
        except:
            print "Error:", str(ss) + '\t' +  str(sys.exc_info()[0]) + '\n'                


def uniquify_list_of_lists(sequence):
    seen = set()
    return [ x for x in sequence if str( x ) not in seen and not seen.add( str( x ) )]

def generate_trips(n=None):
    schedules = RouteSchedule.objects.all()
    if n is not None: schedules = schedules[:n]
    #triplist = []
    for schedule in schedules:
        route = schedule.unique_route.route
        unr = schedule.unique_route
        days = schedule.schedule_type

        for direction in ("UP","DOWN"):
            trip_id = "%s_%s_%s_%s" %(route.code,unr.id,days, direction)
            #triplist.append([schedule, route, direction, trip_id])
            yield schedule, route, direction, trip_id
    #return uniquify_list_of_lists(triplist)


def generate_trips_unr(n=None):
    schedules = RouteSchedule.objects.all()
    if n is not None: schedules = schedules[:n]
    #triplist = []
    for schedule in schedules:
        route = schedule.unique_route.route
        unr = schedule.unique_route
        days = schedule.schedule_type

        for direction in ("UP","DOWN"):
            trip_id = "%s_%s_%s_%s" %(route.code,unr.id,days, direction)
            #triplist.append([schedule, route, direction, trip_id])
            yield schedule, unr, route, direction, trip_id



def export_trips(routelist):
    f = make_csv_writer("trips.txt")
    f.writerow(["route_id","service_id","trip_id"])
    for schedule, route, direction, trip_id in generate_trips():
        if route not in routelist: continue
        f.writerow([route.code, schedule.schedule_type, trip_id])

    # we need to get UniqueRoutes for each route, that is one trip, since it is based on service_id which shows days_of_run.

    """
        try:
            # data checks here 

            # ternary operation :::: ('false','true')[condition]
            f.writerow([ss['code'],
                               (0,1)[ss['days'].__contains__(1)],
                               (0,1)[ss['days'].__contains__(2)],
                               (0,1)[ss['days'].__contains__(3)],
                               (0,1)[ss['days'].__contains__(4)],
                               (0,1)[ss['days'].__contains__(5)],
                               (0,1)[ss['days'].__contains__(6)],
                               (0,1)[ss['days'].__contains__(7)],
                               start_date,
                               end_date
                               ])            
        except:
            print "Error:", str(ss) + '\t' +  str(sys.exc_info()[0]) + '\n'                
            """

def getserial(rdlist,stop):
    #check if rdlist is of a ring route..
    if rdlist[0].route.code[3]== 'R' or '4' :
        # write ring specific code here. rings have multiple occuring stops, which one to choose??
        pass
        #return None    
    for rd in rdlist:
        if(rd.stop==stop):
            return rdlist.index(rd)

def get_routedetail_subset(unr):
    route = unr.route
    from_stop = unr.from_stop
    to_stop = unr.to_stop
    rd_subset = rdlist[getserial(rdlist,from_stop):getserial(rdlist,to_stop)]
    
    return rd_subset
               
def runtime_in_minutes(schedule):
    runtime = schedule.runtime1 or schedule.runtime2 or schedule.runtime3 or schedule.runtime4
    if runtime: return runtime
    t_from, t_to = schedule.first_from, schedule.first_to
    if not t_from or not t_to:
        t_from, t_to = schedule.last_from, schedule.last_to
    return abs(t_from.hour * 60 + t_from.minute -
              (t_to.hour * 60 + t_to.minute))
        


def export_stop_times(routelist):
    f = make_csv_writer("stop_times.txt")
    f.writerow(["trip_id","arrival_time","departure_time","stop_id","stop_sequence"])
    
    # get trips and route details

    for schedule, unr, route, direction, trip_id in generate_trips_unr():

        if route not in routelist: continue

        #  get route in sort_order based on UP or DOWN route 
        order = "" if direction == "UP" else "-"
        rdlist = list(RouteDetail.objects.filter(route=route).order_by(order+"serial"))
        
        #details = get_routedetail_subset(unr)

        details = rdlist[getserial(rdlist,unr.from_stop):getserial(rdlist,unr.to_stop)]

        # calc avg speed for a trip. trip = unr+rs

        dist = unr.distance
        runtime = runtime_in_minutes(schedule)
        #if dist == 0.0 or runtime == 0
        avgspeed = 0.0
        if not runtime == 0.0:
            avgspeed = dist/runtime   # in km/min         
        else:
            avgspeed = 0.0

        initial_time = departure_time = schedule.first_to if direction == "UP" else schedule.first_from
        if initial_time is None:
            initial_time  = time_of("05:00:00")

        arrival_time = initial_time
        cumulative_dist = 0.0
        timedelta = 0
        today = datetime.date.today()
                
        for sequence, detail in enumerate(details):
            if detail.km:
                cumulative_dist+=float(detail.km)
                if avgspeed != 0.0:
                    offsettime = cumulative_dist/avgspeed
                    dt = datetime.datetime.combine(today, initial_time) + datetime.timedelta(seconds=offsettime*60)
                    arrival_time = dt.time()
                   # arrival_time.resolution(datetime.timedelta(0,0,1))
                    dt = datetime.datetime.combine(today, arrival_time) + datetime.timedelta(seconds=10) 
                    departure_time = dt.time()
                    #departure_time.resolution(datetime.timedelta(0,0,1))
                    f.writerow([trip_id,arrival_time.__str__().split(".")[0],departure_time.__str__().split(".")[0],detail.stop.code,sequence])
            else:
                # for non-stage stop 
                # first stop
                if sequence == 0:
                    f.writerow([trip_id,initial_time,initial_time,detail.stop.code,sequence])
                else:    
                # if this is the last stop in the route, then 
                    if sequence == len(details) - 1:
                        arrival = initial_time.hour * 60 + initial_time.minute + runtime_in_minutes(schedule)
                        arrival_time = "%02d:%02d:00" % (int(arrival/60), arrival % 60)
                        departure_time = "%02d:%02d:00" % (int(arrival/60), arrival % 60)                    
                        f.writerow([trip_id,arrival_time,departure_time,detail.stop.code,sequence])
                    else:
                        # if any other stop
                        f.writerow([trip_id,"","",detail.stop.code,sequence])
                                
            """
            # if this is the last stop in the route, then 
            if sequence == len(details) - 1:
                arrival = initial_time.hour * 60 + initial_time.minute + runtime_in_minutes(schedule)
                arrival_time = "%02d:%02d:00" % (int(arrival/60), arrival % 60)
                f.writerow([trip_id,arrival_time,departure_time,detail.stop.code,sequence])
            else:
                departure_time = ""
                f.writerow([trip_id,arrival_time,departure_time,detail.stop.code,sequence])
            """

    #routelist = getRoutesHavingAllLocs()    

    #1. get routeDetails
    #2. get unique routes as unr and the routeDetails subset as rd_subset for that uniqueroute
    #3. get all unr.routeschedules as unr.rs 
    #4. get total distance as tdist from rd_subset
    #5. get runtime from unr.rs 
    #6. get_runtime()
    #7. avgspeed = tdist/runtime... if runtime is not available then ??
    #8.  


    """
    
    
    
    for r in routelist:
        rdlist = RouteDetail.objects.filter(route=r).order_by('serial')    
        sr_no=0
        unrs  =  UniqueRoute.objects.filter(route=r).order_by('id')
        
        for unr in unrs:
            from_stop = unr.from_stop
            to_stop = unr.to_stop
            rd_subset = rdlist[getserial(rdlist,from_stop):getserial(rdlist,to_stop)]
            dist=0
            for rd in rd_subset:
                dist += rd.km
            runtime = unr.runtime1
            if not runtime:
                rs = unr.routeschedule_set.all()[0]
                #if rs.
            sr_no +=1
            for rd in rd_subset:
                f.writerow([r.code+"_"+sr_no,"","",rd.stop.id,rd.serial])
    """



"""
stop_times.txt
================================================================================================================================================
1. For each route.
2. Get rdlist = routedetails for that route.order_by('serial'). Get UniqueRoutes for the route.
3. --- scenario -- Not considering uniqueroutes--
3.1 For rd in rdlist
73.1.1 filewrite (trip_id,,,stopid,stop.serial)

----alternate scenario
3. For each UniqueRoute, get from_to stops list (rdsubset) from RouteDetail list
for unr in unrs:
from_stop, to_stop
rd_subset  = rdlist[getserial(rdlist,from_stop):getserial(rdlist,to_stop)]
"""

def time_of(timestr):
    try:
        tm = timestr.split(":")
        return datetime.time(int(tm[0]),int(tm[1]),int(tm[2]))
    except:
        return None
        
        


def export_frequencies(routelist):
    f = make_csv_writer("frequencies.txt")
    """
    EACH ROW IN FREQUENCIES
    - For an entry in atlas, [ i.e. a given trip+service_id [subset + schedule days] ] 
    If there are headway timings for diff time slots, eg. 
    h7-11, h11-16, h16-22,h22-25
    
    then
    """
    TIMESPANS = ((None,"06:59:59"),
                 ("07:00:00","10:59:59"),
                 ("11:00:00","16:59:59"),
                 ("17:00:00","19:59:59"),
                 ("20:00:00",None))
    
    f.writerow(["trip_id", "start_time","end_time","headway_secs"])
    for schedule, route, direction, trip_id in generate_trips():
        if route not in routelist: continue
        headway = (schedule.headway1,
                   schedule.headway2,
                   schedule.headway3,
                   schedule.headway4,
                   schedule.headway5)
        for span, (start_time, end_time) in enumerate(TIMESPANS):
            # getting headway timings
            # making sure the start_time is earlier than the endtime 
            # making start and end as datetime.time                
            
            if direction == "UP":
                # if 'up' then take *_from values else take *_to values from schedule
                if start_time is None:
                    start_time = schedule.first_from.__str__()
                if end_time is None:                    
                    end_time = schedule.last_from.__str__()
                # if base values are null then put default values                
                if schedule.first_from == datetime.time(0,0,0):
                    start_time = "05:00:00" # magic number here in case BEST data isnt found             
                if schedule.last_from == datetime.time(0,0,0):
                    end_time = "22:59:59" # magic number here in case BEST data  isnt found 
                # check if start_time is always earlier than end_time.. this needs to be logged soon!
                if time_of(start_time) > time_of(end_time):
                    start_time = "05:00:00" 
                if time_of(end_time) < time_of(start_time):
                    end_time = "22:59:59" 
            else:    
                if start_time is None: 
                    start_time = schedule.first_to.__str__()
                if end_time is None:
                    end_time = schedule.last_to.__str__()

                # if base values are null then put default values                
                if schedule.first_from == datetime.time(0,0,0):
                    start_time = "05:00:00" # magic number here in case BEST data isnt found             
                if schedule.last_from == datetime.time(0,0,0):
                    end_time = "22:59:59" # magic number here in case BEST data  isnt found 
                # check if start_time is always earlier than end_time.. this needs to be logged soon!
                if  time_of(start_time) >= time_of(end_time):
                    start_time = "05:00:00" # magic number here in case BEST data isnt found
                if  time_of(end_time) <= time_of(start_time):
                    end_time = "22:59:59" # magic number here in case BEST data isnt found

            if headway[span] is not None:
                f.writerow([trip_id, start_time, end_time, headway[span]*60])

def fire_up(routelist):
    if not routelist:
        routelist = getCompleteRoutes()
    export_routes(routelist)
    export_stops(routelist)
    export_frequencies(routelist)
    export_stop_times(routelist)
    export_calendar()
    export_trips(routelist)
    export_agency()
    

