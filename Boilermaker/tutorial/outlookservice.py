import requests
import uuid
import json
import time, threading

import datetime
from datetime import timedelta

import dateutil.parser

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Generic API Sending
def make_api_call(method, url, token, user_email, payload = None, parameters = None):
  # Send these headers with all API calls
  headers = { 'User-Agent' : 'python_tutorial/1.0',
              'Authorization' : 'Bearer {0}'.format(token),
              'Accept' : 'application/json',
              'X-AnchorMailbox' : user_email }
  #              'timezone'        : 'Eastern Standard Time'}    #not working

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

def get_my_events(access_token, user_email):		#called from views.py/my_events
  #OK get_events_url = graph_endpoint.format('/me/events')
  #NO get_events_url = graph_endpoint.format('/Users/events')
  
  # get_events_url = graph_endpoint.format('/Users/bunker@flexwareinnovation.com/events')   # ! WORKS !!
  # get_events_url = graph_endpoint.format('/Users/Boilermaker.Conference.Room@flexwareinnovation.com/events')   # ! WORKS !!
  #OK WORKS get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/events')
  #
  ############################### 29 June 2017 ##########################################
#########################################################################################
### Read all 4 calendars and populate 4 databases: bunkerroomschedule2, strategyroomschedule2 etc

  #OK WORKS!! get_events_url = graph_endpoint.format('/Users/bunker@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2018-03-31T11:59:00Z')
  #!! OK COOL get_events_url = graph_endpoint.format('/Users/Boilermaker.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
  # !! OK COOL get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
 

  #OK WORKS July, 5 
  #11 July get_events_url = graph_endpoint.format('/me/CalendarView?startDateTime=2017-05-08T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')

  #17 July 
  _StartRetrievingTime = datetime.datetime.utcnow() - timedelta(days=1)
  StartRetrievingTime = dateutil.parser.parse(str( _StartRetrievingTime ) )
  #retrieve events from 5 days back, i.e. within 1 working week

  _EndRetrievingTime = datetime.datetime.utcnow() + timedelta(days=14)
  EndRetrievingTime = dateutil.parser.parse(str( _EndRetrievingTime ) )
  
  #OK worked 16 July get_events_url = graph_endpoint.format('/me/CalendarView?startDateTime=2017-05-08T04:00:00&endDateTime=2017-12-31T11:59:00')
  get_events_url = graph_endpoint.format('/me/CalendarView?startDateTime=' + str(StartRetrievingTime) + '&endDateTime=' + str(EndRetrievingTime) )
  #$ July, 5 get_events_url = graph_endpoint.format(calname);

  #GET /Me/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2015-05-31T04:00:00Z
  print ("[get_my_events] HELLO, Current time is: " + str(datetime.datetime.now()))
  print ("[get_my_events] get_events_url = " + str(get_events_url)) 
  print ("[get_my_events] user_email = " + str(user_email))
  # Use OData query parameters to control the results
  #  - Only first 10 results returned
  #  - Only return the Subject, Start, and End fields
  #  - Sort the results by the Start field in descending order
  #10 July query_parameters = {'$top': '30',
  #                    '$select': 'subject,start,end,organizer,location,body,categories, BodyPreview', 
  #                    '$orderby': 'start/dateTime DESC'}
  
  #10 July test query_parameters = '?$select=Subject, Start, End, Location,BodyPreview&$orderby=start/dateTime desc&$top=30'
  query_parameters = {'$top': '20',
                      '$select': 'subject,start,end,organizer,location,bodyPreview', 
                      '$orderby': 'start/dateTime ASC'}
  r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    #28 June: re-read calendar events every 60 seconds 
    
    #$ 06 July - now thread is created in views.py/all_events 
    #$ 06 July threading.Timer(60, get_my_events, [access_token, user_email]).start()
    return r.json()

  else:
    return "{0}: {1}".format(r.status_code, r.text)

