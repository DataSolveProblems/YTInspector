
class YouTubeException(Exception):
	"""YouTube Exception Base Class"""

class NoVideosReturned(YouTubeException):
	""""""

class NoCommentsReturned(YouTubeException):
	""""""

class SearchResultReturnsNone(YouTubeException):
	""""""