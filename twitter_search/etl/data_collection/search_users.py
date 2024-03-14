"""
Module for searching users on Twitter based on a query and location.

Author : praveenc@uchicago.edu/mahara1995@gmail.com
"""

from twitter_search.config_utils import util
from pathlib import Path

MAX_RESULTS = 50  
EXPANSIONS = ["author_id", "entities.mentions.username", "geo.place_id"]
TWEET_FIELDS = ['attachments', 'author_id', 'context_annotations', \
                'conversation_id', 'created_at', 'edit_controls', \
                    'entities', 'geo', 'id', 'in_reply_to_user_id', \
                        'lang', 'public_metrics', 'possibly_sensitive',\
                              'referenced_tweets', 'reply_settings', \
                                'source', 'text', 'withheld']
USER_FIELDS = ["created_at", 'description', 'entities', 'id', 'location',\
                'most_recent_tweet_id', 'name', 'pinned_tweet_id', \
                    'profile_image_url', 'protected', 'public_metrics',\
                          'url', 'username']


def search_tweets(client, query, MAX_RESULTS, EXPANSIONS, TWEET_FIELDS,\
                   USER_FIELDS):
    """
    Search for recent tweets based on a query.

    Args:
        client: An authenticated Twitter API client.
        query (str): The search query.
        MAX_RESULTS (int): Maximum number of results to retrieve.
        EXPANSIONS (list): List of expansions to include in the response.
        TWEET_FIELDS (list): List of tweet fields to include in the response.
        USER_FIELDS (list): List of user fields to include in the response.

    Returns:
        dict: The search result containing tweets and associated users.
    """
    return client.search_recent_tweets(query=query, max_results=MAX_RESULTS,
                                       expansions=EXPANSIONS,
                                       tweet_fields=TWEET_FIELDS,
                                       user_fields=USER_FIELDS)

def get_users_from_tweets(tweets):
    """
    Extract users from the tweet search result.

    Args:
        tweets (dict): The search result containing tweets and associated users.

    Returns:
        list: List of user objects.
    """
    return tweets.includes['users']

def search_users(query,location):
    """
    Search for users on Twitter based on a query and location.

    Args:
        query (str): The search query.
        location (str): The location for which to search users.

    Returns:
        None
    """

    try:
        output_dir = (Path(__file__).parent.parent.parent / 
                  "data/raw_data")
        output_file = output_dir / f"{location}_users.json"
        client = util.client_creator()
        print("Client initiated")
        print("Now searching for tweets")
        search_tweets_result = search_tweets(client, query, MAX_RESULTS, \
                                             EXPANSIONS, TWEET_FIELDS, \
                                                USER_FIELDS)
        total_users = get_users_from_tweets(search_tweets_result)
        total_users_dict = util.user_dictmaker(total_users)
        util.json_maker(output_file, total_users_dict)
        print("Total number of users:", len(total_users))
        
        return "done"
    except Exception as e:
        print(f"An error occurred: {e}")


