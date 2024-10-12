# AI News Digest Generator

This project automatically fetches recent tech and AI news from your Gmail, summarizes the content using OpenAI's GPT-4, and sends a digest email. It's designed to be deployed on Render.

## Prerequisites

- A Gmail account
- Google Cloud Platform account
- OpenAI API key
- Render account

## Setup

1. **Google Cloud Platform Setup**
   - Create a new project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API for your project
   - Create OAuth 2.0 credentials (Client ID and Client Secret)

2. **OpenAI API Key**
   - Obtain an API key from [OpenAI](https://openai.com/api/)

3. **Environment Variables**
   Set up the following environment variables:
   - `GOOGLE_CLIENT_ID`: Your Google OAuth 2.0 client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth 2.0 client secret
   - `GOOGLE_REFRESH_TOKEN`: (You'll get this after running the script locally once)
   - `NEWSLETTER_GMAIL_LABEL`: The Gmail label for newsletters (e.g., "Newsletters")
   - `NEWSLETTER_DIGEST_OPENAI_API_KEY`: Your OpenAI API key
   - `SENDER_EMAIL`: The email address to send the digest from (must be your Gmail address)

4. **Local Setup**
   - Clone this repository
   - Install dependencies: `pip install -r requirements.txt`
   - Run the script locally once to obtain the `GOOGLE_REFRESH_TOKEN`:
     ```
     python main.py
     ```
   - Follow the OAuth flow in your browser and authorize the application
   - Copy the displayed refresh token and set it as the `GOOGLE_REFRESH_TOKEN` environment variable

## Deployment on Render

1. Create a new cron job on Render
2. Connect your GitHub repository
3. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. Add all the environment variables mentioned above
5. Deploy the job

## Usage

Once deployed, Render will run the script according to your configuration (e.g., daily). The script will:

1. Fetch recent emails with the specified label
2. Summarize the content using GPT-4o
3. Send a digest email to the specified address
4. Mark processed emails as read

## Customization

- Adjust the `SCOPES` in `main.py` if you need different Gmail API permissions
- Modify the `summarize_content` function to change the summarization prompt or model

## TODO

- Implement audio file generation and podcast posting functionality

## License

[MIT License](LICENSE)