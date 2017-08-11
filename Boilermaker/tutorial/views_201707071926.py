from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from tutorial.authhelper import get_signin_url, get_token_from_code, get_access_token

from tutorial.outlookservice import get_me, get_my_messages, get_my_events, get_bunker_events, get_boilermaker_events, get_strategy_events, get_all_events  

import time
import datetime

import json
import threading

#mysql.connector is required to write calendar entries to MySQL database
import mysql.connector

import warnings
import dateutil.parser
# Create your views here.


def home(request):
  #NOT WORKING redirect_uri = request.build_absolute_uri(reverse('tutorial:gettoken'))
  
  #28 June: http is formed, but https is required for a remote access 
  redirect_uri = request.build_absolute_uri('/tutorial/gettoken/')
  #28 June: https is not working redirect_uri = 'https://192.168.52.129:8000/tutorial/gettoken/'

  print("redirect_uri = " + redirect_uri)
  sign_in_url = get_signin_url(redirect_uri)
  print("sign_in_url = " + sign_in_url)
  return HttpResponse('<a href="' + sign_in_url +'">  Click here to sign in to your Office 365 and view calendars </a> ')
  ## return HttpResponse('<a href="' + sign_in_url +'">  Click here to sign in to your Office 365 and view calendars </a>  <img src="FlexwareLogo_300x300.jpeg" align="right" height="210" width="156">  ')
  ## 30 June return HttpResponse('<a href="' + sign_in_url +'">  Click here to sign in to your Office 365 and view calendars </a>  <img src="/home/denis-python3/Desktop/python_tutorial/tutorial/templates/tutorial/FlexwareLogo_300x300.jpeg" align="right" height="210" width="156">  ')
# <a href="dulybysh.jpg"> <img src="./dulybysh.jpg" align="right" height="210" width="156"> </a>

def gettoken(request):
  auth_code = request.GET['code']
  #does not work redirect_uri = request.build_absolute_uri(reverse('tutorial:gettoken'))
  redirect_uri = request.build_absolute_uri('/tutorial/gettoken/')
  token = get_token_from_code(auth_code, redirect_uri)
  access_token = token['access_token']
  user = get_me(access_token)
  refresh_token = token['refresh_token']
  expires_in = token['expires_in']

  # expires_in is in seconds
  # Get current timestamp (seconds since Unix Epoch) and
  # add expires_in to get expiration time
  # Subtract 5 minutes to allow for clock differences
  expiration = int(time.time()) + expires_in - 300

  # Save the token in the session
  request.session['access_token'] = access_token
  request.session['refresh_token'] = refresh_token
  request.session['token_expires'] = expiration
  request.session['user_email'] = user['mail']
  # 30 June return HttpResponseRedirect(reverse('tutorial:mail'))
  #$ OK July 05 return HttpResponseRedirect(reverse('tutorial:events'))
  return HttpResponseRedirect(reverse('tutorial:all_events'))

