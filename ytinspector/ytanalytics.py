from .exceptions import YTAnalyticsException
from .google_apis import create_service

CoreDimensions = [
	'ageGroup',
	'channel',
	'country',
	'day',
	'gender',
	'month',
	'sharingService',
	'uploaderType',
	'video'
]

SubDimensions = [
	'adType',
	'audienceType',
	'claimedStatus',
	'continent',
	'deviceType',
	'elapsedVideoTimeRatio',
	'group',
	'insightPlaybackLocationType',
	'insightPlaybackLocationDetail',
	'insightTrafficSourceType',
	'insightTrafficSourceDetail',
	'isCurated',
	'liveOrOnDemand',
	'operatingSystem',
	'playlist',
	'province',
	'subscribedStatus',
	'subContinent',
	'youtubeProduct'
]

CoreMetrics = [
	'annotationClickThroughRate',
	'annotationCloseRate',
	'averageViewDuration',
	'comments',
	'dislikes',
	'estimatedMinutesWatched',
	'estimatedRevenue',
	'likes',
	'shares',
	'subscribersGained',
	'subscribersLost',
	'viewerPercentage',
	'views'
]

SubMetrics = [
	'adImpressions',
	'annotationClosableImpressions',
	'annotationCloses',
	'annotationClickableImpressions',
	'annotationClicks',
	'annotationImpressions',
	'audienceWatchRatio',
	'averageTimeInPlaylist',
	'averageViewPercentage',
	'cardImpressions',
	'cardClicks',
	'cardClickRate',
	'cardTeaserImpressions',
	'cardTeaserClicks',
	'cardTeaserClickRate',
	'cpm',
	'estimatedAdRevenue',
	'estimatedRedMinutesWatched',
	'estimatedRedPartnerRevenue ',
	'grossRevenue',
	'monetizedPlaybacks',
	'playbackBasedCpm',
	'playlistStarts',
	'redViews',
	'relativeRetentionPerformance',
	'viewsPerPlaylistStart',
	'videosAddedToPlaylists',
	'videosRemovedFromPlaylists'
]


