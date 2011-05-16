import os
import re
import sys
from urllib2 import HTTPError

from ubc.external.BeautifulSoup import BeautifulSoup
from ubc.external.padnums import pprint_table

from ubc import urls
from ubc.cwlsite import CwlSite
from ubc.utilities import cached

class Vista(CwlSite):
	"""Access the Blackboard Vista system and interact with courses on it.
	
	This class implements lazy-loading on all objects internally, so it will only load pages that
	are actually requested.
	
	"""

	# CWL config
	cwl_service_name = urls.VistaServiceName
	cwl_service_url = urls.VistaServiceUrl
	cwl_service_params = urls.VistaServiceParams

	def __init__(self):
		"""Log in and set up the course list."""
		# let the base class log in and do all that other nice stuff
		super(Vista, self).__init__()

	@cached
	def getCourses(self):
		"""Return the courses on the user's Vista homepage as a list of VistaCourse objects"""
		mainPage = self.getPage(urls.VistaCourseListUrl)
		soup = BeautifulSoup(mainPage)
		courseDiv = soup.find('div', {'id':'courses'})
		courseList = []
		for courseLi in courseDiv.findAll('li')[1:]: # first item is a header
			link = courseLi.next['href']
			# eg: https://www.vista.ubc.ca/webct/urw/lc3740786747121.tp3740786768121/
			# 	  startFrameSet.dowebct?forward=studentCourseView.dowebct&amp;lcid=3740786747121
			# need to pull the lc and tp parameters from this
			lc = re.findall('lc(\d*)[^i]', link)[0]	#TODO: is this [^i] necessary? why?
			tp = re.findall('tp(\d*)', link)[0]
			title = courseLi.next.next
			courseList.append(VistaCourse(self, lc, tp, title))
		return courseList
	
	# add a property for easy access
	courses = property(getCourses)

	def printCourses(self):
		pprint_table(sys.stdout, [('Id', 'Course')] + [(i, self.courses[i].title) for i in range(len(self.courses))])

class VistaCourse(object):
	"""Access a course on Vista."""

	def __init__(self, vista, lc, tp, title):
		self.vista = vista
		self.lc = lc
		self.tp = tp
		self.title = title

	def __repr__(self):
		return self.title
	
	
	# Functions to print various parameters
	
	def printGrades(self):
		"""Print a list of grades for a course."""
		pprint_table(sys.stdout, [('Item', 'Grade')] + self.getGrades())

	def printAnnouncements(self):
		"""Print a list of announcements for a course."""
		if self.announcements:
			pprint_table(sys.stdout, [('Id', 'Title')] + [(i, self.announcements[i]['title'])
				for i in range(len(self.announcements))])
		else:
			print "No announcements"

	def printAnnouncement(self, announcementId):
		"""Print an announcement for a course."""
		try:
			announcement = self.getAnnouncement(announcementId)
			print '''%s\n%s\n\n%s''' % (announcement['title'], announcement['date'], announcement['message'])
		except IndexError:
			print '''Invalid announcement id'''


	# Functions to retrieve and parse various pages into python objects

	def getCoursePage(self, url, *args):
		"""Retrieve a course page."""
		params = (self.lc, self.tp)		# course parameters, required for all course urls
		if args != ():
			params += tuple(args)
		return self.vista.getPage(url % params)

	@cached
	def getGrades(self):
		"""Return the grades for the course as a list of tuples of the form (title, grade)"""
		soup = BeautifulSoup(self.getCoursePage(urls.VistaGradesUrl))
		gradeList = []
		for gradeTr in soup.find('table', {'id':'datatable'}).findAll('tr')[1:]: # first row is a header
			# split the td's out
			tdList = gradeTr.findAll('td')
			
			# index 0 is the title with massive amount of random whitespace
			# eg: <td scope="row" nowrap="nowrap"><b>\n\nMidterm:\n</b></td>
			# need to go 2 levels in (td and br tags) then cut whitespace
			title = cleanText(tdList[0].next.next)
			
			# index 1 is the grade, inside only a td
			# eg: <td>\n\n8.00\n\n</td>
			grade = cleanText(tdList[1].next)

			gradeList.append((title, grade))
		return gradeList

	@cached
	def getAnnouncements(self):
		"""Return a list of announcements (dicts) for a course."""
		soup = BeautifulSoup(self.getCoursePage(urls.VistaAnnouncementsUrl))

		# Build the title list
		titleList = []
		for announcementTr in soup.find('table').findAll('tr'):
			# there is only one table on the page, so this should be ok since it doesn't have an id.
			# each tr has the form <td>[img]</td><td>[title]</td>
			dataTd = announcementTr.findAll('td')[1]
			title = cleanText(dataTd.next)
			titleList.append(title)

		# Build the id list
		idList = []
		for javascriptDiv in soup.findAll('div', {'class':'contextdiv'}):
			idList.append(re.findall('menu(\d*)', javascriptDiv['id'])[0])

		# Build the announcement list. "Announcements" are dictionaries with a bunch of keys, of
		# which 'title' and 'id' are set here. Note that this id is only used internally, the
		# announcementId referenced everywhere else is the chronological number of the id
		announcementList = [{'title':titleList[i], 'id':idList[i]} for i in range(len(titleList))]

		return announcementList

	@cached
	def getAnnouncement(self, announcementId):
		"""Return details for an announcement for a course."""
		#TODO: make this into a class, and make getAnnouncements return an array of objects of that
		#	   class
		
		# retrieve the announcement (need to get the date and the message)
		# the data that we are looking for is in a form with format:
		# <form><div></div><h2>[title]</h2><span>[date]</span><div>[message]</div>
		soup = BeautifulSoup(getCoursePage(urls.getAnnouncementUrl, announcements[announcementId]['id']))
		announcementForm = soup.find('form')
		announcement['date'] = cleanText(announcementForm.find('span').next)

		# BeautifulSoup can probably do something really nice with HTML tags, but I'm just mashing
		# it for now.
		messageTags = announcementForm.findAll('div')[1].contents
		announcement['message'] = parseHtmlTags(cleanText(''.join([str(i) for i in messageTags])))
		announcement['retrieved'] = True

		return announcement
		
	def getBaseFolder(self):
		# Passing in ID 0 returns the base folder. Vista doesn't actually do it this way, but it
		# works.
		return makeVistaObject(self, self.title, "ORGANIZER_PAGE_TYPE", 0)
	
	
	# Properties to make code nicer
	
	grades = property(getGrades)
	announcements = property(getAnnouncements)
	baseFolder = property(getBaseFolder)
		

