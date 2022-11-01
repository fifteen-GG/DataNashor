# DataNashor

> League of Legends live replay data parser package


## What is DataNashor?

DataNashor is a League of Legends live replay data parser package.

DataNashor parses live data from League Client using Riot's official [Live Client Data API](https://developer.riotgames.com/docs/lol#game-client-api_live-client-data-api).

## Installation
```
> pip install datanashor
```

## Getting Started
Parse all replay files in the replay directories
```Python
from datanashor.parser import ReplayParser

parser = ReplayParser()
parser.parse()
```

## To parse Client Metadata from lockfile

League of Legends Client MUST be running.

```Python
from datanashor.parser import ReplayParser

parser = ReplayParser(current_game_version='12.20')
parser.get_client_metadata()
```

### Prerequisites

```
League of Legends KR Client
Windows System
Python 3.9+
```