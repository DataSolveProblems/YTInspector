import re
import requests
from collections import namedtuple

ChannelRelatedComment = namedtuple('VideoComment', 
	['channel_id', 'video_id', 'comment_thread_id', 'comment_text', 'commenter_name', 'commenter_channel', 'like_count', 'published_timestamp', 'updated_timestamp', 'reply_count', 'replies'])

VideoComment = namedtuple('VideoComment', 
	['video_id', 'comment_thread_id', 'comment_text', 'commenter_name', 'commenter_channel', 'like_count', 'published_timestamp', 'updated_timestamp', 'reply_count', 'replies'])
    
VideoReply = namedtuple('VideoCommentReply', 
	['comment_reply_id', 'comment_thread_id', 'reply_text', 'reply_commenter_name','reply_commenter_channel', 'like_count', 'published_timestamp', 'updated_timestamp' ])

SearchResultsVideo = namedtuple('SearchResultsVideo',
    ['video_id', 'video_title', 'channel_id', 'channel_title', 'description', 'published_at', 'region_code', 'thumbnails', 'video_url']
)

SearchResultsChannel = namedtuple('SearchResultsChannel',
    ['channel_id', 'channel_title', 'description', 'published_at', 'region_code', 'thumbnails', 'channel_url']
)

SearchResultsPlaylist = namedtuple('SearchResultsPlaylist',
    ['playlist_id', 'playlist_title', 'channel_id', 'channel_title', 'description', 'published_at', 'region_code', 'thumbnails', 'playlist_url']
)


def convert_duration(duration):
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

def locate_channel_id(video_id):
    """returns channel url and channel id"""
    results = re.search(r'channel\/(UC.{22})', response.text, re.MULTILINE)
    if results:
        return results.group(1)
    else:
        return
        
