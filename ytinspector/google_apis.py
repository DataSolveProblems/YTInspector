import pickle
import os
import datetime
from collections import namedtuple
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request


def create_service(client_secret_file, api_name, api_version, *scopes, prefix=''):
	CLIENT_SECRET_FILE = client_secret_file
	API_SERVICE_NAME = api_name
	API_VERSION = api_version
	SCOPES = [scope for scope in scopes[0]]
	
	cred = None
	working_dir = os.getcwd()
	token_dir = 'token files'
	pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.pickle'

	### Check if token dir exists first, if not, create the folder
	if not os.path.exists(os.path.join(working_dir, token_dir)):
		os.mkdir(os.path.join(working_dir, token_dir))

	if os.path.exists(os.path.join(working_dir, token_dir, pickle_file)):
		with open(os.path.join(working_dir, token_dir, pickle_file), 'rb') as token:
			cred = pickle.load(token)

	if not cred or not cred.valid:
		if cred and cred.expired and cred.refresh_token:
			cred.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
			cred = flow.run_local_server()

		with open(os.path.join(working_dir, token_dir, pickle_file), 'wb') as token:
			pickle.dump(cred, token)

	try:
		service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
		print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
		return service
	except Exception as e:
		print(e)
		print(f'Failed to create service instance for {API_SERVICE_NAME}')
		os.remove(os.path.join(working_dir, token_dir, pickle_file))
		return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
	dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
	return dt

class SheetsHelper:
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

	# --> spreadsheets().batchUpdate()
	Paste_Type = namedtuple('_Paste_Type', 
					('normal', 'value', 'format', 'without_borders', 
					 'formula', 'date_validation', 'conditional_formatting')
					)('PASTE_NORMAL', 'PASTE_VALUES', 'PASTE_FORMAT', 'PASTE_NO_BORDERS', 
					  'PASTE_FORMULA', 'PASTE_DATA_VALIDATION', 'PASTE_CONDITIONAL_FORMATTING')

	Paste_Orientation = namedtuple('_Paste_Orientation', ('normal', 'transpose'))('NORMAL', 'TRANSPOSE')

	Merge_Type = namedtuple('_Merge_Type', ('merge_all', 'merge_columns', 'merge_rows')
					)('MERGE_ALL', 'MERGE_COLUMNS', 'MERGE_ROWS')

	Delimiter_Type = namedtuple('_Delimiter_Type', ('comma', 'semicolon', 'period', 'space', 'custom', 'auto_detect')
						)('COMMA', 'SEMICOLON', 'PERIOD', 'SPACE', 'CUSTOM', 'AUTODETECT')

	# --> Types
	Dimension = namedtuple('_Dimension', ('rows', 'columns'))('ROWS', 'COLUMNS')

	Value_Input_Option = namedtuple('_Value_Input_Option', ('raw', 'user_entered'))('RAW', 'USER_ENTERED')

	Value_Render_Option = namedtuple('_Value_Render_Option',["formatted", "unformatted", "formula"]
							)("FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA")

	def __init__(self, scopes=None):
		if not scopes:
			self.scopes = self.SCOPES
		else:
			self.scopes = scopes
		
	@staticmethod
	def define_cell_range(
		sheet_id, 
		start_row_number=1, end_row_number=0, 
		start_column_number=None, end_column_number=0):
		"""GridRange object"""
		json_body = {
			'sheetId': sheet_id,
			'startRowIndex': start_row_number - 1,
			'endRowIndex': end_row_number,
			'startColumnIndex': start_column_number - 1,
			'endColumnIndex': end_column_number
		}
		return json_body

	@staticmethod
	def define_dimension_range(sheet_id, dimension, start_index, end_index):
		json_body = {
			'sheetId': sheet_id,
			'dimension': dimension,
			'startIndex': start_index,
			'endIndex': end_index
		}
		return json_body



class CalendarHelper:
	API_NAME = 'calendar'
	API_VERSION = 'v3'
	SCOPES = ['https://www.googleapis.com/auth/calendar']

	def __init__(self, scopes=None):
		if not scopes:
			self.scopes = self.SCOPES
		else:
			self.scopes = scopes

class DriveHelper:
	API_NAME = 'drive'
	API_VERSION = 'v3'
	SCOPES = ['https://www.googleapis.com/auth/drive']

	def __init__(self, scopes=None):
		if not scopes:
			self.scopes = self.SCOPES
		else:
			self.scopes = scopes

class YouTubeHelper:
	API_NAME = 'youtube'
	VERSION = 'v3'
	SCOPES = [
		'https://www.googleapis.com/auth/youtube',
		'https://www.googleapis.com/auth/youtube.force-ssl',
		'https://www.googleapis.com/auth/youtubepartner'
	]

	def get_comment_threads(service, video_id, sort_by='time', sort_order='asc'):
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

		if sort_by == 'time':
			comment_threads = sorted(comment_threads, key=lambda x: x['snippet']['topLevelComment']['snippet']['publishedAt'], reverse=order)
		elif sort_by == 'relevance':
			comment_threads = sorted(comment_threads, key=lambda x: x['snippet']['topLevelComment']['snippet']['authorChannelId']['likeCount'], reverse=order)
		return comment_threads

if __name__ == '__main__':
	g = GoogleSheetsHelper()
	print(g.Value_Render_Option)
