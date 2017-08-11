from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from tutorial.authhelper import get_signin_url, get_token_from_code, get_access_token

from tutorial.outlookservice import get_me, get_my_messages, get_my_events, get_bunker_events, get_boilermaker_events, get_strategy_events #get_all_events  

import time
import datetime

import json
import threading

#mysql.connector is required to write calendar entries to MySQL database
import mysql.connector

import warnings
import dateutil.parser
import sys
import os

# from datetime import timedelta, datetime
# 11 July from datetime import tzinfo, timedelta, datetime
# 11 July from pytz import timezone
from dateutil import tz

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/New_York')

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

def updateDB (dict_events, table_name, db_context, status_table_name):
  cursor = db_context.cursor()

  #09 June: drop table if already exists, ignoring warning/errors if table does not exist
  with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    # 14 July cursor.execute("DROP TABLE IF EXISTS %s" % (db_name)) # will not warn
    # 14 July cursor.execute("CREATE TABLE %s (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), organizer varchar(128), description varchar(16384) )" % (db_name) )
    cursor.execute("CREATE TABLE IF NOT EXISTS %s (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), organizer varchar(128), description varchar(16384) )" % (table_name) )
    cursor.execute("DELETE FROM %s" % (table_name)) # will not warn

    #~~~ create table to store status of the meeting room: available / taken 
    # 17 July - drop table is temporary for debugging purposes
    #17 July cursor.execute("DROP TABLE IF EXISTS %s" % (status_table_name))
    cursor.execute("CREATE TABLE IF NOT EXISTS %s (id int, isTakenStatus varchar(16) )" % (status_table_name) )
    #~ no need to delete cursor.execute("DELETE FROM %s" % (status_table_name)) # will not warn

    #$ cursor.execute('CREATE TABLE bunkerroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')

    #commit right after drop-create table to prevent Ignition reading data from dropped tables
    #14 July  db_context.commit()	#no need to commit empty table - populate it with data first

    #17 July: create one more table with name table_name2, which is StrategyRoomStatus, i.e. add one more argumet to updateDB function. Schema:    roomname | status 
    #					      Strategy | Taken
    # 					      Bunker   | Available
    # here (before cycle) write "Available" (0) to status,which will be 'RoomTaken'variable in Ignition  
    room_status = 'Available'
    cursor.execute("DELETE FROM %s" % (status_table_name)) # will not warn
    add_status_event = """INSERT INTO %s (id, isTakenStatus)
    VALUES (%s, %s)""" % (status_table_name, "%s", "%s")
    data_status_event = (1, room_status)
    cursor.execute(add_status_event, data_status_event)
    db_context.commit()
    
  mnum = 1   	#meeting counter, used as primary key in room reservation schedules
  
  if not dict_events:
    print('[updateDB] No upcoming calendar events found.')

  for i in dict_events["value"]:
    if i["subject"] is None:
      i["subject"] = 'Not Specified'
    if i["location"]["displayName"] is None:
      i["location"]["displayName"] = 'Not Specified' 
    if i["bodyPreview"] is None:
      i["bodyPreview"] = '.' 
  
    print ('Meeting #' + str(mnum) + ' >>> Subject: ' + i["subject"] + ' >>> Location: ' + i["location"]["displayName"] + ' >>> Start Time: ' + i["start"]["dateTime"], i["start"]["timeZone"] + ' >>> End Time: ' + i["end"]["dateTime"], i["end"]["timeZone"] + ' >>> Organizer: ' + i["organizer"]["emailAddress"]["name"] + ' >>>  Desription: ' + i["bodyPreview"])
    #10 July  print ('Subject: ' + str(i["subject"]) + ' >>> Location: ' + str(i["location"]["displayName"]) + ' >>> Start Time: ' + str(i["start"]["dateTime"]), str(i["start"]["timeZone"]) + ' >>> End Time: ' + str(i["end"]["dateTime"]), str(i["end"]["timeZone"]) + ' >>> Organizer: ' + str(i["organizer"]["emailAddress"]["name"]) + ' >>>  Desription: ' + str(i["bodyPreview"]))
    print ('###### END OF CALENDAR EVENT #####')

    add_event = """INSERT INTO %s (id, start_time, end_time, location, summary, organizer, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s)""" % (table_name, "%s", "%s", "%s", "%s", "%s", "%s", "%s")

    _starttime = dateutil.parser.parse(i["start"]["dateTime"])
    _starttime = _starttime.replace(tzinfo=from_zone)
    starttime = _starttime.astimezone(to_zone)
    _endtime = dateutil.parser.parse(i["end"]["dateTime"])
    _endtime = _endtime.replace(tzinfo=from_zone)
    endtime = _endtime.astimezone(to_zone)
    
    _currtime = datetime.datetime.now()
    _currtime = _currtime.replace(tzinfo=from_zone)
    currtime = _currtime.astimezone(to_zone)

    data_event = (mnum, starttime , endtime, i["location"]["displayName"], i["subject"], i["organizer"]["emailAddress"]["name"], i["bodyPreview"])
    
    cursor.execute(add_event, data_event)

    #17 July - logic to determien the status of a meeting room" available / taken
    if (starttime < currtime) and (endtime > currtime): 
      room_status = 'Taken'
      #17 July add_status_event = """INSERT INTO %s (roomname, isTakenStatus)
      # VALUES (%s, %s)""" % (status_table_name, "%s", "%s")
      add_status_event = "UPDATE %s SET id=%s, isTakenStatus=%s" % (status_table_name, "%s", "%s")
      print('add_status_event = ' + add_status_event)
      data_status_event = (1, room_status)
      cursor.execute(add_status_event, data_status_event)
      db_context.commit()

      print('[updateDB]: room: ' + table_name + ' is taken..., room_taken = ' + str(room_status) )
      #17 July: write 1 to the MySQL database 
      
    mnum+=1
  db_context.commit()	
  print ("[updateDB] SQL command committed; the following DB has been updated: " + table_name) 
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

    cnx = mysql.connector.connect(user='root', password='password', 
                              host='sparksvm.eastus.cloudapp.azure.com',
    #			      port=3306,
                              database='roomreservations')

    updateDB(events1, 'otherroomschedule2', cnx, 'OtherRoomStatus') 
    print ('[all_events]: >>>> otherroomschedule2 has been updated ....... \r\n') 

    events2 = get_bunker_events(access_token, user_email)
    context2 = { 'events': events2['value'] }
    #time.sleep(1)
    updateDB(events2, 'bunkerroomschedule2', cnx, 'BunkerRoomStatus')
    print ('[all_events]: >>>> bunkerroomschedule2 has been updated ....... \r\n')  

    events3 = get_boilermaker_events(access_token, user_email)
    context3 = { 'events': events3['value'] }
    updateDB(events3, 'boilermakerroomschedule2', cnx, 'BoilermakerRoomStatus')
    print ('[all_events]: >>>> boilermakerroomschedule2 has been updated ....... \r\n')  

    #$ Strategy Room events are already read in get_all_events() function - ? 
    events4 = get_strategy_events(access_token, user_email)
    context4 = { 'events': events4['value'] }
    updateDB(events4, 'strategyroomschedule2', cnx, 'StrategyRoomStatus')
    print ('[all_events]: >>>> strategyroomschedule2 has been updated ....... \r\n')  

    '''
    context = dict(context1, **context2) 
    context.update(context3) 
    context.update(context4)
    10 July
    '''
    print("[views.py/all_events] Databases have been updated. Current time is:" + str(datetime.datetime.now()))
    threading.Timer(600, all_events, [request]).start()

    cnx.close()

    #19 July sys.exit()
    #os.system('pkill -f runsslserver')
    #restart_script()

  return render(request, 'tutorial/strategy_events.html', context4)

def restart_script():
  #os.system('pkill -f runsslserver')
  #sleep(1)
  os.system('ls -la')
  os.system('pwd')
  #os.system('python3 manage.py runsslserver 0:8000 > logroomsfile.txt ')
   