def mail(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  user_email = request.session['user_email']
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    messages = get_my_messages(access_token, user_email)
    context = { 'messages': messages['value'] }
    return render(request, 'tutorial/mail.html', context)

def my_events(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  user_email = request.session['user_email']
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    events = get_my_events(access_token, user_email)
    '''
    events1 = get_my_events(access_token, user_email, '/me/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2018-03-31T11:59:00Z')
    context1 = { 'events': events1['value'] }

    events4 = get_my_events(access_token, user_email, '/Users/bunker@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2018-03-31T11:59:00Z')
    context4 = { 'events': events4['value'] }

    events2 = get_my_events(access_token, user_email, '/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
    context2 = { 'events': events2['value'] }
    
    events3 = get_my_events(access_token, user_email, '/Users/Boilermaker.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
    context3 = { 'events': events3['value'] }

    #$ context = dict(context2.items() + context3.items() + context4.items())
    
    context = dict(context2)
    for d in (context3, context4): context.update(d)
    
    print('context = ' + str(context))
    #context = context1 + context2 + context3 + context4
    '''
    context = { 'events': events['value'] }
    return render(request, 'tutorial/my_events.html', context)

def bunker_events(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  user_email = request.session['user_email']
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    events = get_bunker_events(access_token, user_email)
    context = { 'events': events['value'] }
    return render(request, 'tutorial/bunker_events.html', context)

def boilermaker_events(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  user_email = request.session['user_email']
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    events = get_boilermaker_events(access_token, user_email)
    context = { 'events': events['value'] }
    return render(request, 'tutorial/boilermaker_events.html', context)

def strategy_events(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  user_email = request.session['user_email']
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    events = get_strategy_events(access_token, user_email)
    context = { 'events': events['value'] }
    return render(request, 'tutorial/strategy_events.html', context)

''' 
duplicate function my_events - remove it
def my_events(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  user_email = request.session['user_email']
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    events = get_my_events(access_token, user_email)
    context = { 'events': events['value'] }
    return render(request, 'tutorial/my_events.html', context)
'''

#07 July  def dbUpdate (dict_events, db_name):

def updateDB (dict_events, db_name, db_context):
   
  cursor = db_context.cursor()

  #09 June: drop table if already exists, ignoring warning/errors if table does not exist
  with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    #$ drop_statement = 'DROP TABLE IF EXISTS %s') 
    cursor.execute("DROP TABLE IF EXISTS %s" % (db_name)) # will not warn
    #$ cursor.execute('DROP TABLE IF EXISTS boilermakerroomschedule') # will not warn
    #$ cursor.execute('DROP TABLE IF EXISTS bunkerroomschedule') # will not warn
    #$ cursor.execute('DROP TABLE IF EXISTS otherroomschedule') # will not warn
    #$ cursor.execute('CREATE TABLE strategyroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')
    cursor.execute("CREATE TABLE %s (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), organizer varchar(128), description varchar(16384) )" % (db_name) )
    #$ cursor.execute('CREATE TABLE bunkerroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')
    #$ cursor.execute('CREATE TABLE otherroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')

    #commit right after drop-create table to prevent Ignition reading data from dropped tables
    db_context.commit()	
    
  mnum = 1   	#meeting counter, used as primary key in room reservation schedules
  
  if not dict_events:
    print('[updateDB] No upcoming calendar events found.')

  for i in dict_events["value"]:
    print ('Meeting #' + str(mnum) + ' >>> Subject: ' + i["subject"] + ' >>> Location: ' + i["location"]["displayName"] + ' >>> Start Time: ' + i["start"]["dateTime"], i["start"]["timeZone"] + ' >>> End Time: ' + i["end"]["dateTime"], i["end"]["timeZone"] + ' >>> Organizer: ' + i["organizer"]["emailAddress"]["name"] + ' >>>  Desription: ' + i["bodyPreview"])
    print ('###### END OF CALENDAR EVENT #####')

    #$ 07 July 
    #add_event = ("INSERT INTO %s " %(db_name) 
    #   "(id, start_time, end_time, location, summary, organizer, description) "
    #   "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    add_event = """INSERT INTO %s (id, start_time, end_time, location, summary, organizer, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s)""" % (db_name, "%s", "%s", "%s", "%s", "%s", "%s", "%s")
    '''
    add_event = ("INSERT INTO otherroomschedule2 " 
       "(id, start_time, end_time, location, summary, organizer, description) "
       "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    '''
    starttime = dateutil.parser.parse(i["start"]["dateTime"])
    endtime = dateutil.parser.parse(i["end"]["dateTime"])
    
    data_event = (mnum, starttime , endtime, i["location"]["displayName"], i["subject"], i["organizer"]["emailAddress"]["name"], i["bodyPreview"])
    #$ data_event = (mnum, starttime , endtime, i["location"]["displayName"], i["subject"], i["organizer"]["emailAddress"]["name"], "test")

    print (add_event)
    print (data_event)
    print ("starttime: " + str(starttime))
    print ("endtime: " + str(endtime))				
    cursor.execute(add_event, data_event)

    mnum+=1
  #cursor.execute(add_event, (19, '2017-06-07 18:00:00', '2017-06-07 19:00:00', 'Bunker', '[HOLD] Trailblazer PD #4 (Balloon Launch and STEM Learning)', 'Jillian Vanarsdall', 'test'))
  db_context.commit()	
  print ("[updateDB] SQL command committed; the following DB has been updated: " + db_name) 
  cursor.close() 

def all_events(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  user_email = request.session['user_email']
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    events1 = get_my_events(access_token, user_email)
    context1 = { 'events': events1['value'] }
    #events11 = json.loads(events1)
    #$ OK for key, value in context1.items():
    #~~~ OK 6pm for key, value in events1.items():
    # 07 July: write a function updateDB (dict_events,db_name);call it: updateDB(events1, strategyroomschedule2 ) 
    cnx = mysql.connector.connect(user='root', password='password', 
                              host='sparksvm.eastus.cloudapp.azure.com',
    #			      port=3306,
                              database='roomreservations')

    updateDB(events1, 'otherroomschedule2', cnx) 
    
    #$ OK print (context1) 
    ##% for event1 in events1:
      #start = event.get.start.dateTime #event['start'].get('dateTime', event['start'].get('date'))
      #end = event['end'].get('dateTime', event['end'].get('date'))
      #location = event.get('location', '')
      #location = event.location
      #summary = event.get('subject', '')
      #description = event.get('body.content', '')
      ## print (event[0].value.location)  
      ## print (' >>>>>>>>> \r\n')  
      ## print(event[1])
      #print(' start time: ' + start + '; End time: ' + end + '; Location: ' + location + ' ; Summary: ' + summary + ' ; Description: ' + description )
  
    print (' >>>>>>>>> \r\n') 
    '''
    print (event1)
    print (' >>>>>>>>> \r\n') 
    '''
    #.location.displayName)
    #response_dict.get("scans",{}).get("AVG",{})

    events2 = get_bunker_events(access_token, user_email)
    context2 = { 'events': events2['value'] }

    events3 = get_boilermaker_events(access_token, user_email)
    context3 = { 'events': events3['value'] }

    #$ Strategy Room events are already read in get_all_events() function - ? 
    events4 = get_strategy_events(access_token, user_email)
    context4 = { 'events': events4['value'] }

    context = dict(context1, **context2) 
    context.update(context3) 
    context.update(context4)
 
    print("[views.py/all_events]  HOLA, Databases have been updated. Current time is: " + str(datetime.datetime.now()))
    threading.Timer(60, all_events, [request]).start()

    cnx.close()

  return render(request, 'tutorial/strategy_events.html', context)


