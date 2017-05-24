# HB_Info_Bot
This is a reddit bot that scans submissions on [/r/GameDeals](https://www.reddit.com/r/GameDeals/). If it finds a post linking to a HumbleBundle Game Bundle, it creates a game info table and comments on the submission.

## How to use 
1. Install python
2. Create a reddit app [here](https://www.reddit.com/prefs/apps)
3. Make a `config.py` file with necessary info. Here's an example:
```python
client_id='reddit_app_client_id'
client_secret='reddit_app_client_secret'
username='your_bot_username_here'
password='your_bot_password_here'
footer='Cool Catchphrase'
```
4. Run `humblebot.py`
  * Automate with a cron job, task scheduler, etc.
5. Celebrate

## Credits
[swiftyspiffy's SteamStoreQuery](https://github.com/swiftyspiffy/SteamStoreQuery)
