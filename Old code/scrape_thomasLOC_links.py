from bs4 import BeautifulSoup
import requests 
import re 
import sys
sys.setrecursionlimit(4800)


def collect_suitable_links_for_day(link): 
	''' 
	Given a link to a day when there were senate proceedings, returns all links that should 
	be followed and scraped 
	''' 
	links = {}
	response = requests.get(link)
	soup = BeautifulSoup(response.content, "html.parser")
	main_table = soup.findAll("table", {"class":"item_table"})

	if len(main_table)==0: # this happens when no senate activity on date or invalid date
		#print "NOT SUITABLE:"
		#print link 
		return []

	tds = main_table[0].findAll("td")
	for td in tds: 
		a = td.findAll("a")
		if should_follow_link(a[0].text): 
			links[a[0].text] = {}
			links[a[0].text]['link'] = a[0]['href']
	return links 


def should_follow_link(text): 
	''' 
	Takes in text description of a link to some senate proceedings document. Returns true or 
	false based on whether it is a link that you should follow. Would not want to follow 
	procedural links, recognition stuff, etc. 
	'''
	text = text.lower() 

	things_not_to_follow = ["conclusion of", "extension of", "recognizing", "measures", "measure", "recess", "notices of", "quorum",  
		"reauthorizing", "order of", "appointment", "memorial", "honoring", "senate concurrent resolution", "recognition", 
		"text of", "welcoming", "prayer", "recognition of", "reservation of", "morning business", "remembering ", "committees", 
		"introduction of", "submission of", "additional cosponsors", "additional sponsors", "submitted", "senate resolution", "notice of", "authority for", 
		"reports of", "report of", "nomination", "orders for", "adjournment", "nominations", "schedule", "executive session", 
		"legislative session", "motion to", "tribute to", "rules of the", "reports on", "report on", "executive and other communications", 
		"executive messages", "messages from", "pledge of", "privileges of", "message from", "joint meeting", "res.", "unanimous", "award winners", 
		"authorization to", "authorization of",  "appoint", "executive calendar", "congratulat", "celebrating", "as modified", "amendment no.",
		"enrolled bill presented", "upcoming business", "expression to", "anniversary of", "issuance of", "authorization", "exhibition of", "commemorating",
		 "thanking", "condemning the", "committee", "resilience of", "h.r.", "the journal", "permission to" , "general leave", "leave of absence",
		 "senate", "bills and resolutions", "authority statement", "congressional earmarks", "house of representatives", "morning-hour debate", "announcement by", 
		  "removal of", "memory", "adjournment", "executive communications", "deletion of",  "memorial",  "communication from", "designat", "amendments", 
		  "hour of", "special orders", "welcome home", ]
	if re.search("s[0-9]", text) is not None: # For links like S9192 
		return False 
	if re.search("h[0-9]", text) is not None: # For links like S9192 
		return False 
	if (("national" in text) or ("history" in text)) and (("day" in text) or ("week" in text) or ("month" in text)): 
		return False 
	if text == "senate" or text == "program" or text == "confirmations" or text == "confirmation": 
		return False
	for thing in things_not_to_follow: 
		if thing in text: 
			return False
	return True


def scrape_all_links(start_year, start_month, end_year, end_month, is_senate):
	''' 
	Start year + month will be first month of links scraped. End year + month will be last 
	month of links scraped. Returns all suitable links in a dictionary {date: links}. 
	''' 
	if is_senate:
		chamber = "/senate-section"
	else: 
		chamber = "/house-section"
	rv = {} 
	for year in range(start_year, end_year+1): 
		for month in range(1,13):
			if year == start_year and month < start_month: 
				continue
			if year == end_year and month > end_month: 
				continue
			print "Scraping " + str(month) + "/" + str(year) + "..."

			for day in range(1, 32): 
				date = str(year) + "/" + str(month) + "/" + str(day) 
				#print "Scraping " + date
				link = "https://www.congress.gov/congressional-record/" + date + chamber
				l = collect_suitable_links_for_day(link)
				if len(l) != 0 and l is not None: 
					rv[date] = l 
	return rv 