def get_strategy_events(access_token, user_email):		#called from views.py/strategy_events
  #get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2016-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
  #~ OK 12 July get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2017-05-08T04:00:00&endDateTime=2017-12-31T11:59:00')

  _StartRetrievingTime = datetime.datetime.utcnow() - timedelta(days=1)
  StartRetrievingTime = dateutil.parser.parse(str( _StartRetrievingTime ) )
  #retrieve events from 5 days back, i.e. within 1 working week

  _EndRetrievingTime = datetime.datetime.utcnow() + timedelta(days=14)
  EndRetrievingTime = dateutil.parser.parse(str( _EndRetrievingTime ) )

  get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=' + str(StartRetrievingTime) + '&endDateTime=' + str(EndRetrievingTime) )
  
  print("[get_strategy_events]  HELLO, Current time is: " + str(datetime.datetime.now()))
  print ("[get_strategy_events] get_events_url = " + str(get_events_url)) 
  print ("[get_strategy_events] user_email = " + str(user_email))
  #  - Only return the Subject, Start, and End fields
  #  - Sort the results by the Start field in ascending order
  query_parameters = {'$top': '20',
                      '$select': 'subject,start,end,organizer,location,bodyPreview', 
                      '$orderby': 'start/dateTime ASC'}

  r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    #28 June: re-read calendar events every 120 seconds 

    #$ 06 July - now thread is created in views.py/all_events 
    #$ 06 July threading.Timer(60, get_strategy_events, [access_token, user_email]).start()

    #$ WORKS OK 06 July events = r.json().items()
    #$ 06 July print("r.json.events = " + str(events) )
    #$ context1 = { 'events': r.json().events }
    #$ context1 = { 'events': r.json['value'] }
    return r.json()

  else:
    return "{0}: {1}".format(r.status_code, r.text)

def get_bunker_events(access_token, user_email):		#called from views.py/bunker_events

  #17 July 
  _StartRetrievingTime = datetime.datetime.utcnow() - timedelta(days=1)
  StartRetrievingTime = dateutil.parser.parse(str( _StartRetrievingTime ) )
  #retrieve events from 5 days back, i.e. within 1 working week

  _EndRetrievingTime = datetime.datetime.utcnow() + timedelta(days=14)
  EndRetrievingTime = dateutil.parser.parse(str( _EndRetrievingTime ) )

  #OK Worked 16 July get_events_url = graph_endpoint.format('/Users/bunker@flexwareinnovation.com/CalendarView?startDateTime=2017-05-08T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
  get_events_url = graph_endpoint.format('/Users/bunker@flexwareinnovation.com/CalendarView?startDateTime=' + str(StartRetrievingTime) + '&endDateTime=' + str(EndRetrievingTime) )  
 
  #GET /Me/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2015-05-31T04:00:00Z
  print("[get_bunker_events]  HELLO, Current time is: " + str(datetime.datetime.now()))
  print ("[get_bunker_events] get_events_url = " + str(get_events_url)) 
  print ("[get_bunker_events] user_email = " + str(user_email))
  # Use OData query parameters to control the results
  #  - Only first 10 results returned
  #  - Only return the Subject, Start, and End fields
  #  - Sort the results by the Start field in descending order
  query_parameters = {'$top': '20',
                      '$select': 'subject,start,end,organizer,location,bodyPreview', 
                      '$orderby': 'start/dateTime ASC'}

  r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    #28 June: re-read calendar events every 120 seconds 
    
    #$ 06 July - now thread is created in views.py/all_events 
    #$ 06 July threading.Timer(60, get_bunker_events, [access_token, user_email]).start()
    return r.json()

  else:
    return "{0}: {1}".format(r.status_code, r.text)

