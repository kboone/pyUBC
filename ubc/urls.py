""" This file contains a list of URLs used by the various sites. All URLs should be here to be able
to update stuff easily when it changes.
"""

# CWL
CwlBaseUrl 				= 	"https://www.auth.cwl.ubc.ca"
CwlLoginUrl 			= 	CwlBaseUrl + "/auth/login"

# SSC
SscBaseUrl				=	"https://ssc.adm.ubc.ca/sscportal/servlets"
SscServiceName			=	"ytestssc"
SscServiceParams		=	"null"
SscServiceUrl			=	SscBaseUrl + "/SSCMain.jsp"
SscGradesUrl			=	SscBaseUrl + "/SRVAcademicRecord"

# Vista
VistaBaseUrl			=	"https://www.vista.ubc.ca/webct/urw"
VistaServiceName		=	"webct_vista_psa"
VistaServiceParams		=	"null"
VistaServiceUrl			=	"null"
VistaCourseListUrl		=	VistaBaseUrl + "/lc5116011.tp0/populateMyWebCT.dowebct"
VistaBaseCourseUrl		=	VistaBaseUrl + "/lc%s.tp%s"		# lc and tp are course related variables
VistaGradesUrl			=	VistaBaseCourseUrl + "/membergradebookMyGradesView.dowebct"
VistaAnnouncementsUrl	=	VistaBaseCourseUrl + "/sstuViewAllAnnouncements.dowebct"
VistaAnnouncementUrl	=	VistaAnnouncementsUrl + "?action=view&annid=%s"
VistaFolderUrl			=	VistaBaseCourseUrl + "/studentCourseView.dowebct?displayinfo=%s"
VistaFileUrl			=	VistaBaseCourseUrl + "/displayContentPage.dowebct?pageID=%s"
VistaResourceUrl		=	VistaBaseCourseUrl + "/RelativeResourceManager?contentID=%s"

