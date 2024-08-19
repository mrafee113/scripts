import json

def load_tweets(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def build_reply_tree(tweets):
    tweet_dict = {}
    reply_tree = {}

    for tweet_entry in tweets:
        tweet = tweet_entry['tweet']
        tweet_id = tweet['id_str']
        in_reply_to_id = tweet['in_reply_to_status_id_str']

        tweet_dict[tweet_id] = tweet

        if in_reply_to_id:
            if in_reply_to_id not in reply_tree:
                reply_tree[in_reply_to_id] = []
            reply_tree[in_reply_to_id].append(tweet_id)

    return tweet_dict, reply_tree

def traverse_replies(tweet_id, reply_tree, tweet_dict):
    stack = [tweet_id]
    result = []

    while stack:
        current_id = stack.pop()
        if current_id in tweet_dict:
            result.append(tweet_dict[current_id])
        if current_id in reply_tree:
            stack.extend(reply_tree[current_id])

    return result

if __name__ == "__main__":
    # Load tweets from file
    tweets = load_tweets('tweets.js')

    # Build the tweet dictionary and reply tree
    tweet_dict, reply_tree = build_reply_tree(tweets)

    # Specify the tweet ID to start the traversal
    start_tweet_id = '1773254809983885580'  # Replace with your tweet ID

    # Traverse the replies starting from the specified tweet ID
    replies = traverse_replies(start_tweet_id, reply_tree, tweet_dict)

    # Print the result
    for reply in replies:
        print(json.dumps(reply, indent=2))
