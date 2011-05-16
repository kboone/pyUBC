from cookielib import CookieJar
from getpass import getpass
from urllib import urlencode
from urllib2 import build_opener
from urllib2 import HTTPCookieProcessor
from urllib2 import HTTPHandler
from urllib2 import HTTPRedirectHandler
from urllib2 import HTTPSHandler

from ubc import urls
from ubc.config import debugPrintRequests

class CwlSite(object):
	"""Virtual base class to handle actual communication with the UBC servers.
	
	This handles logging in through the CWL system, cookies and basic page requests. It will ask for
	a username and password if one isn't specified in the config file. This is a virtual class, and
	the cwl_service_name, cwl_service_url and cwl_service_params must be specified for any
	non-virtual subclass. These are the parameters used when loading the actual CWL login page.
	"""
	def __init__(self):
		"""Set up the HTTPS, HTTP, redirect and cookie handlers and log in to the site"""
		# the username and password can be specified in the config file, or prompted for		
		try:
			from ubc.utilities import username
		except ImportError:
			username = raw_input("Username: ")
		
		try:
			from ubc.utilities import password
		except ImportError:
			password = getpass()

		self.cookieJar = CookieJar()		
		self.opener = build_opener(
			HTTPRedirectHandler(),
			HTTPHandler(debuglevel=0),	
			HTTPSHandler(debuglevel=0),
			HTTPCookieProcessor(self.cookieJar)
		)
		self.opener.addheaders = [
			('User-agent', ('Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.9.2.13)'
				+ 'Gecko/20101203 Firefox/3.6.13')),
			('Referer', (urls.CwlLoginUrl)),
			('Accept', ('text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')),
			('Accept-Language', ('Accept-Language=en-us,en;q=0.5')),
			('Accept-Charset', ('ISO-8859-1,utf-8;q=0.7,*;q=0.7')),
			('Accept-Encoding', ('gzip,deflate')),
		]

		print "Logging in to CWL..."
		self.login(username, password)
		print "Log in successful."

	def login(self, username, password):
		""" Log in to a service using through CWL """
		loginData = {
			'loginName' : username,
			'password' : password,
			'serviceName' : self.cwl_service_name,
			'serviceURL' : self.cwl_service_url,
			'serviceParams' : self.cwl_service_params,
			'action' : '''Continue >''',
		}
		self.getPage(urls.CwlLoginUrl, loginData)

	def getPage(self, page, postParams=None, *args, **kwargs):
		"""	Get a page, with post data passed along.
		POST paramaters can be either in a dict or as kwargs.
		"""
		if debugPrintRequests:
			print "GET:", page
			
		if postParams:
			postData = urlencode(postParams)
		elif kwargs:
			postData = urlencode(kwargs)
		else:
			postData = None

		response = self.opener.open(page, postData)
		return ''.join(response.readlines())
