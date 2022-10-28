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
```Python
from DataNashor.parser import ReplayParser

parser = ReplayParser()
parser.parse()
```

### Prerequisites

```
League of Legends KR Client
Windows System
Python 3.9+
```