def get_boilermaker_events(access_token, user_email):		#called from views.py/boilermaker_events
 
  #17 July 
  _StartRetrievingTime = datetime.datetime.utcnow() - timedelta(days=1)
  StartRetrievingTime = dateutil.parser.parse(str( _StartRetrievingTime ) )
  #retrieve events from 5 days back, i.e. within 1 working week

  _EndRetrievingTime = datetime.datetime.utcnow() + timedelta(days=14)
  EndRetrievingTime = dateutil.parser.parse(str( _EndRetrievingTime ) )  

  get_events_url = graph_endpoint.format('/Users/Boilermaker.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=' + str(StartRetrievingTime) + '&endDateTime=' + str(EndRetrievingTime) )  
  #OK 17 July Worked  get_events_url = graph_endpoint.format('/Users/Boilermaker.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2017-05-08T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')

  print("[get_boilermaker_events]  HELLO, Current time is: " + str(datetime.datetime.now()))
  print ("[get_boilermaker_events] get_events_url = " + str(get_events_url)) 
  print ("[get_boilermaker_events] user_email = " + str(user_email))
  # Use OData query parameters to control the results
  #  - Only first 10 results returned
  #  - Only return the Subject, Start, and End fields
  #  - Sort the results by the Start field in ascending order
  query_parameters = {'$top': '20',
                      '$select': 'subject,start,end,organizer,location,bodyPreview',
                      '$orderby': 'start/dateTime ASC'}

  r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    #28 June: re-read calendar events every 60 seconds 

    #$06 July - now thread is created in views.py/all_events 
    #$06 July threading.Timer(60, get_boilermaker_events, [access_token, user_email]).start()
    return r.json()

  else:
    return "{0}: {1}".format(r.status_code, r.text)

### 10 July: the function 'get_all_events' is not called in the latest version 
'''
def get_all_events(access_token, user_email):		#called from views.py/my_events
#OK WORKS!! get_events_url = graph_endpoint.format('/Users/bunker@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2018-03-31T11:59:00Z')
  #!! OK COOL get_events_url = graph_endpoint.format('/Users/Boilermaker.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
  # !! OK COOL get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
 
  #$ OK July 05 get_events_url = graph_endpoint.format('/Users/Strategy.Conference.Room@flexwareinnovation.com/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2017-12-31T11:59:00Z')
  #OK WORKS July, 5 
  get_events_url = graph_endpoint.format('/me/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2018-03-31T11:59:00Z')
  
  #$ July, 5 get_events_url = graph_endpoint.format(calname);

  #GET /Me/CalendarView?startDateTime=2015-05-30T04:00:00Z&endDateTime=2015-05-31T04:00:00Z
  print("[get_all_events]  HELLO, Current time is: " + str(datetime.datetime.now()))
  print ("[get_all_events] get_events_url = " + str(get_events_url)) 
  print ("[get_all_events] user_email = " + str(user_email))
  # Use OData query parameters to control the results
  #  - Only first 10 results returned
  #  - Only return the Subject, Start, and End fields
  #  - Sort the results by the Start field in ascending order
  query_parameters = {'$top': '30',
                      '$select': 'subject,start,end,organizer,location,body,categories, BodyPreview', 
                      '$orderby': 'start/dateTime DESC'}

  r = make_api_call('GET', get_events_url, access_token, user_email, parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    #28 June: re-read calendar events every 60 seconds 
    #$ July 05 threading.Timer(60, get_all_events, [access_token, user_email]).start()
    return r.json()

  else:
    return "{0}: {1}".format(r.status_code, r.text)
'''

# Creates an event in the Calendar
#   parameters:
#   calendar_endpoint: string. The URL to Calendar API endpoint (https://outlook.office365.com/api/v1.0)
#   token: string. The access token 
#   event_payload: string. A JSON representation of the new event.  
def create_event(calendar_endpoint, token, event_payload):
  print(' [create_event] Entering create_event. ')
  print(' calendar_endpoint: {0} '.format(calendar_endpoint))
  print(' token: {0} '.format(token))
  print(' event_payload: {0}'.format(event_payload))
                
  create_event = '{0}/Me/Events'.format(calendar_endpoint)
    
  r = make_api_call('POST', create_event, token, event_payload)
    
  print('Response: {0}'.format(r.json()))
  print('[create_event] Leaving create_event.')
    
  return r.status_code

def update_event(calendar_endpoint, token, event_id, update_payload):
    print(' Entering update_event.')
    print('  calendar_endpoint: {0}'.format(calendar_endpoint))
    print('  token: {0}'.format(token))
    print('  event_id: {0}'.format(event_id))
    print('  update_payload: {0}'.format(update_payload))
                
    update_event = '{0}/Me/Events/{1}'.format(calendar_endpoint, event_id)
    
    r = make_api_call('PATCH', update_event, token, update_payload)

    print('Response: {0}'.format(r.json()))
    print('Leaving update_event.')
    
    return r.status_code

