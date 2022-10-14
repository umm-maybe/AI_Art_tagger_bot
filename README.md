# AI tagger bot for image submissions to automate moderation

This bot uses a neural net to flair/remove new image submissions to subreddits as AI-generated or not to automate moderation.

## Installation

Clone repo with `git clone https://github.com/umm-maybe/AI_Art_tagger_bot.git`

Install dependencies with `pip install -r requirements.txt`

### Usage

Create new Reddit user and create an app for the user (https://www.reddit.com/prefs/apps/).

Optionally, make it a moderator of your subreddit(s), or use an existing moderator user.

Enter the Authentication info `client id, client secret, username, password` into `keys.py`

Edit configuration options in `config.py`

Run `classify_AI_SubredditStream.py` to start streaming and moderating image submissions from your subreddit(s)!
