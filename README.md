## Setup
1. `pip install`
2. Copy `.env.example` to `.env`
3. Replace the placeholder values in `.env` with your actual information

The credentials.json file contains the OAuth 2.0 client credentials for your Google Cloud project. You don't create this file manually; instead, you download it from the Google Cloud Console. Here's how to obtain it:

1. Go to the Google Cloud Console.
2. Create a new project or select an existing one.
3. Enable the Gmail API for your project:
- In the sidebar, click on "APIs & Services" > "Library"
- Search for "Gmail API" and click on it
- Click "Enable"
4. Set up OAuth 2.0 credentials:
- In the sidebar, click on "APIs & Services" > "Credentials"
- Click "Create Credentials" and select "OAuth client ID"
- Choose "Desktop app" as the application type
- Give it a name (e.g., "Gmail API Client")
5. Download the credentials:
- After creating the OAuth client ID, you'll see a download button (looks like a download arrow)
- Click it to download the JSON file
- Rename this downloaded file to credentials.json
6. Place the credentials.json file in the same directory as your Python script.

Remember:
- Never share your credentials.json file or commit it to version control.
- The first time you run your script, it will use this file to start the OAuth flow.
- It will open a browser window asking you to log in to your Google account and grant permissions.
- After granting permissions, a token.json file will be created, which is used for subsequent authentications.
