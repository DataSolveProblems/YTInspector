import re
from collections import namedtuple
from .exceptions import YouTubeException, NoVideosReturned, NoCommentsReturned
from .google_apis import create_service

video_comment = namedtuple('VideoComment', 
	['comment_thread_id', 'comment_text', 'commenter_name', 'commenter_channel', 'like_count', 'published_timestamp', 'updated_timestamp', 'reply_count', 'replies'])
video_reply = namedtuple('VideoCommentReply', 
	['comment_reply_id', 'comment_thread_id', 'reply_text', 'reply_commenter_name','reply_commenter_channel', 'like_count', 'published_timestamp', 'updated_timestamp' ])

class YouTube:
	SCOPES = ['https://www.googleapis.com/auth/youtube', 
			  'https://www.googleapis.com/auth/youtube.force-ssl',
			  'https://www.googleapis.com/auth/youtubepartner']
	API_NAME = 'youtube'
	API_VERSION = 'v3'

	def __init__(self, client_secret_file:str):
		self.client_secret_file = client_secret_file
		self.service = None
	   
	def initService(self, prefix:str=None):
		try:
			self.service = create_service(self.client_secret_file, self.API_NAME, self.API_VERSION, self.SCOPES, prefix=prefix)
		except Exception as e:
			raise YouTubeException(e)

	def getChannelVideos(self, channel_id:str, id_type:str='by id'):
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
				comment_replies.append(video_reply(
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
			if 3000 > comment_thread_count:
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
				comment_threads.append(video_comment(
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
				comment_threads.append(video_comment(
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

	@staticmethod
	def convert_duration(duration:str):
		"""
		Convert duration string to seconds
		"""
		try:
			h = int(re.search('\d+H', duration)[0][:-1]) * 60**2  if re.search('\d+H', duration) else 0
			m = int(re.search('\d+M', duration)[0][:-1]) * 60  if re.search('\d+M', duration) else 0
			s = int(re.search('\d+S', duration)[0][:-1])  if re.search('\d+S', duration) else 0

			return h + m + s
		except Exception as e:
			print(e)
			return 0