# fb-messenger-bot-v2
Messenger Bot for groups utilizing the fbchat api.


This script uses fbchat package for handling and sending requests from/to Facebook.


In order to use the script, you need a functioning Facebook account and access to Google Drive API - put the bot logging information in `bot_creds.json` file. 
The `drive_creds.json` file can be generated on the Google Cloud service when getting access to Google Drive API and generating OAuth 2.0 credentials.


The commands implemented at this time are as follows:

- 'Bot help' - lists all the comments
- 'Bot tag' - tags all of the group members
- 'Bot link' - sends a link to google drive
- 'Bot meme' - sends a random img from the drive folder

The script can be started with arguments: '-nl' for no google cloud logging and '-ng' for no greeting in the fb groups on bot startup.
