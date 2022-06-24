from .exceptions import YouTubeException, NoVideosReturned, NoCommentsReturned, SearchResultReturnsNone
from .google_apis import create_service, convert_to_RFC_datetime
from ytinspector.utility import (ChannelRelatedComment, VideoComment, VideoReply, SearchResultsChannel, SearchResultsVideo, SearchResultsPlaylist)
from ytinspector.utility import (convert_duration)

class YouTube:
	SCOPES = ['https://www.googleapis.com/auth/youtube', 
			  'https://www.googleapis.com/auth/youtube.force-ssl',
			  'https://www.googleapis.com/auth/youtubepartner']
	API_NAME = 'youtube'
	API_VERSION = 'v3'

	def __init__(self, client_secret_file):
		self.client_secret_file = client_secret_file
		self.service = None
	   
	def initService(self, prefix:str=None):
		try:
			self.service = create_service(self.client_secret_file, self.API_NAME, self.API_VERSION, self.SCOPES, prefix=prefix)
		except Exception as e:
			raise YouTubeException(e)

	def retrieveChannelVideos(self, channel_id, id_type='by id'):
		if id_type == 'by id':
			response = self.service.channels().list(part='contentDetails,brandingSettings', id=channel_id).execute()
		elif id_type == 'by username':
			response = self.service.channels().list(part='contentDetails,brandingSettings', forUsername=channel_id).execute()
		
		if response['pageInfo']['totalResults'] == 0:
			raise NoVideosReturned('No video returned. Perhaps channel id is incorrect?')

		playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
		part_string = 'contentDetails'
		try:
			response = self.service.playlistItems().list(
					part=part_string,
					playlistId=playlist_id,
					maxResults=50
				).execute()
			playlistItems = response['items']
			nextPageToken = response.get('nextPageToken')

			while nextPageToken:
				response = self.service.playlistItems().list(
					part=part_string,
					playlistId=playlist_id,
					maxResults=50,
					pageToken=nextPageToken
				).execute()
				playlistItems.extend(response['items'])
				nextPageToken = response.get('nextPageToken')
				print('Token {0}'.format(nextPageToken))

			videos = [v['contentDetails'] for v in playlistItems]
			videos_info = []

			for batch_num in range(0, len(videos), 50):
				video_batch = videos[batch_num: batch_num + 50]				
				# maxium 50 videos per request
				response_videos = self.service.videos().list(
					id=','.join(list(map(lambda x:x['videoId'], video_batch))),
					part='snippet,contentDetails,statistics',
					maxResults=50
				).execute()
				videos_info.extend(response_videos['items'])
			return videos_info
		except Exception as e:
			raise YouTubeException(e)

	def retrieveVideoComments(self, video_id, order_by='time', output_type='plainText', search_keyword=None, include_replies=False):
		"""
		Retrieve video comments. Limiting to 3,000 comments cap to avoid exceeding daily usage quota.
		:param video_id
		:param ordder_by: {time; relevance}
		:param output_format: {plainText; html}
		:param include_replies: {True; False}
		"""
		def getCommentReply(service, comment_thread_id, output_format='plainText'):
			comment_replies = [] 
			comment_replies_items = []
			response_comment_repleis = service.comments().list(
				part='snippet',
				parentId=comment_thread_id,
				maxResults=100,
				textFormat=output_format
			).execute()

			comment_replies_items.extend(response_comment_repleis.get('items'))
			nextPageToken = response_comment_repleis.get('nextPageToken')

			while nextPageToken:
				response_comment_repleis = service.comments().list(
					part='snippet',
					parentId=comment_thread_id,
					maxResults=100,
					textFormat=output_format,
					pageToken=nextPageToken
				).execute()

				comment_replies_items.extend(response_comment_repleis.get('items'))
				nextPageToken = response_comment_repleis.get('nextPageToken')     

			for comment_replies_item in comment_replies_items:
				comment_replies.append(VideoReply(
					comment_replies_item['id'],
					comment_thread_id,
					comment_replies_item['snippet']['textDisplay'],
					comment_replies_item['snippet']['authorDisplayName'],
					comment_replies_item['snippet']['authorChannelUrl'],
					comment_replies_item['snippet']['likeCount'],
					comment_replies_item['snippet']['publishedAt'],
					comment_replies_item['snippet']['updatedAt']
				))
			return comment_replies

		comment_thread_count = 0
		comment_threads = []
		comment_threads_items = []
		response_commentThreads = self.service.commentThreads().list(
			part='snippet',
			videoId=video_id,
			maxResults=100,
			order=order_by,
			textFormat=output_type,
			searchTerms=search_keyword
		).execute()

		if response_commentThreads['pageInfo']['totalResults'] == 0:
			raise NoCommentsReturned("Video has no comment")

		comment_threads_items.extend(response_commentThreads['items'])
		nextPageToken = response_commentThreads.get('nextPageToken')
		comment_thread_count += len(response_commentThreads['items'])

		while nextPageToken:
			if 3000 >= comment_thread_count:
				response_commentThreads = self.service.commentThreads().list(
					part='snippet',
					videoId=video_id,
					maxResults=100,
					order=order_by,                      
					textFormat=output_type,
					pageToken=nextPageToken,
					searchTerms=search_keyword
				).execute()   
				comment_threads_items.extend(response_commentThreads['items'])
				nextPageToken = response_commentThreads.get('nextPageToken')
				print('Token {0}'.format(nextPageToken))
				comment_thread_count += len(response_commentThreads['items'])
			else:
				nextPageToken = None

		if include_replies:
			for comment_threads_item in comment_threads_items:
				comment_threads.append(VideoComment(
					comment_threads_item['snippet']['videoId'],
					comment_threads_item['snippet']['topLevelComment']['id'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['textDisplay'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['likeCount'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['publishedAt'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['updatedAt'], 
					comment_threads_item['snippet']['totalReplyCount'],
					getCommentReply(self.service, comment_threads_item['snippet']['topLevelComment']['id'], output_type)
				))
		else:
			for comment_threads_item in comment_threads_items:
				comment_threads.append(VideoComment(
					comment_threads_item['snippet']['videoId'],
					comment_threads_item['snippet']['topLevelComment']['id'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['textDisplay'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['likeCount'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['publishedAt'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['updatedAt'], 
					comment_threads_item['snippet']['totalReplyCount'],
					[]
				))			
		return comment_threads

	def retrieveChannelRelatedComments(self, channel_id, order_by='time', output_type='plainText', search_keyword=None, include_replies=False):
		"""
		Retrieve video and channel related comments. Limiting to 500 comments cap to avoid exceeding daily usage quota.
		:param channel_id
		:param ordder_by: {time; relevance}
		:param output_format: {plainText; html}
		:param include_replies: {True; False}
		"""
		def getCommentReply(service, comment_thread_id, output_format='plainText'):
			comment_replies = [] 
			comment_replies_items = []
			response_comment_repleis = service.comments().list(
				part='snippet',
				parentId=comment_thread_id,
				maxResults=100,
				textFormat=output_format
			).execute()

			comment_replies_items.extend(response_comment_repleis.get('items'))
			nextPageToken = response_comment_repleis.get('nextPageToken')

			while nextPageToken:
				response_comment_repleis = service.comments().list(
					part='snippet',
					parentId=comment_thread_id,
					maxResults=100,
					textFormat=output_format,
					pageToken=nextPageToken
				).execute()

				comment_replies_items.extend(response_comment_repleis.get('items'))
				nextPageToken = response_comment_repleis.get('nextPageToken')     

			for comment_replies_item in comment_replies_items:
				comment_replies.append(VideoReply(
					comment_replies_item['id'],
					comment_thread_id,
					comment_replies_item['snippet']['textDisplay'],
					comment_replies_item['snippet']['authorDisplayName'],
					comment_replies_item['snippet']['authorChannelUrl'],
					comment_replies_item['snippet']['likeCount'],
					comment_replies_item['snippet']['publishedAt'],
					comment_replies_item['snippet']['updatedAt']
				))
			return comment_replies

		comment_thread_count = 0
		comment_threads = []
		comment_threads_items = []
		response_commentThreads = self.service.commentThreads().list(
			part='snippet',
			allThreadsRelatedToChannelId=channel_id,
			maxResults=100,
			order=order_by,
			textFormat=output_type,
			searchTerms=search_keyword
		).execute()

		if response_commentThreads['pageInfo']['totalResults'] == 0:
			raise NoCommentsReturned("Video has no comment")

		comment_threads_items.extend(response_commentThreads['items'])
		nextPageToken = response_commentThreads.get('nextPageToken')
		comment_thread_count += len(response_commentThreads['items'])

		while nextPageToken:
			if 500 >= comment_thread_count:
				response_commentThreads = self.service.commentThreads().list(
					part='snippet',
					allThreadsRelatedToChannelId=channel_id,
					maxResults=100,
					order=order_by,                      
					textFormat=output_type,
					pageToken=nextPageToken,
					searchTerms=search_keyword
				).execute()   
				comment_threads_items.extend(response_commentThreads['items'])
				nextPageToken = response_commentThreads.get('nextPageToken')
				print('Token {0}'.format(nextPageToken))
				comment_thread_count += len(response_commentThreads['items'])
			else:
				nextPageToken = None

		if include_replies:
			for comment_threads_item in comment_threads_items:
				comment_threads.append(ChannelRelatedComment(
					comment_threads_item['snippet']['channelId'],
					comment_threads_item['snippet']['videoId'],
					comment_threads_item['snippet']['topLevelComment']['id'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['textDisplay'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['likeCount'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['publishedAt'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['updatedAt'], 
					comment_threads_item['snippet']['totalReplyCount'],
					getCommentReply(self.service, comment_threads_item['snippet']['topLevelComment']['id'], output_type)
				))
		else:
			for comment_threads_item in comment_threads_items:
				comment_threads.append(ChannelRelatedComment(
					comment_threads_item['snippet']['channelId'],
					comment_threads_item['snippet']['videoId'],					
					comment_threads_item['snippet']['topLevelComment']['id'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['textDisplay'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['likeCount'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['publishedAt'],
					comment_threads_item['snippet']['topLevelComment']['snippet']['updatedAt'], 
					comment_threads_item['snippet']['totalReplyCount'],
					[]
				))			
		return comment_threads		

	def retrieveVideoCategoriesList(self, region_code='us'):
		"""
		Retrieve a list of video categories.
		:param region_code: The region code for the categories.
		:return: A list of video categories.
		"""
		try:
			video_categories = {}
			response = self.service.videoCategories().list(
				part='snippet',
				regionCode=region_code
			).execute()

			for item in response['items']:
				video_categories[item['id']] = item['snippet']['title']
			return video_categories
		except TypeError as e:
			raise Exception('Invalid region code')
		except Exception as e:
			raise Exception('Error retrieving video categories')

	def searchVideos(self, search_keyword, region_code='us', video_duration='any', video_definition='any', video_dimension='any', published_before=None, 
					  published_after=None, order_by='relevance', channel_type='any', safe_search='none', category_id=None, location=None, location_radius=None, result_limit=50):
		"""
		Search Channels (There is a limit of up to 500 items can be returned)
		:param search_keyword: Query term.
		:param region_code: The region code for the search.
		:param video_duration: The duration of the video (any, short, medium, long).
		:param video_definition: The definition of the video (any, standard, high).
		:param video_dimension: The dimension of the video (any, 2d, 3d).
		:param published_before: The oldest YouTube release date that a returned video could have.
			(The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z)).
		:param published_after: The newest YouTube release date that a returned video could have.
			(The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z)).
		:param order_by: Order results by (date, rating, relevance, title, videoCount, viewCount).
		:param channel_type: Filter by channel type (any, show).
		:param safe_search: Search safety level (none, moderate, strict).
		:param category_id: Filter by category ID.
		:param location: The parameter value is a string that specifies latitude/longitude coordinates e.g. (37.42307,-122.08427).
			If location is set, location_radius must be provided.
		:param location_radius: TThe locationRadius parameter, in conjunction with the location parameter, defines a circular geographic area.
			(Valid parameter values include 1500m, 5km, 10000ft, and 0.75mi. The API does not support locationRadius parameter values larger than 1000 kilometers.)
		:param result_limit: Up to 500 results can be returned.
		
		ps: A call to this method has a quota cost of 100 units.
		"""
		videos = []
		videos_items = []
		item_count = 0

		response = self.service.search().list(
			part='snippet',
			q=search_keyword,
			channelType=channel_type,
			publishedBefore=published_before,
			publishedAfter=published_after,
			location=location,
			locationRadius=location_radius, 
			regionCode=region_code,
			videoCategoryId=category_id,
			type='video',
			order=order_by,
			safeSearch=safe_search,
			videoDuration=video_duration,
			videoDefinition=video_definition,
			videoDimension=video_dimension,
			maxResults=50
		).execute()

		if response['pageInfo']['totalResults'] == 0:			
			raise SearchResultReturnsNone("No videos found for the search keyword: " + search_keyword)

		# total_results = response['pageInfo']['totalResults']
		videos_items.extend(response['items'])
		nextPageToken = response.get('nextPageToken')
		item_count += len(response['items'])
		print('Token {0}'.format(nextPageToken))

		while nextPageToken:
			if result_limit > item_count:
				response = self.service.search().list(
					part='snippet',
					q=search_keyword,
					channelType=channel_type,
					publishedBefore=published_before,
					publishedAfter=published_after,
					location=location,
					locationRadius=location_radius, 
					regionCode=region_code,
					videoCategoryId=category_id,
					type='video',
					order=order_by,
					safeSearch=safe_search,
					videoDuration=video_duration,
					videoDefinition=video_definition,
					videoDimension=video_dimension,
					maxResults=50,
					pageToken=nextPageToken
				).execute()			
				videos_items.extend(response['items'])
				nextPageToken = response.get('nextPageToken')
				item_count += len(response['items'])
				print('Token {0}'.format(nextPageToken))
			else:
				nextPageToken = None
		
		for videos_item in videos_items:
			videos.append(SearchResultsVideo(					
				videos_item['id']['videoId'],
				videos_item['snippet']['title'],
				videos_item['snippet']['channelId'],
				videos_item['snippet']['channelTitle'],
				videos_item['snippet']['description'],
				videos_item['snippet']['publishedAt'],
				region_code,
				videos_item['snippet']['thumbnails']['default']['url'],
				'https://www.youtube.com/watch?v={0}'.format(videos_item['id']['videoId'])
			))
		return videos				  

	def searchChannels(self, search_keyword, region_code='us', published_before=None, published_after=None, order_by='relevance', channel_type=None, result_limit=50):
		"""
		Search Channels (There is a limit of up to 500 items can be returned)
		:param search_keyword: Query term.
		:param region_code: The region code for the search.
		:param published_before: Filter by date and time published before this time 
			(The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z)).
		:param published_after: Filter by date and time published after this time.
			(The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z)).
		:param order_by: Order results by (date, rating, relevance, title, videoCount, viewCount).
		:param channel_type: Filter by channel type (any, show).
		:param result_limit: Up to 500 results can be returned.
		
		ps: A call to this method has a quota cost of 100 units.
		"""
		channels = []
		channels_items = []
		item_count = 0

		response = self.service.search().list(
			part='snippet',
			q=search_keyword,
			channelType=channel_type,
			publishedBefore=published_before,
			publishedAfter=published_after,
			regionCode=region_code,
			type='channel',
			order=order_by,
			maxResults=50
		).execute()

		if response['pageInfo']['totalResults'] == 0:			
			raise SearchResultReturnsNone("No channels found for the search keyword: " + search_keyword)

		# total_results = response['pageInfo']['totalResults']
		channels_items.extend(response['items'])
		nextPageToken = response.get('nextPageToken')
		item_count += len(response['items'])
		print('Token {0}'.format(nextPageToken))

		while nextPageToken:
			if result_limit > item_count:
				response = self.service.search().list(
					part='snippet',
					q=search_keyword,
					channelType=channel_type,
					publishedBefore=published_before,
					publishedAfter=published_after,
					regionCode=region_code,
					type='channel',
					order=order_by,
					maxResults=50,
					pageToken=nextPageToken
				).execute()				
				channels_items.extend(response['items'])
				nextPageToken = response.get('nextPageToken')
				item_count += len(response['items'])
				print('Token {0}'.format(nextPageToken))
			else:
				nextPageToken = None
		
		for channel_item in channels_items:
			channels.append(SearchResultsChannel(
				channel_item['snippet']['channelId'],
				channel_item['snippet']['channelTitle'],
				channel_item['snippet']['description'],
				channel_item['snippet']['publishedAt'],
				region_code,
				channel_item['snippet']['thumbnails']['default']['url'],
				'https://www.youtube.com/channel/{0}'.format(channel_item['snippet']['channelId'])
			))
		return channels

	def searchPlaylists(self, search_keyword, region_code='us', published_before=None, published_after=None, order_by='relevance', result_limit=50):
		"""
		Search Playlists (There is a limit of up to 500 items can be returned)
		:param search_keyword: Query term.
		:param region_code: The region code for the search.
		:param published_before: Filter by date and time published before this time 
			(The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z)).
		:param published_after: Filter by date and time published after this time.
			(The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z)).
		:param order_by: Order results by (date, rating, relevance, title, videoCount, viewCount).
		:param result_limit: Up to 500 results can be returned.
		
		ps: A call to this method has a quota cost of 100 units.
		"""
		playlists = []
		playlist_items = []
		item_count = 0

		response = self.service.search().list(
			part='snippet',
			q=search_keyword,
			publishedBefore=published_before,
			publishedAfter=published_after,
			regionCode=region_code,
			type='playlist',
			order=order_by,
			maxResults=50
		).execute()

		if response['pageInfo']['totalResults'] == 0:			
			raise SearchResultReturnsNone("No playlists found for the search keyword: " + search_keyword)

		# total_results = response['pageInfo']['totalResults']
		playlist_items.extend(response['items'])
		nextPageToken = response.get('nextPageToken')
		item_count += len(response['items'])
		print('Token {0}'.format(nextPageToken))

		while nextPageToken:
			if result_limit > item_count:
				response = self.service.search().list(
					part='snippet',
					q=search_keyword,
					publishedBefore=published_before,
					publishedAfter=published_after,
					regionCode=region_code,
					type='playlist',
					order=order_by,
					maxResults=50,
					pageToken=nextPageToken
				).execute()				
				playlist_items.extend(response['items'])
				nextPageToken = response.get('nextPageToken')
				item_count += len(response['items'])
				print('Token {0}'.format(nextPageToken))
			else:
				nextPageToken = None
		
		for playlist_item in playlist_items:
			playlists.append(SearchResultsPlaylist(					
				playlist_item['id']['playlistId'],
				playlist_item['snippet']['title'],
				playlist_item['snippet']['channelId'],
				playlist_item['snippet']['channelTitle'],
				playlist_item['snippet']['description'],
				playlist_item['snippet']['publishedAt'],
				region_code,
				playlist_item['snippet']['thumbnails']['default']['url'],
				'https://www.youtube.com/playlist?list={0}'.format(playlist_item['id']['playlistId'])
			))
		return playlists	

