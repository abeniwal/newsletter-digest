import os
import datetime
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials # type: ignore
from googleapiclient.discovery import build # type: ignore
from google.auth.transport.requests import Request # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow # type: ignore
from openai import OpenAI # type: ignore

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_credentials():
    creds = None
    if os.getenv('GOOGLE_REFRESH_TOKEN'):
        creds = Credentials.from_authorized_user_info({
            'refresh_token': os.getenv('GOOGLE_REFRESH_TOKEN'),
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET')
        }, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                SCOPES
            )
            creds = flow.run_local_server(port=0)
            print(f'Refresh token: {creds.refresh_token}')
            print('Please save this refresh token as an environment variable named GOOGLE_REFRESH_TOKEN')
    
    return creds

def get_recent_emails(service):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    query = f'label:{os.getenv('NEWSLETTER_GMAIL_LABEL')} after:{yesterday.strftime("%Y/%m/%d")}'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages

def mark_emails_as_read(service, message_ids):
    for msg_id in message_ids:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

def get_email_content(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    if 'parts' in payload:
        parts = payload['parts']
        data = parts[0]['body']['data']
    else:
        data = payload['body']['data']
    data = data.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)
    return decoded_data.decode()

def summarize_content(content):
    client = OpenAI(api_key=os.getenv('NEWSLETTER_DIGEST_OPENAI_API_KEY'))
    prompt = f"""
    Given the following newsletter emails from various providers, consolidate all of that content into one digest of the day's most important tech and AI news.
    Pull together all the content across the emails about a specific news story and include it alongside the header so the reader can read this email and get as
    complete a picture of the news story as possible. At the end of each section of news, please include relevant links from the source content alone to explore/learn more.
    Do not make up links, only use links from the content provided. Generate the response in the format of a beautiful but simple HTML email.
    
    ONLY RETURN THE HTML CONTENT, DO NOT INCLUDE THE MARKDOWN (eg: "```html"). DO NOT INCLUDE ANY FAKE UNSUBSCRIBE LINKS. DO NOT INCLUDE ANY FAKE COPYRIGHTS OR ANYTHING IN THE FOOTER.
    
    This report is intended for industry experts who have been consistently following the market. Therefore, it should adhere to the following guidelines: 

    - No Fluff or Generic Statements: The report should contain only precise, relevant, and insightful information. 
    - Assume Reader Expertise: The report should assume that the reader has a strong background in technology and AI, so avoid explaining basic concepts or providing obvious, generic statements.
    - Avoid Repetition: Ensure that information is not repeated across sections; each piece of data or insight should be unique to its section. The content below might have the same news multiple times. Please consolidate overlapping news articles into one piece of news.

    {content}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a highly knowledgeable AI assistant specializing in summarizing tech and AI news."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def send_email(service, to, subject, body):
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['subject'] = subject
    
    html_content = MIMEText(body, 'html')
    message.attach(html_content)
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()

def main():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    messages = get_recent_emails(service)
    
    all_content = ""
    for message in messages:
        content = get_email_content(service, message['id'])
        all_content += content + "\n\n"

    summary = summarize_content(all_content)

    send_email(service, os.getenv('SENDER_EMAIL'), "Tech and AI News Digest", summary)

    # Get the IDs of the messages we processed
    processed_message_ids = [message['id'] for message in messages]

    # Mark the processed emails as read
    mark_emails_as_read(service, processed_message_ids)

    # TODO: Implement audio file generation and podcast posting

if __name__ == '__main__':
    main()

