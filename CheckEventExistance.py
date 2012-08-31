
def CheckEventExistance(query,calendar_client,title,content):
	
	feed = calendar_client.GetCalendarEventFeed(q=query)
	existance_state = 0
	for z in feed.entry:
		if z.title.text == title and z.content.text == content:
			existance_state = 1
			break
	
	return existance_state
	
