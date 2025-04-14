# API Reference

This document provides detailed information about the FOGIS API Client classes, methods, and data types.

## Table of Contents

- [FogisApiClient Class](#fogisapiclient-class)
- [Exception Classes](#exception-classes)
- [Data Types](#data-types)
- [Event Types](#event-types)

## FogisApiClient Class

The main class for interacting with the FOGIS API.

### Constructor

```python
FogisApiClient(username=None, password=None, cookies=None)
```

**Parameters:**
- `username` (Optional[str]): FOGIS username. Required if cookies are not provided.
- `password` (Optional[str]): FOGIS password. Required if cookies are not provided.
- `cookies` (Optional[Dict[str, str]]): Session cookies for authentication. If provided, username and password are not required.

**Raises:**
- `ValueError`: If neither valid credentials nor cookies are provided

**Example:**
```python
# Initialize with username and password
client = FogisApiClient(username="your_username", password="your_password")

# Initialize with cookies
client = FogisApiClient(cookies={"FogisMobilDomarKlient_ASPXAUTH": "cookie_value",
                                "ASP_NET_SessionId": "session_id"})
```

### Authentication Methods

#### login

```python
login() -> Dict[str, str]
```

Logs into the FOGIS API and stores the session cookies.

**Returns:**
- `Dict[str, str]`: The session cookies if login is successful

**Raises:**
- `FogisLoginError`: If login fails or if neither credentials nor cookies are available
- `FogisAPIRequestError`: If there's an error during the login request

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
cookies = client.login()
print("Login successful" if cookies else "Login failed")
```

#### validate_cookies

```python
validate_cookies() -> bool
```

Validates if the current cookies are still valid for authentication.

**Returns:**
- `bool`: True if cookies are valid, False otherwise

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
client.login()
# Later, check if the session is still valid
if client.validate_cookies():
    print("Session is still valid")
else:
    print("Session has expired, need to login again")
```

#### get_cookies

```python
get_cookies() -> Optional[Dict[str, str]]
```

Returns the current session cookies.

**Returns:**
- `Optional[Dict[str, str]]`: The current session cookies, or None if not authenticated

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
client.login()
cookies = client.get_cookies()  # Save these cookies for later use
print("Cookies retrieved" if cookies else "No cookies available")

# Later, in another session:
new_client = FogisApiClient(cookies=cookies)  # Authenticate with saved cookies
print("Using saved cookies for authentication")
```

### Match Methods

#### fetch_matches_list_json

```python
fetch_matches_list_json(filter=None) -> List[Dict[str, Any]]
```

Fetches the list of matches for the logged-in referee.

**Parameters:**
- `filter` (Optional[Dict[str, Any]]): An optional dictionary containing server-side date range filter criteria.
  Common filter parameters include:
  - `datumFran`: Start date in format 'YYYY-MM-DD'
  - `datumTill`: End date in format 'YYYY-MM-DD'
  - `datumTyp`: Date type filter (e.g., 'match', 'all')
  - `sparadDatum`: Saved date filter

**Returns:**
- `List[Dict[str, Any]]`: A list of match dictionaries

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
# Get matches with default date range
matches = client.fetch_matches_list_json()

# Get matches with custom date range
from datetime import datetime, timedelta
today = datetime.now().strftime('%Y-%m-%d')
next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
matches = client.fetch_matches_list_json({
    'datumFran': today,
    'datumTill': next_week,
    'datumTyp': 'match'
})
```

#### fetch_match_json

```python
fetch_match_json(match_id: Union[str, int]) -> Dict[str, Any]
```

Fetches detailed information for a specific match.

**Parameters:**
- `match_id` (Union[str, int]): The ID of the match to fetch

**Returns:**
- `Dict[str, Any]`: Match details including teams, score, venue, etc.

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
match = client.fetch_match_json(123456)
print(f"Match: {match['hemmalag']} vs {match['bortalag']}")
```

#### fetch_match_result_json

```python
fetch_match_result_json(match_id: Union[str, int]) -> Union[Dict[str, Any], List[Dict[str, Any]]]
```

Fetches the match results in JSON format for a given match ID.

**Parameters:**
- `match_id` (Union[str, int]): The ID of the match

**Returns:**
- `Union[Dict[str, Any], List[Dict[str, Any]]]`: Result information for the match, including full-time and half-time scores

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
result = client.fetch_match_result_json(123456)
if isinstance(result, dict):
    print(f"Score: {result.get('hemmamal', 0)}-{result.get('bortamal', 0)}")
else:
    print(f"Multiple results found: {len(result)}")
```

#### report_match_result

```python
report_match_result(result_data: Dict[str, Any]) -> Dict[str, Any]
```

Reports match results (halftime and fulltime) to the FOGIS API.

**Parameters:**
- `result_data` (Dict[str, Any]): Data containing match results. Must include:
  - `matchid`: The ID of the match
  - `hemmamal`: Full-time score for the home team
  - `bortamal`: Full-time score for the away team

  Optional fields:
  - `halvtidHemmamal`: Half-time score for the home team
  - `halvtidBortamal`: Half-time score for the away team

**Returns:**
- `Dict[str, Any]`: Response from the API, typically containing success status

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a dictionary
- `ValueError`: If required fields are missing

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
result = {
    "matchid": 123456,
    "hemmamal": 2,
    "bortamal": 1,
    "halvtidHemmamal": 1,
    "halvtidBortamal": 0
}
response = client.report_match_result(result)
print(f"Result reported successfully: {response.get('success', False)}")
```

#### mark_reporting_finished

```python
mark_reporting_finished(match_id: Union[str, int]) -> Dict[str, bool]
```

Mark a match report as completed/finished in the FOGIS system.

**Parameters:**
- `match_id` (Union[str, int]): The ID of the match to mark as finished

**Returns:**
- `Dict[str, bool]`: The response from the FOGIS API, typically containing a success status

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a dictionary
- `ValueError`: If match_id is empty or invalid

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
client.login()
result = client.mark_reporting_finished(match_id=123456)
print(f"Report marked as finished: {result.get('success', False)}")
```

### Player and Team Methods

#### fetch_match_players_json

```python
fetch_match_players_json(match_id: Union[str, int]) -> Dict[str, List[Dict[str, Any]]]
```

Fetches player information for a specific match.

**Parameters:**
- `match_id` (Union[str, int]): The ID of the match

**Returns:**
- `Dict[str, List[Dict[str, Any]]]`: Player information for the match, typically containing keys for home and away team players

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a dictionary

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
players = client.fetch_match_players_json(123456)
home_players = players.get('hemmalag', [])
away_players = players.get('bortalag', [])
print(f"Home team has {len(home_players)} players, Away team has {len(away_players)} players")
```

#### fetch_team_players_json

```python
fetch_team_players_json(team_id: Union[str, int]) -> Dict[str, Any]
```

Fetches player information for a specific team.

**Parameters:**
- `team_id` (Union[str, int]): The ID of the team

**Returns:**
- `Dict[str, Any]`: Dictionary containing player information for the team with a 'spelare' key that contains a list of players

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
team_players = client.fetch_team_players_json(12345)
players = team_players.get('spelare', [])
print(f"Team has {len(players)} players")
if players:
    print(f"First player: {players[0]['fornamn']} {players[0]['efternamn']}")
```

### Event Methods

#### fetch_match_events_json

```python
fetch_match_events_json(match_id: Union[str, int]) -> List[Dict[str, Any]]
```

Fetches events information for a specific match.

**Parameters:**
- `match_id` (Union[str, int]): The ID of the match

**Returns:**
- `List[Dict[str, Any]]`: List of events information for the match, including goals, cards, substitutions, and other match events

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a list

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
events = client.fetch_match_events_json(123456)
goals = [event for event in events if event.get('mal', False)]
print(f"Total events: {len(events)}, Goals: {len(goals)}")
```

#### report_match_event

```python
report_match_event(event_data: Dict[str, Any]) -> Dict[str, Any]
```

Reports a match event to FOGIS.

**Parameters:**
- `event_data` (Dict[str, Any]): Data for the event to report. Must include at minimum:
  - `matchid`: The ID of the match
  - `handelsekod`: The event type code (see EVENT_TYPES)
  - `minut`: The minute when the event occurred
  - `lagid`: The ID of the team associated with the event

  Depending on the event type, additional fields may be required:
  - `personid`: The ID of the player (for player-related events)
  - `assisterandeid`: The ID of the assisting player (for goals)
  - `period`: The period number
  - `resultatHemma/resultatBorta`: Updated score (for goals)

**Returns:**
- `Dict[str, Any]`: Response from the API, typically containing success status and the ID of the created event

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a dictionary

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
# Report a goal
event = {
    "matchid": 123456,
    "handelsekod": 6,  # Regular goal
    "minut": 35,
    "lagid": 78910,  # Team ID
    "personid": 12345,  # Player ID
    "period": 1,
    "resultatHemma": 1,
    "resultatBorta": 0
}
response = client.report_match_event(event)
print(f"Event reported successfully: {response.get('success', False)}")
```

#### delete_match_event

```python
delete_match_event(event_id: Union[str, int]) -> bool
```

Deletes a specific event from a match.

**Parameters:**
- `event_id` (Union[str, int]): The ID of the event to delete

**Returns:**
- `bool`: True if deletion was successful, False otherwise

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
# Get all events for a match
events = client.fetch_match_events_json(123456)
if events:
    # Delete the first event
    event_id = events[0]['matchhandelseid']
    success = client.delete_match_event(event_id)
    print(f"Event deletion {'successful' if success else 'failed'}")
```

#### clear_match_events

```python
clear_match_events(match_id: Union[str, int]) -> Dict[str, bool]
```

Clear all events for a match.

**Parameters:**
- `match_id` (Union[str, int]): The ID of the match

**Returns:**
- `Dict[str, bool]`: Response from the API, typically containing a success status

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a dictionary

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
response = client.clear_match_events(123456)
print(f"Events cleared successfully: {response.get('success', False)}")
```

### Official Methods

#### fetch_match_officials_json

```python
fetch_match_officials_json(match_id: Union[str, int]) -> Dict[str, List[Dict[str, Any]]]
```

Fetches officials information for a specific match.

**Parameters:**
- `match_id` (Union[str, int]): The ID of the match

**Returns:**
- `Dict[str, List[Dict[str, Any]]]`: Officials information for the match, typically containing keys for referees and other match officials

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a dictionary

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
officials = client.fetch_match_officials_json(123456)
referees = officials.get('domare', [])
if referees:
    print(f"Main referee: {referees[0]['fornamn']} {referees[0]['efternamn']}")
else:
    print("No referee assigned yet")
```

#### fetch_team_officials_json

```python
fetch_team_officials_json(team_id: Union[str, int]) -> List[Dict[str, Any]]
```

Fetches officials information for a specific team.

**Parameters:**
- `team_id` (Union[str, int]): The ID of the team

**Returns:**
- `List[Dict[str, Any]]`: List of officials information for the team, including coaches, managers, and other team staff

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a list

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
officials = client.fetch_team_officials_json(12345)
print(f"Team has {len(officials)} officials")
if officials:
    coaches = [o for o in officials if o.get('roll', '').lower() == 'tränare']
    print(f"Number of coaches: {len(coaches)}")
```

#### report_team_official_action

```python
report_team_official_action(action_data: Dict[str, Any]) -> Dict[str, Any]
```

Reports team official disciplinary action to the FOGIS API.

**Parameters:**
- `action_data` (Dict[str, Any]): Data containing team official action details. Must include:
  - `matchid`: The ID of the match
  - `lagid`: The ID of the team
  - `personid`: The ID of the team official
  - `matchlagledaretypid`: The type ID of the disciplinary action

  Optional fields:
  - `minut`: The minute when the action occurred

**Returns:**
- `Dict[str, Any]`: Response from the API, typically containing success status and the ID of the created action

**Raises:**
- `FogisLoginError`: If not logged in
- `FogisAPIRequestError`: If there's an error with the API request
- `FogisDataError`: If the response data is invalid or not a dictionary
- `ValueError`: If required fields are missing

**Example:**
```python
client = FogisApiClient(username="your_username", password="your_password")
# Report a yellow card for a team official
action = {
    "matchid": 123456,
    "lagid": 78910,  # Team ID
    "personid": 12345,  # Official ID
    "matchlagledaretypid": 1,  # Yellow card
    "minut": 35
}
response = client.report_team_official_action(action)
print(f"Action reported successfully: {response.get('success', False)}")
```

## Exception Classes

### FogisLoginError

Exception raised when login to FOGIS fails.

This exception is raised in the following cases:
- Invalid credentials
- Missing credentials when no cookies are provided
- Session expired
- Unable to find login form elements

**Attributes:**
- `message` (str): Explanation of the error

### FogisAPIRequestError

Exception raised when an API request to FOGIS fails.

This exception is raised in the following cases:
- Network connectivity issues
- Server errors
- Invalid request parameters
- Timeout errors

**Attributes:**
- `message` (str): Explanation of the error

### FogisDataError

Exception raised when there's an issue with the data from FOGIS.

This exception is raised in the following cases:
- Invalid response format
- Missing expected data fields
- JSON parsing errors
- Unexpected data types

**Attributes:**
- `message` (str): Explanation of the error

## Data Types

The FOGIS API Client uses several TypedDict classes to define the structure of data:

### MatchDict

Type definition for a match object returned by the API.

**Fields:**
- `matchid` (int): The ID of the match
- `matchnr` (str): The match number
- `datum` (str): The date of the match
- `tid` (str): The time of the match
- `hemmalag` (str): The name of the home team
- `bortalag` (str): The name of the away team
- `hemmalagid` (int): The ID of the home team
- `bortalagid` (int): The ID of the away team
- `arena` (str): The venue of the match
- `status` (str): The status of the match
- `domare` (str): The referee of the match
- `ad1` (str): The first assistant referee
- `ad2` (str): The second assistant referee
- `fjarde` (str): The fourth official
- `matchtyp` (str): The type of match
- `tavling` (str): The competition
- `grupp` (str): The group
- `hemmamal` (Optional[int]): The number of goals scored by the home team
- `bortamal` (Optional[int]): The number of goals scored by the away team
- `publik` (Optional[int]): The number of spectators
- `notering` (Optional[str]): Notes about the match
- `rapportstatus` (str): The status of the match report
- `matchstart` (Optional[str]): The start time of the match
- `halvtidHemmamal` (Optional[int]): The number of goals scored by the home team in the first half
- `halvtidBortamal` (Optional[int]): The number of goals scored by the away team in the first half

### PlayerDict

Type definition for a player object returned by the API.

**Fields:**
- `personid` (int): The ID of the player
- `fornamn` (str): The first name of the player
- `efternamn` (str): The last name of the player
- `smeknamn` (Optional[str]): The nickname of the player
- `tshirt` (Optional[str]): The jersey number of the player
- `position` (Optional[str]): The position of the player
- `positionid` (Optional[int]): The ID of the position
- `lagkapten` (Optional[bool]): Whether the player is the team captain
- `spelareid` (Optional[int]): The ID of the player in the match
- `licensnr` (Optional[str]): The license number of the player

### OfficialDict

Type definition for an official object returned by the API.

**Fields:**
- `personid` (int): The ID of the official
- `fornamn` (str): The first name of the official
- `efternamn` (str): The last name of the official
- `roll` (str): The role of the official
- `rollid` (int): The ID of the role

### EventDict

Type definition for an event object returned by the API.

**Fields:**
- `matchhandelseid` (int): The ID of the event
- `matchid` (int): The ID of the match
- `handelsekod` (int): The code of the event
- `handelsetyp` (str): The type of the event
- `minut` (int): The minute when the event occurred
- `lagid` (int): The ID of the team
- `lag` (str): The name of the team
- `personid` (Optional[int]): The ID of the player
- `spelare` (Optional[str]): The name of the player
- `assisterande` (Optional[str]): The name of the assisting player
- `assisterandeid` (Optional[int]): The ID of the assisting player
- `period` (Optional[int]): The period when the event occurred
- `mal` (Optional[bool]): Whether the event is a goal
- `resultatHemma` (Optional[int]): The number of goals scored by the home team after the event
- `resultatBorta` (Optional[int]): The number of goals scored by the away team after the event
- `strafflage` (Optional[str]): The position of the penalty
- `straffriktning` (Optional[str]): The direction of the penalty
- `straffresultat` (Optional[str]): The result of the penalty

## Event Types

The FOGIS API Client defines several event types for match events:

### Goals

- `6`: Regular Goal
- `39`: Header Goal
- `28`: Corner Goal
- `29`: Free Kick Goal
- `15`: Own Goal
- `14`: Penalty Goal

### Penalties

- `18`: Penalty Missing Goal
- `19`: Penalty Save
- `26`: Penalty Hitting the Frame

### Cards

- `20`: Yellow Card
- `8`: Red Card (Denying Goal Opportunity)
- `9`: Red Card (Other Reasons)

### Other Events

- `17`: Substitution

### Control Events

- `31`: Period Start
- `32`: Period End
- `23`: Match Slut (Match End)