class VistaObject(object):
	"""An object in the Course Content section of Vista"""
	
	def __init__(self, course, title, fileType, fileId):
		self.course = course
		self.title = title
		self.fileType = fileType
		self.fileId = fileId
		
	def __repr__(self):
		return self.title
	
	def getType(self):
		return self.fileType

	def isFolder(self):
		return isinstance(self, VistaFolder)
		
	def download(self):
		pass


class VistaFolder(VistaObject):
	"""A folder in the Course Content section of Vista"""
	
	def __init__(self, course, title, fileId):
		super(VistaFolder, self).__init__(course, title, "Folder", fileId)
	
	@cached
	def getItems(self):
		soup = BeautifulSoup(self.course.getCoursePage(urls.VistaFolderUrl, self.fileId))
		
		# Find all relevant divs. There is one for the image and one for the title for each file.
		# The title divs have class "orgtext". In each of these is a link with a call to submitLoad
		# in the href and the desired title as the link message. We can get all required information
		# from the submitLoad call
		itemList = []
		for javascriptDiv in soup.findAll('div', {'class':'orgtext'}):
			link = javascriptDiv.find('a')
			submitLoadCall = link['href']
			# link eg: u"javascript:submitLoad('3764064849121','ORGANIZER_PAGE_TYPE', false, false)"
			fileId, fileType = re.findall("'(\d*)','([A-Z_]*)", link['href'])[0]
			title = link.text
			itemList.append(makeVistaObject(self.course, title, fileType, int(fileId)))
		
		return itemList

	def download(self):
		# Download everything in the folder. This works recursively to grab subfolders!
		# This will overwrite stuff if it already is there
		try:
			os.mkdir(self.title)
		except OSError:
			pass
		
		os.chdir(self.title)
		
		for item in self.items:
			item.download()
			
		os.chdir('..')
		
		
	# Properties to make code nicer
	
	items = property(getItems)
		

class VistaFile(VistaObject):
	"""A file in the Course Content section of Vista"""
	
	def __init__(self, course, title, fileId):
		super(VistaFile, self).__init__(course, title, "File", fileId)
	
	def download(self):
		# Download the file. This creates a file in the pwd with the file's title. I think that all
		# files are pdfs, so I'm just smacking on a .pdf extension. This is probably wrong...
		
		# We have to traverse some random useless page to actually get to the file.
		try:
			firstPage = self.course.getCoursePage(urls.VistaFileUrl, self.fileId)
		except HTTPError:
			# Occasionally, teachers will break this and put links to other pages here somehow.
			# Then everything breaks. This could potentially be refined further, but there doesn't
			# seem to be much point.
			return

		resourceId = re.findall("contentID=(\d*)", firstPage)[0]
		
		outFile = open(self.title + ".pdf", 'w')
		print >>outFile, self.course.getCoursePage(urls.VistaResourceUrl, resourceId)
		outFile.close()


@cached
def makeVistaObject(course, title, fileType, fileId):
	if fileType == "PAGE_TYPE":
		return VistaFile(course, title, fileId)
	elif fileType == "ORGANIZER_PAGE_TYPE":
		return VistaFolder(course, title, fileId)
	#elif fileType == "URL_TYPE":		#TODO: implement
	#	return VistaURL(course, title, fileId)
	else:
		return VistaObject(course, title, fileType, fileId)
		
def cleanText(text):
	""" Hax to fix Vista's mess of adding newlines, &nbsp;'s and junk all over the place """
	return ' '.join(text.strip().replace('&nbsp;', ' ').split())

def parseHtmlTags(text):
	""" Parses a few common html tags and makes stuff nice looking """
	text = text.replace('<br />', '\n')
	text = text.replace('<b>', '')	#TODO: can we do something better for bold?
	text = text.replace('</b>', '')
	return text