class YTAnalytics:
	SCOPES = ['https://www.googleapis.com/auth/youtube',
              'https://www.googleapis.com/auth/yt-analytics-monetary.readonly',
              'https://www.googleapis.com/auth/youtubepartner']
	API_NAME = 'youtubeAnalytics'
	API_VERSION = 'v2'

	def __init__(self, client_secret_file):
		self.client_secret_file = client_secret_file
		self.service = None
	   
	def initService(self, prefix=None):
		try:
			self.service = create_service(self.client_secret_file, self.API_NAME, self.API_VERSION, self.SCOPES, prefix=prefix)
		except Exception as e:
			raise YTAnalyticsException(e)

	def query(self, start_date, end_date, metric_list, 
			  dimension_list=None, filters=None, max_results=1000, start_index=1, sort_by=None):
		"""
			Query the YouTube Analytics API.
			Args:
				start_date str: The start date for the query in the format YYYY-MM-DD.
				end_date str: The end date for the query in the format YYYY-MM-DD.
				metric_list list: YouTube Analytics metrics.
				dimension_list list (optional): YouTube Analytics dimensions.
				filters str (optional): A list of filters that should be applied when retrieving YouTube Analytics data
									(e.g. video==pd1FJh59zxQ,Zhawgd0REhA;country==IT).
				row_limit int (optional): The maximum number of rows to return (max is 10000).
				start_index int (optional): The 1-based index of the first entity to retrieve. (The default value is 1.) 
										Use this parameter as a pagination mechanism along with the max-results parameter..
				sort_by str (optional): A list of fields to sort by. (e.g. -views)
			Returns:
				Tuple(columns, rows)
		"""
		if not self.service:
			raise YTAnalyticsException('Service is not initialized.')

		if not isinstance(metric_list, list):
			raise YTAnalyticsException('metric_list must be a list')
		else:
			metrics = ','.join(metric_list)

		if dimension_list is not None:
			if not isinstance(dimension_list, list):
				raise YTAnalyticsException('dimension_list must be a list')
			else:    
				dimensions = ','.join(dimension_list)
		else:
			dimensions = None
		
		try:
			response = self.service.reports().query(
				ids='channel==MINE',
				startDate=start_date,
				endDate=end_date,
				metrics=metrics,
				dimensions=dimensions,
				filters=filters,
				maxResults=max_results,
				startIndex=start_index,
				sort=sort_by
			).execute()
			columns = [column['name'] for column in response['columnHeaders']]
			rows = response['rows']
			return columns, rows
		except Exception as e:
			raise YTAnalyticsException(e)

	def channelSummary(self, start_date, end_date, is_yt_partner=False):
		"""
		Total view, comment, likes, dislikes, estimated watch time, average view duration.
		Args:
			start_date str: The start date for the query in the format YYYY-MM-DD.
			end_date str: The end date for the query in the format YYYY-MM-DD.
		Returns:
			Tuple(columns, rows)		
		"""
		if is_yt_partner:
			response = self.service.reports().query(
				ids='channel==MINE',
				startDate=start_date,
				endDate=end_date,
				metrics='views,comments,likes,dislikes,estimatedMinutesWatched,subscribersGained,subscribersLost,estimatedRevenue'
			).execute()
		else:
			response = self.service.reports().query(
				ids='channel==MINE',
				startDate=start_date,
				endDate=end_date,
				metrics='views,comments,likes,dislikes,estimatedMinutesWatched,subscribersGained,subscribersLost'
			).execute()			
		columns = [column['name'] for column in response['columnHeaders']]
		rows = response['rows']
		return columns, rows

	def summaryByCountry(self, start_date, end_date, country_code='us', is_yt_partner=False):
		if is_yt_partner:
			response = self.service.reports().query(
							ids='channel==MINE',
							startDate=start_date,
							endDate=end_date,
							metrics='views,likes,dislikes,estimatedMinutesWatched,estimatedRevenue',
							filters='country=={0}'.format(country_code)
						).execute()
		else:
			response = self.service.reports().query(
				ids='channel==MINE',
				startDate=start_date,
				endDate=end_date,
				metrics='views,likes,dislikes,estimatedMinutesWatched,subscribersGained,subscribersLost',
				filters='country=={0}'.format(country_code)
			).execute()
		columns = [column['name'] for column in response['columnHeaders']]
		rows = response['rows']
		return columns, rows

	def top200Videos(self, start_date, end_date, sortby_field='views', is_yt_partner=False):
		"""
			Get the top 200 videos by views.
			Args:
				start_date str: The start date for the query in the format YYYY-MM-DD.
				end_date str: The end date for the query in the format YYYY-MM-DD.
				sort_by_category str: The category to sort by. (e.g. -views)
			Returns:
				Tuple(columns, rows)
		"""
		if is_yt_partner:
			response = self.service.reports().query(
				ids='channel==MINE',
				startDate=start_date,
				endDate=end_date,
				metrics='views,comments,likes,dislikes,estimatedMinutesWatched,subscribersGained,subscribersLost',
				dimensions='video',
				sort='-{0}'.format(sortby_field),
				maxResults=200
			).execute()
			columns = [column['name'] for column in response['columnHeaders']]
			rows = response['rows']
			return columns, rows		
		else:
			response = self.service.reports().query(
				ids='channel==MINE',
				startDate=start_date,
				endDate=end_date,
				metrics='views,comments,likes,dislikes,estimatedMinutesWatched,subscribersGained,subscribersLost,estimatedRevenue',
				dimensions='video',
				sort='-{0}'.format(sortby_field),
				maxResults=200
			).execute()
			columns = [column['name'] for column in response['columnHeaders']]
			rows = response['rows']
			return columns, rows

	def playlistSummary(self, start_date, end_date, playlist_id=None):
		if playlist_id is None:
			response = self.service.reports().query(
							ids='channel==MINE',
							metrics='playlistStarts,estimatedMinutesWatched,views,viewsPerPlaylistStart',
							startDate=start_date,
							endDate=end_date,
							filters="isCurated==1",
						).execute()
			columns = [column['name'] for column in response['columnHeaders']]
			rows = response['rows']
			return columns, rows				
		response = self.service.reports().query(
						ids='channel==MINE',
						metrics='playlistStarts,estimatedMinutesWatched,views,viewsPerPlaylistStart',
						startDate=start_date,
						endDate=end_date,
						filters="isCurated==1",
						playlist='playlist=={0}'.format(playlist_id)
					).execute()
		columns = [column['name'] for column in response['columnHeaders']]
		rows = response['rows']
		return columns, rows

	def top200Playlists(self, start_date, end_date, sortby_field='view'):
		response = self.service.reports().query(
						ids='channel==MINE',
						dimensions='playlist',
						metrics='playlistStarts,estimatedMinutesWatched,views,viewsPerPlaylistStart',
						startDate=start_date,
						endDate=end_date,
						filters='isCurated==1',
						maxResults=200,
						sort='-{0}'.format(sortby_field)
					).execute()		
		columns = [column['name'] for column in response['columnHeaders']]
		rows = response['rows']
		return columns, rows