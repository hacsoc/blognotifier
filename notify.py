"""Sends a notification to the #blogs channel manually, easily."""

import sys

from blognotifier import notify_article
from private import WEBHOOK


def main():
    if len(sys.argv) != 4:
        print("Usage: python notify.py [title] [sitename] [link]")
        return

    notify_article(WEBHOOK, *sys.argv[1:])


if __name__ == '__main__':
    main()
