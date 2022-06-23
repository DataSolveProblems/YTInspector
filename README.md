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

3. Start using YTInspector:

## Examples

### 1. Search videos

```python
from ytinspector import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)

# initialize YouTube service connection
yt.initService()

# perform video search
video_results = yt.searchVideos('tesla')
```

### 2. Serach videos by release date range

```python
from ytinspector import YouTube, convert_to_RFC_datetime

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
from ytinspector import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

categories = yt.retrieveVideoCategoriesList()
```

### 4. Search channels

```python
from ytinspector import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

channel_list = yt.searchChannels('electrical cars')
```

### 5. Search playlists

```python
from ytinspector import YouTube

CLIENT_FILE = 'client-secret.json'

yt = YouTube(CLIENT_FILE)
yt.initService()

playlist_list = yt.searchPlaylists('electrical cars')
```
