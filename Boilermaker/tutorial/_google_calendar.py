from __future__ import print_function
import httplib2
import os
import os.path

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
from datetime import timedelta
import dateutil.parser

#mysql.connector is required to write calendar entries to MySQL database
import mysql.connector

import warnings

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

logfilename = "ReadingCalendar.log"

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_calendars(googleservice):
    ''' 
    get all available calendars 
    '''
    # 07 June: figure out from which calendar the entries are read. Currently it is svp
    page_token = None
    while True:
	calendar_list = googleservice.calendarList().list(pageToken=page_token).execute()
	for calendar_list_entry in calendar_list['items']:
    	    print (calendar_list_entry['summary'])
  	page_token = calendar_list.get('nextPageToken')
	if not page_token:
    	    break 

def Write_LogRecord(logfiledesc, db_name, i_mnum, dt_start, dt_end, str_location, str_summary):
 
    logfiledesc.write('[Meeting number: ' + str(i_mnum) + '; DB name: ' + str(db_name) + '] ;  start time: ' + dt_start + '; End time: ' + dt_end + '; Location: ' + str(str_location) + ' ; Summary: ' + str(str_summary) + '\n')

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    N = maxResults events on the user's calendar.
    """
    
    #maxResults: number of calendar entries to be read. If metings at Flexware can occur from 7am to 9pm and
    #can be scheduled for no less than 15 minutes,then there could be 60 meetings per day in a room 	
    maxRes=int(60) 	
	
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    print ("service = " + str(service))

    get_calendars(service)   #Check what calendars are available.     

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # now = datetime.datetime.utcnow().isoformat()           # 'Z' indicates UTC time
    print('Current date and time:  ' + str(now))
    NowTime = dateutil.parser.parse(now)  #used to measure script execution time 
    print('Getting the upcoming N = ' + str(maxRes) + ' calendar events')
    # print('Getting the upcoming N=60 events')
    #d = datetime.today() - timedelta(days=1)

    # calendar entries will be retrieved from google calendar starting from 1 day from the past from now
    StartRetrievingTime = datetime.datetime.utcnow() - timedelta(days=1)
    #debug print (StartRetrievingTime) 

    #without conversion to isoformat and string type the google api call doesn't work
    strStartRetrievingTime = str(StartRetrievingTime.isoformat() + 'Z')
    print ("Google calendar entries will now be retrieved starting from date: " + strStartRetrievingTime) 
    
    '''
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxRes, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    '''
   
    '''
    WORKS OK but just retrieves 60 calendar entries starting from now.I also need 1 day from the past   
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=60, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    END OF WORKABLE FRAGMENT 
    '''
    eventsResult = service.events().list(
        calendarId='primary', timeMin=strStartRetrievingTime, maxResults=60, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', []) 

    # room selector: do we assume one calendar per room and we know what room does the calendar belong to? 

    #connect to a MySQL database of calendar events and prepare cursor to write events into it

    #local config WORKS FINE 
    '''
    cnx = mysql.connector.connect(user='root', password='password',
                              host='127.0.0.1',
    #			      port=3306,
                              database='roomreservations')
    '''
    cnx = mysql.connector.connect(user='root', password='password',
                              host='sparksvm.eastus.cloudapp.azure.com',
    #			      port=3306,
                              database='roomreservations')
    
    cursor = cnx.cursor()

    #09 June: drop table if already exists, ignoring warning/errors if table does not exist
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute('DROP TABLE IF EXISTS strategyroomschedule') # will not warn
        cursor.execute('DROP TABLE IF EXISTS boilermakerroomschedule') # will not warn
        cursor.execute('DROP TABLE IF EXISTS bunkerroomschedule') # will not warn
	cursor.execute('DROP TABLE IF EXISTS otherroomschedule') # will not warn
        cursor.execute('CREATE TABLE strategyroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')
	cursor.execute('CREATE TABLE boilermakerroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')
	cursor.execute('CREATE TABLE bunkerroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')
	cursor.execute('CREATE TABLE otherroomschedule (id int PRIMARY KEY, start_time datetime, end_time datetime, location varchar(128), summary varchar(256), description varchar(16384) )')

	#commit right after drop-create table to prevent Ignition reading data from dropped tables
	cnx.commit()	

    mnum = 1   	#meeting counter, used as primary key in room reservation schedules
    
    if os.path.exists(logfilename):
	append_write = 'a' # append if already exists
    else:
	append_write = 'w' # make a new file if not
    log_record = open(logfilename, append_write)
    log_record.write('\n' + '[----------------- NEW SCRIPT ITERATION STARTS AT: ' + str(datetime.datetime.utcnow().isoformat()) + '... ]' + '\n')

    if not events:
        print('No upcoming calendar events found.')
    for event in events:
	start = event['start'].get('dateTime', event['start'].get('date'))

	#DAU, 26 May 2017   
	end = event['end'].get('dateTime', event['end'].get('date'))

	#20 June: event['location'] crashes for some events     location = str(event['location'])
	#20 June print('location old option' + location)

	location = event.get('location', '')   	#print('location new option' + 	event.get('location', ''))
	summary = event.get('summary', '') 
	# description = str(event['description'])
	description = event.get('description', '')
        
	#OK, works print(start, event['summary'])
	# 06 June print('Meeting #' + str(mnum) + ' start time: ' + start, '; End time: ' + end, '; Summary: ' + event['summary'], '; Description: ' + event['description'])

        # 06 June print('Meeting #' + str(mnum) + ' start time: ' + start + '; End time: ' + end + '; Location: ' + event['location'] + ' ; Summary: ' + event['summary'] + ' ; Description: ' + event['description'] )

	#$ if location == "Strategy Conference Room":
	#OK worked before June, 20 2017 
	#$ print('Meeting #' + str(mnum) + ' start time: ' + start + '; End time: ' + end + '; Location: ' + event['location'] + ' ; Summary: ' + summary + ' ; Description: ' + description )

	print('Meeting #' + str(mnum) + ' start time: ' + start + '; End time: ' + end + '; Location: ' + location + ' ; Summary: ' + summary + ' ; Description: ' + description )
        #populate MySQL database with google calendar entries
	starttime = dateutil.parser.parse(start)
	endtime = dateutil.parser.parse(end)
	#$ June, 21 OK IT WORKS if location == "Strategy Conference Room":
	if "trategy" in location:
    	    add_event = ("INSERT INTO strategyroomschedule "
       "(id, start_time, end_time, location, summary, description) "
       "VALUES (%s, %s, %s, %s, %s, %s)")
	    Write_LogRecord(log_record, 'strategyroomschedule', mnum, start, end, location, summary)

	#OK IT WORKS elif location == "Boilermaker Conference Room":
	elif "oilermaker" in location:
    	    add_event = ("INSERT INTO boilermakerroomschedule "
       "(id, start_time, end_time, location, summary, description) "
       "VALUES (%s, %s, %s, %s, %s, %s)")
	    Write_LogRecord(log_record, 'boilermakerroomschedule', mnum, start, end, location, summary)

	#$ OK IT WORKS June 21 elif location == "Bunker":
	elif "unker" in location:
    	    add_event = ("INSERT INTO bunkerroomschedule "
       "(id, start_time, end_time, location, summary, description) "
       "VALUES (%s, %s, %s, %s, %s, %s)")
	    Write_LogRecord(log_record, 'bunkerroomschedule', mnum, start, end, location, summary)	    
# Write_LogRecord(log_record, 'bunkerroomschedule', mnum, start, end, location, summary, description)
	else:
	    add_event = ("INSERT INTO otherroomschedule "
       "(id, start_time, end_time, location, summary, description) "
       "VALUES (%s, %s, %s, %s, %s, %s)")
	    Write_LogRecord(log_record, "otherroomschedule", mnum, start, end, location, summary)

	data_event = (mnum+2000, starttime, endtime, location, summary, description)
        # Insert new calendar event
	cursor.execute(add_event, data_event)

        '''
        #datetime type issue: '2013-08-25T17:00:00+00:00' is a valid iso-8601 datetime value
        # but not a valid MySQL literal does not understand
        '''
        # cursor.execute(add_event, data_event) 

        mnum+=1

    '''
    # test that I am able to insert/update tuples to MySQL database - insert just one tuple - !! IT WORKS
    starttime = dateutil.parser.parse(start)
    #starttime = datetime.datetime.strptime(start, "%Y-%m-%d \'T' %H-%M-%S (UTC)") 
    print (starttime)
    endtime = dateutil.parser.parse(end)

    add_event = ("INSERT INTO strategyroomschedule "
       "(id, start_time, end_time, location, summary, description) "
       "VALUES (%s, %s, %s, %s, %s, %s)")
 
    #OK data_event = (mnum+15, '2017-06-07 18:00:00', '2017-06-07 19:00:00', location, summary, description)
    data_event = (mnum+19, starttime, endtime, location, summary, description)
    cursor.execute(add_event, data_event) 
    '''

    cnx.commit()
    print ("SQL command committed...")

    cursor.close()

    cnx.close()
    
    #Added on June , 14  in order to maintain log file of operations 
    nowend = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    #nowend has type str. To convert it to datetime - the dateutil.parser.parse(nowend) call is required
    EndTime = dateutil.parser.parse(nowend)
    operation_time = EndTime-NowTime;
    print('Updating databases of calendar events completed. Operation time:   ' + str(operation_time))
    
    log_record.write('\n' + '[----------------- SCRIPT ITERATION ENDED AT: ' + str(datetime.datetime.utcnow().isoformat()) + '... ]. Operation time: ' + str(operation_time) + '\n')
    log_record.close()

if __name__ == '__main__':
    main()


