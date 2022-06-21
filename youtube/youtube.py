import re
from .exceptions import YouTubeException, NoVideosReturned
from .google_apis import create_service

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

    def get_comment_threads(self, service, video_id, sort_by='time', sort_order='asc'):
        order = ['asc', 'desc'].index(sort_order)
        comment_threads = []

        response = service.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=100,
            order=sort_by,  # time | relevance
            textFormat='plainText'  # plainText | html
        ).execute()
        comment_threads = response['items']
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = service.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                maxResults=100,
                order=sort_by,  # time | relevance
                textFormat='plainText',  # plainText | html
                pageToken=nextPageToken
            ).execute()

            comment_threads.extend(response['items'])
            nextPageToken = response.get('nextPageToken')
        comment_threads = sorted(comment_threads, key=lambda x: x['snippet']['topLevelComment']['snippet']['publishedAt'], reverse=order)            
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

	def channelComments(self, channel_id:str):
		#TODO
		response_commentThreads = yt.service.commentThreads().list(
	    part='snippet',
	    # videoId='SpmWlHRVn9c',
	    allThreadsRelatedToChannelId='UCw-ppX-E9oGs2b_Mt4Rq4fQ',
	    maxResults=100,
	    order='time',                       # {time; relevance}
	    textFormat='plainText'              # {plainText; html}    
	).execute()


