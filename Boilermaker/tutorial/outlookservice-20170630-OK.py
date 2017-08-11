import requests
import uuid
import json
import time, threading

import datetime
from datetime import timedelta

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Generic API Sending
def make_api_call(method, url, token, user_email, payload = None, parameters = None):
  # Send these headers with all API calls
  headers = { 'User-Agent' : 'python_tutorial/1.0',
              'Authorization' : 'Bearer {0}'.format(token),
              'Accept' : 'application/json',
              'X-AnchorMailbox' : user_email }

  # Use these headers to instrument calls. Makes it easier
  # to correlate requests and responses in case of problems
  # and is a recommended best practice.
  request_id = str(uuid.uuid4())
  instrumentation = { 'client-request-id' : request_id,
                      'return-client-request-id' : 'true' }

  headers.update(instrumentation)

  response = None

  if (method.upper() == 'GET'):
      response = requests.get(url, headers = headers, params = parameters)
  elif (method.upper() == 'DELETE'):
      response = requests.delete(url, headers = headers, params = parameters)
  elif (method.upper() == 'PATCH'):
      headers.update({ 'Content-Type' : 'application/json' })
      response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
  elif (method.upper() == 'POST'):
      headers.update({ 'Content-Type' : 'application/json' })
      response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)

  return response

def get_me(access_token):
  get_me_url = graph_endpoint.format('/me')

  # Use OData query parameters to control the results
  #  - Only return the displayName and mail fields
  query_parameters = {'$select': 'displayName,mail'}

  r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    return r.json()
  else:
    return "{0}: {1}".format(r.status_code, r.text)

def get_my_messages(access_token, user_email):
  get_messages_url = graph_endpoint.format('/me/mailfolders/inbox/messages')

  # Use OData query parameters to control the results
  #  - Only first 10 results returned
  #  - Only return the ReceivedDateTime, Subject, and From fields
  #  - Sort the results by the ReceivedDateTime field in descending order
  query_parameters = {'$top': '60',
                      '$select': 'receivedDateTime,subject,from',
                      '$orderby': 'receivedDateTime DESC'}

  r = make_api_call('GET', get_messages_url, access_token, user_email, parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    return r.json()
  else:
    return "{0}: {1}".format(r.status_code, r.text)

def get_my_events(access_token, user_email):		#called from views.py/events
  #OK get_events_url = graph_endpoint.format('/me/events')
  #NO get_events_url = graph_endpoint.format('/Users/events')
  
  # get_events_url = graph_endpoint.format('/Users/bunker@flexwareinnovation.com/events')   # ! WORKS !!
  # get_events_url = graph_endpoint.format('/Users/Boilermaker.Conference.Room@flexwareinnovation.com/events')   # ! WORKS !!
  #OK WORKS get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/events')

  ############################### 29 June 2017 ##########################################
#########################################################################################
### Read all 4 calendars and populate 4 databases: bunkerroomschedule2, strategyroomschedule2 etc


  #OK WORKS!! get_events_url = graph_endpoint.format('/Users/bunker@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2018-03-31T11:59:00Z')
  #!! OK COOL get_events_url = graph_endpoint.format('/Users/Boilermaker.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
  # !! OK COOL get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
  get_events_url = graph_endpoint.format('/me/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2018-03-31T11:59:00Z')
  #GET /Me/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2015-05-31T04:00:00Z
  print("[get_my_events]  HELLO, Current time is: " + str(datetime.datetime.now()))
  print ("get_events_url = " + str(get_events_url)) 
  print ("user_email = " + str(user_email))
  # Use OData query parameters to control the results
  #  - Only first 10 results returned
  #  - Only return the Subject, Start, and End fields
  #  - Sort the results by the Start field in ascending order
  query_parameters = {'$top': '60',
                      '$select': 'subject,start,end,organizer,location,body,categories, BodyPreview', 
                      '$orderby': 'start/dateTime DESC'}

  r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    #28 June: re-read calendar events every 60 seconds 
    threading.Timer(60, get_my_events, [access_token, user_email]).start()
    return r.json()

  else:
    return "{0}: {1}".format(r.status_code, r.text)
