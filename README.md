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

## Examples

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

### 2. Serach videos by release date range

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

## Reference
- [YouTube Data API Reference](https://developers.google.com/youtube/v3/docs)
- [Set up credentials](https://developers.google.com/youtube/v3/guides/auth/client-side-web-apps)