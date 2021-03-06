"""Slack bot that notifies a channel when a new article is posted to a blog."""

import time
import json
import os.path

import feedparser
import requests

from private import WEBHOOK
from config import FEEDS


def notify_article(hook_url, title, site, link):
    message = '<!channel>: *{title}* @ {site}\n'\
              '<{link}>'.format(title=title, site=site, link=link)
    # We can make our message more pretty by adding JSON keys.
    json_obj = {'text': message, 'username': 'Blog Notifier',
                'icon_emoji': ':swift:'}
    # We should say that we're using JSON.
    headers = {'Content-type': 'application/json'}
    requests.post(hook_url, data=json.dumps(json_obj), headers=headers)


class BlogNotifier(object):
    """Blog notifier POSTS to Slack webhook when a feed is updated."""

    def __init__(self, feed_urls, hook_url, statefile='state.json'):
        self._urls = feed_urls
        self._hook_url = hook_url
        self._statefile = statefile
        if not os.path.isfile(statefile):
            feeds = [feedparser.parse(f) for f in feed_urls]
            self._latests = [f.entries[0].published_parsed for f in feeds]
            self.write_state()
        else:
            self.read_state()
            self.update()

    def update(self):
        """Run periodically to check for updates and POST them to Slack."""
        for i, (url, latest) in enumerate(zip(self._urls, self._latests)):
            feed = feedparser.parse(url)

            # Skip feeds that are empty.
            if len(feed.entries) <= 0:
                continue

            new_latest = feed.entries[0].published_parsed
            if new_latest > latest:
                # Don't repeatedly notify ;)
                self._latests[i] = new_latest
                notify_article(self._hook_url, feed.entries[0].title,
                               feed.feed.title, feed.entries[0].link)
        self.write_state()

    def write_state(self):
        d = {url: latest for url, latest in zip(self._urls, self._latests)}
        with open(self._statefile, 'w') as f:
            json.dump(d, f)

    def read_state(self):
        with open(self._statefile, 'r') as f:
            d = json.load(f)
        self._latests = []
        for url in self._urls:
            if url in d:
                self._latests.append(time.struct_time(d[url]))
            else:
                # feedparser uses UTC/GMT for all times
                self._latests.append(time.gmtime())

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