class CommentThreadViewer(QWidget):
	def __init__(self, parent=None):
		super().__init__()
		self.parent = parent
	
		layout = QVBoxLayout()

		layout_channel_info = QFormLayout()
		layout_channel_info.setLabelAlignment(Qt.AlignRight)
		layout.addLayout(layout_channel_info)

		self.video_id = QLineEdit()
		layout_channel_info.addRow(QLabel('video Id:'), self.video_id)

		self.video_name = QLineEdit()
		self.video_name.setReadOnly(True)
		layout_channel_info.addRow(QLabel('Video Name:'), self.video_name)

		self.comments = QTextBrowser ()
		self.comments.verticalScrollBar().setMinimumWidth(500)
		# self.comments.s
		layout.addWidget(self.comments)

		button_layout = QHBoxLayout()
		layout.addLayout(button_layout)
		button_layout.addStretch()

		self.button_retrieve = QPushButton('Retrieve')
		self.button_retrieve.clicked.connect(self.retrieve_comments)
		button_layout.addWidget(self.button_retrieve)

		self.button_reset = QPushButton('Reset fields')
		self.button_reset.clicked.connect(self.reset_fields)
		button_layout.addWidget(self.button_reset)

		self.setLayout(layout)

	# def wheelEvent(self, event):
	# 	if event.modifiers() == Qt.ControlModifier :
	# 		if event.angleDelta().y() > 0:
	# 			fnt_size = self.comments.fontPointSize()
	# 			print(fnt_size + 2)
	# 			self.comments.setFontPointSize(fnt_size + 2)
	# 		else:
	# 			fnt_size = self.comments.fontPointSize()
	# 			print(fnt_size - 2)				
	# 			self.comments.setFontPointSize(fnt_size - 2)

	def retrieve_comments(self):
		# try:

		video_id_raw = self.video_id.text().strip()

		# pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'
		# result = re.match(r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})', video_id_raw, re.IGNORECASE)

		# if re.match(r'(https://studio.youtube.com/video/)([^\/]{11})', video_id_raw, re.IGNORECASE):
		# 	video_id = re.match(r'(https://studio.youtube.com/video/)([^\/]{11})', video_id_raw, re.IGNORECASE)[2]
		# elif re.match(r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})', video_id_raw, re.IGNORECASE):
		# 	video_id = re.match(r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})', video_id_raw, re.IGNORECASE)[1]
		# else:
		# 	video_id = None

		video_id = video_id_raw
		# if video_id.startswith("https://www.youtube.com/watch?v="):
			# video_id = video_id.replace('https://www.youtube.com/watch?v=', '')

		if self.parent.service is None:
			self.parent.status.setText('Please connect to YouTube')
			return
		elif not video_id:
			self.parent.status.setText('Please check video Id')
			return

		try:
			response_video_name = self.parent.yt.get_video_info(self.parent.service, video_id)
		except Exception as e:
			self.parent.status.setText(str(e))
			return

		try:
			if response_video_name['pageInfo']['totalResults'] == 0:
				self.parent.status.setText('No result returned')
				return
			else:
				self.video_name.setText(response_video_name['items'][0]['snippet']['title'])
		except TypeError as e:
			if TypeError is ConnectionAbortedError:
				self.parent.status.setText('Lost connection. Please reconnect')
				return
			else:
				self.parent.status.setText(str(e))
		except Exception as e:
			self.parent.status.setText(str(e))

		### populate video info
		self.comments.clear()
		self.comments.setFontPointSize(float(self.parent.comboFontSize.currentText()))
		try:
			
			### populate comments
			comment_threads = self.parent.yt.get_comment_threads(self.parent.service, video_id)

			for index, comment_thread in enumerate(comment_threads):
				published = comment_thread['snippet']['topLevelComment']['snippet']['publishedAt'][:-1].replace('T', ' ')
				comment_text = comment_thread['snippet']['topLevelComment']['snippet']['textDisplay']
				author_name = comment_thread['snippet']['topLevelComment']['snippet']['authorDisplayName']

				### Some users' account might got deleted but the post will remain
				if comment_thread['snippet']['topLevelComment']['snippet'].get('authorChannelId'):
					author_channel_id = comment_thread['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
				else:
					author_channel_id = ''
					author_name = 'Author Profile Removed'

				like_count = comment_thread['snippet']['topLevelComment']['snippet']['likeCount']
				comment_thread_id = comment_thread['id']
				self.comments.insertPlainText('Author: {0} ({1})\n'.format(author_name, author_channel_id))
				self.comments.insertPlainText('Post Date: {0}\n'.format(published))
				self.comments.insertPlainText('#{1} Comment: (Like Count: {0})'.format(like_count, index + 1) + '\n')
				self.comments.insertPlainText(comment_text + '\n')
				self.comments.insertPlainText('\n')
				self.comments.insertPlainText('-'*90 + '\n')

				### Check if any reply
				total_replies = comment_thread['snippet']['totalReplyCount']
				if total_replies > 0:
					comments = []

					response = self.parent.service.comments().list(
						part='snippet',
						parentId=comment_thread_id,
						maxResults=100,
						textFormat='plainText'
					).execute()
					comments = response['items']
					nextPageToken = response.get('nextPageToken')

					while nextPageToken:
						response = self.parent.service.comments().list(
							part='snippet',
							parentId=comment_thread_id,
							maxResults=100,
							textFormat='plainText',
							pageToken=nextPageToken
						).execute()
						comments.extend(response['items'])
						nextPageToken = response.get('nextPageToken')

					# comments = comment_thread['replies']['comments']
					comments = sorted(comments, key=lambda x: x['snippet']['publishedAt'], reverse=False)
					for sub_index, comment in enumerate(comments):
						self.x = comment['snippet']
						published = comment['snippet']['publishedAt'][:-1].replace('T', ' ')
						comment_text = comment['snippet']['textDisplay']
						author_name = comment['snippet']['authorDisplayName']
						author_channel_id = comment['snippet']['authorChannelId']['value']
						like_count = comment['snippet']['likeCount']

						self.comments.insertPlainText('Reply #{0}-{1}\n'.format(index + 1, sub_index + 1))
						self.comments.insertPlainText('-'*90 + '\n')
						self.comments.insertPlainText('Author: {0} ({1})\n'.format(author_name, author_channel_id))
						self.comments.insertPlainText('Post Date: {0}\n'.format(published))
						self.comments.insertPlainText('#{1}-{2} Comment: (Like Count: {0})'.format(like_count, index + 1, sub_index + 1) + '\n')
						self.comments.insertPlainText(comment_text + '\n')
						self.comments.insertPlainText('\n')
						self.comments.insertPlainText('-'*90 + '\n')

				self.parent.status.clear()
		except Exception as e:
			print(str(e))
			self.parent.status.setText(str(e))
