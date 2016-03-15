"""Slack bot that notifies a channel when a new article is posted to a blog."""

import time
import json

import feedparser
import requests

from private import WEBHOOK
from config import FEEDS


class BlogNotifier(object):
    """Blog notifier POSTS to Slack webhook when a feed is updated."""

    def __init__(self, feed_urls, hook_url):
        self._urls = feed_urls
        feeds = [feedparser.parse(f) for f in feed_urls]
        self._latests = [f.entries[0].published_parsed for f in feeds]
        self._hook_url = hook_url

    def update(self):
        """Run periodically to check for updates and POST them to Slack."""
        for i, (url, latest) in enumerate(zip(self._urls, self._latests)):
            feed = feedparser.parse(url)

            # Skip feeds that are empty.
            if len(feed.entries) <= 0:
                continue

            new_latest = feed.entries[0].published_parsed
            if new_latest > latest:
                # Record the new latest publication date.
                self._latests[i] = new_latest
                # This is roughly Slack formatting.  Should be good enough.
                message = '<!channel>: *{title}* @ {site}\n'\
                          '<{link}>'.format(site=feed.feed.title,
                                            **feed.entries[0])
                # We can make our message more pretty by adding JSON keys.
                json_obj = {'text': message, 'username': 'Blog Notifier',
                            'icon_emoji': ':swift:'}
                # We should say that we're using JSON.
                headers = {'Content-type': 'application/json'}
                requests.post(self._hook_url, data=json.dumps(json_obj),
                              headers=headers)

    def run_forever(self, delay):
        """Does what it sounds like.... runs forever."""
        while True:
            # Update first so we know whether or not the update code is working
            # :)
            self.update()
            time.sleep(delay)


if __name__ == '__main__':
    notifier = BlogNotifier(FEEDS, WEBHOOK)
    notifier.run_forever(15 * 60)
