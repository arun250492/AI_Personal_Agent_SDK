"""
Google integrations for Gmail, Calendar, and other Google services
"""

import os
import datetime
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle


class GoogleIntegration:
    """
    Integration with Google services (Gmail, Calendar, etc.)
    """

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]

    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.creds = None
        self.gmail_service = None
        self.calendar_service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google APIs"""
        token_path = os.path.join(os.path.dirname(self.credentials_path), 'token.pickle')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        # Build services
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)

    def get_recent_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails from Gmail"""
        try:
            results = self.gmail_service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])

            emails = []
            for msg in messages:
                msg_data = self.gmail_service.users().messages().get(
                    userId='me', id=msg['id']).execute()

                email = {
                    'id': msg['id'],
                    'subject': '',
                    'from': '',
                    'date': '',
                    'snippet': msg_data.get('snippet', '')
                }

                headers = msg_data.get('payload', {}).get('headers', [])
                for header in headers:
                    if header['name'] == 'Subject':
                        email['subject'] = header['value']
                    elif header['name'] == 'From':
                        email['from'] = header['value']
                    elif header['name'] == 'Date':
                        email['date'] = header['value']

                emails.append(email)

            return emails

        except Exception as e:
            print(f"Failed to get emails: {e}")
            return []

    def get_today_events(self) -> List[Dict[str, Any]]:
        """Get today's calendar events"""
        try:
            now = datetime.datetime.utcnow()
            today_start = datetime.datetime(now.year, now.month, now.day).isoformat() + 'Z'
            today_end = datetime.datetime(now.year, now.month, now.day, 23, 59, 59).isoformat() + 'Z'

            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=today_start,
                timeMax=today_end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return [{
                'id': event['id'],
                'summary': event['summary'],
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'description': event.get('description', '')
            } for event in events]

        except Exception as e:
            print(f"Failed to get calendar events: {e}")
            return []

    def get_upcoming_events(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get upcoming events within specified minutes"""
        try:
            now = datetime.datetime.utcnow()
            future = now + datetime.timedelta(minutes=minutes)

            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=future.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return [{
                'id': event['id'],
                'summary': event['summary'],
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'description': event.get('description', '')
            } for event in events]

        except Exception as e:
            print(f"Failed to get upcoming events: {e}")
            return []

    def create_event(self, summary: str, start_time: str, end_time: str,
                    description: str = "") -> Dict[str, Any]:
        """Create a calendar event"""
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                }
            }

            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return {
                'status': 'success',
                'event_id': created_event['id'],
                'html_link': created_event.get('htmlLink')
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}