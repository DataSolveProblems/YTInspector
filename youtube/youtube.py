
from .exceptions import YouTubeException, NoVideosReturned
from .google_apis import create_service

class YouTube:
	SCOPES = ['https://www.googleapis.com/auth/youtube', 
			  'https://www.googleapis.com/auth/youtube.force-ssl',
			  'https://www.googleapis.com/auth/youtubepartner']
	API_NAME = 'youtube'
	API_VERSION = 'v3'

	def __init__(self, client_secret_file):
		self.client_secret_file = client_secret_file
		self.service = None
	   
	def initService(self, prefix=None):
		try:
			self.service = create_service(self.client_secret_file, self.API_NAME, self.API_VERSION, self.SCOPES, prefix=prefix)
		except Exception as e:
			raise YouTubeException(e)

	def getChannelVideos(self, channel_id, id_type='by id'):
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