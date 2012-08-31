
def moodle_calendar(username,password):
	
	import cookielib,urllib2,getpass,urllib,re

	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	login_data = urllib.urlencode({'username':username, 'password': password })
	opener.open('http://moodle.iitb.ac.in/login/index.php', login_data)
	url=opener.open('http://moodle.iitb.ac.in')
	url=url.read()
	
	login_details = re.compile('You are not logged in')
	
	invalid_login = login_details.findall(str(url))
	invalid_login_flag = 0
	
	if len(invalid_login)!=0:
		invalid_login_flag = 1
	
	events = re.compile('<td.*hasevent.*</a>')
	
	all_events = events.findall(str(url))
	assignment_details = []

	for i in range(len(all_events)):
		
		string = all_events[i]
		day = string.split('cal_d')[1].split('&')[0]
		day = day[1:]
		month = string.split('cal_m')[1].split('&')[0]
		month = month[1:]
		year = string.split('cal_y')[1].split('#')[0]
		year = year[1:]
		event_id = string.split('#')[1].split('"')[0]
		
		link = 'http://moodle.iitb.ac.in/calendar/view.php?view=day&cal_d='+ day +'&cal_m='+month + '&cal_y=' + year + '#'+event_id
		
		url=opener.open(link)
		url=url.read()
		
		topic = re.compile('<td.*referer.*</td>')
		all_topics = topic.findall(str(url))
		
		for j in range(len(all_topics)):
			tmp_string = all_topics[j]
			
			assignment_number = tmp_string.split('href')[1].split('>')[1].split('<')[0]
			course_name = tmp_string.split('href')[2].split('>')[1].split('<')[0]
			submission_time = tmp_string.split('</span>')[0].split('>')[-1]
			
			assignment = assignment_number+'|'+course_name+'|'+submission_time+'|'+ day+'|'+month+'|'+year
			assignment_details.append(assignment)
	return assignment_details,invalid_login
			
