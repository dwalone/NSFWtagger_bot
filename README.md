# NSFW tagger bot for image submissions to automate moderation

This bot uses a neural net to flair/remove new image submissions to subreddits as NSFW or not to automate moderation.

## Installation

Clone repo with `git clone https://github.com/dwalone/NSFWtagger_bot.git`

Install dependencies with `pip install -r requirements.txt`

(You may have to also run `pip install --upgrade nudenet` to install further dependencies)

### Usage

Create new Reddit user and make it a moderator of your subreddit(s), or use an existing moderator user.

Create an app for the user (https://www.reddit.com/prefs/apps/)

Enter the Authentication info `client id, client secret, username, password` into `keys.py`

Edit configuration options in `config.py`

Run `classify_nsfw_SubredditStream.py` to start streaming and moderating image submissions from your subreddit(s)!
