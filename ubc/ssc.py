from ubc.cwlsite import CwlSite
from ubc import urls

class Ssc(CwlSite):
	"""Access the Student Service Centre (SSC)
	
	The SSC is actually made up of a bunch of different CWL sites that all work separately. This
	class only covers the actual SSC, and not sub sites like housing, voting or registration.
	"""

	# CWL config
	cwl_service_name = urls.SscServiceName
	cwl_service_url = urls.SscServiceUrl
	cwl_service_params = urls.SscServiceParams

	def __init__(self):
		# let the base class log in and do all that other nice stuff
		super(Ssc, self).__init__()

	def getGrades(self):
		#TODO: parse output	
		return self.getPage(urls.SscGradesUrl)
