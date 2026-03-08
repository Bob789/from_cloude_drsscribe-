import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CLIENT_SECRET_FILE = '/app/client_secret.json'


def get_calendar_auth_url(redirect_uri: str, state: str | None = None) -> str:
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES, redirect_uri=redirect_uri)
    kwargs = {'access_type': 'offline', 'prompt': 'consent'}
    if state:
        kwargs['state'] = state
    auth_url, _ = flow.authorization_url(**kwargs)
    return auth_url


def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES, redirect_uri=redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
    }


def get_calendar_service(refresh_token: str):
    with open(CLIENT_SECRET_FILE) as f:
        client_config = json.load(f)['web']
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_config['client_id'],
        client_secret=client_config['client_secret'],
        scopes=SCOPES,
    )
    return build('calendar', 'v3', credentials=creds)


async def create_event(refresh_token: str, event_data: dict) -> dict:
    service = get_calendar_service(refresh_token)
    event = {
        'summary': event_data['title'],
        'description': event_data.get('description', ''),
        'start': {'dateTime': event_data['start_time'], 'timeZone': 'Asia/Jerusalem'},
        'end': {'dateTime': event_data['end_time'], 'timeZone': 'Asia/Jerusalem'},
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': event_data.get('reminder_minutes', 60)}],
        },
    }
    result = service.events().insert(calendarId='primary', body=event).execute()
    return {'google_event_id': result['id'], 'html_link': result.get('htmlLink')}


async def update_event(refresh_token: str, google_event_id: str, event_data: dict) -> dict:
    service = get_calendar_service(refresh_token)
    event = service.events().get(calendarId='primary', eventId=google_event_id).execute()
    if 'title' in event_data:
        event['summary'] = event_data['title']
    if 'start_time' in event_data:
        event['start'] = {'dateTime': event_data['start_time'], 'timeZone': 'Asia/Jerusalem'}
    if 'end_time' in event_data:
        event['end'] = {'dateTime': event_data['end_time'], 'timeZone': 'Asia/Jerusalem'}
    if 'description' in event_data:
        event['description'] = event_data['description']
    result = service.events().update(calendarId='primary', eventId=google_event_id, body=event).execute()
    return {'google_event_id': result['id']}


async def delete_event(refresh_token: str, google_event_id: str):
    service = get_calendar_service(refresh_token)
    service.events().delete(calendarId='primary', eventId=google_event_id).execute()


async def get_today_events(refresh_token: str) -> list:
    service = get_calendar_service(refresh_token)
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0).isoformat() + '+02:00'
    end_of_day = now.replace(hour=23, minute=59, second=59).isoformat() + '+02:00'
    result = service.events().list(
        calendarId='primary', timeMin=start_of_day, timeMax=end_of_day,
        singleEvents=True, orderBy='startTime',
    ).execute()
    return result.get('items', [])


async def get_events_range(refresh_token: str, date_from: str, date_to: str) -> list:
    service = get_calendar_service(refresh_token)
    result = service.events().list(
        calendarId='primary',
        timeMin=date_from + 'T00:00:00+02:00',
        timeMax=date_to + 'T23:59:59+02:00',
        singleEvents=True, orderBy='startTime',
    ).execute()
    return result.get('items', [])
