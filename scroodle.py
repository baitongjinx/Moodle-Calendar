#~ Scroodle for linux
#~ Description: Extracts data from the moodle calendar and adds the events into the person's google calendar
#~ Parameters: Specified in accompanying file 
#~ Author: Giri Prashant, max.payne7891@gmail.com
#~ Date: 31/8/2012
#~ _________________________________________________________________________________________________________


import sys
import os
import time
import getpass
from moodle_calendar import *
from CheckEventExistance import *
from gdata.calendar.client import *

def InsertEventInCalendar(function,event, tries, msg):
    '''Attempt a Google data API call, retry on fail.

    Google data API has some intermittent errors that pop up randomly.  This
    allows us to try the request a few times.
    '''

    for currentTry in range(1, tries + 1):        
        try:
            result = function(event)
        except:
            result = ''
        else:
            # Success! Get out of this loop.
            break

        tries -= 1
        time.sleep(10.0)

    return result

# Uptil this point in the code the encrypted file has been decrypted and each line in the decrypted file is one element in the array "lines".
# The encryption code has not been shared for security purposes. This is the code for ubuntu users, but the code is the same for windows users as well except for the system commands that have been used.
	
moodle_username = lines[0].replace('LDAP username:','').strip()
moodle_password = lines[1].replace('LDAP password:','').strip()
gmail_username = lines[2].replace('Google username:','').strip()
gmail_password = lines[3].replace('Google password:','').strip()
proxy_flag = lines[4].replace('Use proxy? Enter 1 for yes or 0 for no:','').strip()

os.system('notify-send Scroodle "Started Execution"')
while True:
		
	moodle_events_list,invalid_login = moodle_calendar(moodle_username,moodle_password)

	if proxy_flag:	
		os.environ['http_proxy'] = 'http://netmon.iitb.ac.in:80' 
		os.environ['https_proxy'] = 'https://netmon.iitb.ac.in:80' 
		os.environ['proxy-username'] = moodle_username 
		os.environ['proxy-password'] = moodle_password 

	calendar_client = gdata.calendar.client.CalendarClient()
		

	for i in range(100):
		try:
		  calendar_client.ClientLogin(gmail_username, gmail_password, "test",service='cl')

		except gdata.client.CaptchaChallenge as challenge:
		  print 'Please visit ' + challenge.captcha_url
		  answer = raw_input('Answer to the challenge? ')
		  calendar_client.ClientLogin(gmail_username, gmail_password, "test",captcha_token=challenge.captcha_token,captcha_response=answer)

		except gdata.client.BadAuthentication:
			notification = 'notify-send Scroodle "Google username and password dont match. Please try again"'
			os.system(notification)
			sys.exit()
		
		except:
			continue
		else:
			break
		time.sleep(10)


	if invalid_login:
		notification = 'notify-send Scroodle "Moodle username and password dont match. Please try again"'
		os.system(notification)
		sys.exit()

	for i in range(len(moodle_events_list)):
		
		current_event = moodle_events_list[i]
		current_event_details = current_event.split('|')
		
		if len(current_event_details[-2]) == 1:
			month = '0'+ current_event_details[-2]	
		else:
			month = current_event_details[-2]	
		
		if len(current_event_details[-3]) == 1:
			start_date = '0'+ current_event_details[-3]	
		else:
			start_date = current_event_details[-3]
		
		if len(str(int(current_event_details[-3])+1)) == 1:
			end_date = '0'+ str(int(current_event_details[-3])+1)
		else:
			end_date = str(int(current_event_details[-3])+1)		
			
		
		start_time = current_event_details[-1] + '-' + month + '-' + start_date	
		end_time = current_event_details[-1] + '-' +  month + '-' + end_date
		title = current_event_details[1]
		content = current_event_details[0]+'@'+current_event_details[2]
		
		query = gdata.calendar.client.CalendarEventQuery(start_min=start_time, start_max=end_time)	
		existance_state = CheckEventExistance(query,calendar_client,title,content)
		
		if not existance_state:
			print_event = 'Added %s of %s on %s' %(content,title,start_time)
			notification = 'notify-send Scroodle "' + print_event + '"'
			os.system(notification)
			new_event = gdata.calendar.data.CalendarEventEntry()
			new_event.title = gdata.atom.data.Title(text=title)
			new_event.content = gdata.atom.data.Content(text=content)
			new_event.when.append(gdata.data.When(start=start_time, end=end_time))	

			output = InsertEventInCalendar(calendar_client.InsertEvent,new_event,100,'Trial')
	
	time.sleep(7200)
