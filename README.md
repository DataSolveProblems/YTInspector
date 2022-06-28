# YouTube Channel Video Inspector

A lightweight Python library to simplify querying YouTube stuff (videos, comments, channels, playlists).

**Features**:

- Search videos, channels, playlists with additional filters.
- Search video comments (including replies) by keywords.
- Pull channel latest comments.
- Pull channel upload videos infos.

## Installation

`pip install git+https://github.com/DataSolveProblems/YTInspector.git`

Requirements: Python 3.6+.

## Basic Usage

1. [Create a credential in Google Cloud Console.](console.cloud.google.com/)

2. [Create a project, set up OAuth2 protocol, and download client file.](https://youtu.be/PKLG5pfs4nY)

3. Enable YouTube Data API.

4. Start using YTInspector:

## Examples (YouTube)

### 1. Search videos

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)

# initialize YouTube service connection
yt.initService()

# perform video search
video_results = yt.searchVideos('tesla')
```

### 2. Serach videos by uploaded date range

```python
from ytinspector import convert_to_RFC_datetime
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

video_results = yt.searchVideos(
    'tesla', 
    region_code='us', 
    published_after=convert_to_RFC_datetime(2022, 1, 1), 
    published_before=convert_to_RFC_datetime(2022, 1, 31)
)
```

### 3. List video categories

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

categories = yt.retrieveVideoCategoriesList()
```

### 4. Search channels

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

channel_list = yt.searchChannels('electrical cars')
```

### 5. Search playlists

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

playlist_list = yt.searchPlaylists('electrical cars')
```

### 6. Retrieve channel uploaded videos

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

channel_videos = yt.retrieveChannelVideos('UCVhDYDVo3AqyMIKtMLSrcEg')
```

### 7. Retrieve video comments (comment threads only)

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

video_comments = yt.retrieveVideoComments('bcNUbQ2CBHM')
```

### 8. Retrieve video comments (include replies)

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

video_comments = yt.retrieveVideoComments('bcNUbQ2CBHM', include_replies=True)
```

### 9. Retrieve channel latest comments

```python
from ytinspector.youtube import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

latest_comments = yt.retrieveChannelRelatedComments('UCVhDYDVo3AqyMIKtMLSrcEg')
```

### 10. Extract channel id
```python
from ytinspector import locate_channel_id

video_id = 't49Q6qhMfk8'
channel_id = locate_channel_id(video_id)
print(channel_id)                                
```

## Examples (YouTube Data Analytics)

#### 1. Run report query
*Using the query method, you should be able to run any report that the API supports*
**below query is equalvant to top 200 playlists by views**

```python
response = yt_analytics.query(
	start_date='2017-01-01', 
	end_date='2022-05-31',
	metric_list=['playlistStarts', 'estimatedMinutesWatched', 'views', 'viewsPerPlaylistStart'],
	dimension_list=['playlist'],
	sort_by='-views',
	max_result=200,
	filters='isCurated==1'
)
df = pd.DataFrame(response[1], columns=response[0])
print(df)
```

### 2. Channel Sumamry Report

```python
response = yt_analytics.channelSummary('2022-01-01', '2022-05-31')
df = pd.DataFrame(response[1], columns=response[0])
print(df)
```

### 3. Summary by country

```python
response = yt_analytics.summaryByCountry('2022-01-01', '2022-05-31', country_code='au', is_yt_partner=True)
df = pd.DataFrame(response[1], columns=response[0])
print(df)
```

### 4. Top 200 videos

```python
response = yt_analytics.top200Videos('2022-01-01', '2022-05-31', sortby_field='subscribersGained', is_yt_partner=True)
df = pd.DataFrame(response[1], columns=response[0])
print(df)
```

### 5. PlaylistSummary

```python
response = yt_analytics.playlistSummary('2022-01-01', '2022-05-31', playlist_id=None)
df = pd.DataFrame(response[1], columns=response[0])
print(df)
```

### 6. Top 200 playlists

```python
response = yt_analytics.top200Playlists('2022-01-01', '2022-05-31', sortby_field='estimatedMinutesWatched')
df = pd.DataFrame(response[1], columns=response[0])
print(df)
```

## Reference
- [YouTube Data API Reference](https://developers.google.com/youtube/v3/docs)
- [Set up credentials](https://developers.google.com/youtube/v3/guides/auth/client-side-web-apps)