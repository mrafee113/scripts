#!/usr/bin/env python3

"""
this repo (https://github.com/lucahammer/tweetXer) can be used to delete twitter user data.
 it relies on tweets.js, tweet-header.js and likes.js files of the downloaded twitter archive.

this script is used to manipulate the contents of those files so that there's some sense of 
 control over what will be deleted.
"""

import json


def tweets_js(filepath: str):
    with open(filepath) as file:
        data = file.read()
    
    data = data[data.find('['):]
    data: list[dict] = json.loads(data)
    date.sort(key=lambda x: datetime.strptime(x['tweet']['created_at'], '%a %b %d %H:%M:%S %z %Y'))

    highly_liked = set()
    pinterest = set()
    replies = set()
    self_replies = set()
    quotes = set()
    spotify = set()
    youtube = set()
    videos = set()
    photos = set()
    english = set()
    old = set()
    no_text = set()
    for ndx, t in enumerate(data):
        if int(t['tweet']['favorite_count']) >= 8:
            highly_liked.add(ndx)
        if 'daily dose of pinterest' in t['tweet']['full_text'].lower():
            pinterest.add(ndx)
        if 'in_reply_to_user_id_str' in t['tweet']:
            replies.add(ndx)
        if 'in_reply_to_screen_name' in t['tweet'] and 'francis' in t['tweet']['in_reply_to_screen_name']:
            self_replies.add(ndx)
        if t['tweet']['entities']['user_mentions'] and t['tweet']['full_text'].startswith('RT '):
            retweets.add(ndx)
        for url in t['tweet']['entities']['urls']:
            if 'expanded_url' in url and url['expanded_url'].startswith('https://twitter.com'):
                quotes.add(ndx)
            if 'expanded_url' in url and url['expanded_url'].startswith('https://open.spotify.com'):
                spotify.add(ndx)
            if 'expanded_url' in url and 'youtu' in url['expanded_url']:
                youtube.add(ndx)
        if 'media' in t['tweet']['entities']:
            for media in t['tweet']['entities']['media']:
                if 'expanded_url' in media and 'video' in media['expanded_url']:
                    videos.add(ndx)
                if 'expanded_url' in media and 'photo' in media['expanded_url'] and t['tweet']['lang'] != 'fa':
                    photos.add(ndx)
        if t['tweet']['lang'] == 'en':
            english.add(ndx)
        if t['tweet']['lang'] == 'zxx':
            no_text.add(ndx)
        if datetime.strptime(t['tweet']['created_at'], '%a %b %d %H:%M:%S %z %Y') < datetime.strptime('Feb 27 +0000 2024', '%b %d %z %Y'):
            old.add(ndx)
        
    to_remove = set(range(len(data)))
    other_replies = replies - self_replies
    for ndx in range(len(data)):
        if ndx in english and ndx not in quotes and ndx not in replies and ndx not in old:
            to_remove.discard(ndx)
        if ndx in videos  and ndx not in old    and ndx not in other_replies:
            to_remove.discard(ndx)
        if ndx in photos  and ndx not in old    and (ndx in english or ndx in no_text) and ndx not in other_replies:
            to_remove.discard(ndx)
        if ndx in youtube and ndx not in old    and ndx not in other_replies:
            to_remove.discard(ndx)
        if ndx in spotify and ndx not in old    and ndx not in other_replies:
            to_remove.discard(ndx)
        if ndx in pinterest:
            to_remove.discard(ndx)
        if ndx in highly_liked:
            to_remove.discard(ndx)

def main():
    pass
