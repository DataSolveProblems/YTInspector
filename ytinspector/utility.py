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