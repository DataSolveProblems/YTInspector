from .exceptions import AuthException
from .utility import create_service

class YouTubeAnalytics:
	API_NAME = 'youtubeAnalytics'
	API_VERSION = 'v2'
	SCOPES = ['https://www.googleapis.com/auth/yt-analytics-monetary.readonly']

	def __init__(self, client_file):
		self.client_file = client_file
		self.service = None

	def init_service(self):
		self.service = create_service(self.client_file, self.API_NAME, self.API_VERSION, self.SCOPES)

	def run_report(self, start_date, end_date, metrics, dimensions=None):
		"""
		Dimensions
		https://developers.google.com/youtube/analytics/dimensions

		Metrics
		https://developers.google.com/youtube/analytics/metrics
		"""
		response = self.service.reports().query(
			ids='channel==MINE',
			startDate=start_date,
			endDate=end_date,
			metrics=','.join(metrics),
			dimensions=dimensions
		).execute()
		columns = [col['name'] for col in response['columnHeaders']]
		rows = response['rows']
		return {'columns': columns, 'rows': rows}
		

