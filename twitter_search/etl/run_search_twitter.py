"""
This script runs the Twitter search, data collection and filtering process.
"""

from pathlib import Path
from etl.data_collection.get_users import UserGetter
from etl.data_collection.get_lists import ListGetter
from etl.data_collection.search_users import UserSearcher
from twitter_filtering.users_filtering.users import UserFilter
from twitter_filtering.lists_filtering.filter_lists import ListFilter, ListReader
from etl.data_cleaning.clean_users import UserCleaner


def run_search_twitter(query, location):
    """
    Run Twitter search and data collection process.

    Args:
        query (str): The search query to search for Twitter users.
        location (str): The location to filter the search for Twitter users.

    Returns:
        str: A message indicating the completion of the data cleaning process.

    Raises:
        ValueError: If any of the input arguments are invalid.
    """
    count = 1

    while True:
        # Set up file paths with count
        dir = Path(__file__).parent.parent / "data/raw_data"
        output_file_search = dir / f"{location}_users_test.json"

        if count == 1:
            input_file_filter = output_file_search
        else:
            input_file_filter = dir / f"{location}_totalusers_{count-1}.json"

        output_file_filter = dir / f"{location}_users_filtered_{count}.json"
        input_file_lists = output_file_filter
        output_file_lists = dir / f"{location}_lists_{count}.json"
        input_file_total = output_file_lists
        output_file_total = dir / f"{location}_totalusers_{count}.json"

        print(f"Iteration {count}:")

        if count == 1:
            # Perform search only in the first iteration
            print("Searching for Twitter users...")
            search_twitter_users(location, query, output_file_search)

        # Filter users based on location
        print("Filtering Twitter users based on location...")
        filter_twitter_users(location, input_file_filter, output_file_filter)

        # Retrieve lists associated with filtered users
        print("Retrieving lists associated with filtered users...")
        retrieve_lists(location, input_file_lists, output_file_lists)

        # Filter lists
        filter_twitter_lists(location, input_file_filter, output_file_filter)

        # Retrieve user data from the retrieved lists
        print("Retrieving user data from lists...")
        retrieve_user_data(location, input_file_total, output_file_total)

        # Increment count for the next iteration
        count += 1

        # Check if additional iterations are needed
        if additional_iterations_needed(count):
            continue
        else:
            break

    return "Data collection and cleaning process completed."


def search_twitter_users(location, query, output_file_search):
    user_searcher = UserSearcher(location, output_file_search, query)
    user_searcher.run_search_all()


def filter_twitter_users(location, input_file_filter, output_file_filter):
    user_filter = UserFilter(location, input_file_filter, output_file_filter)
    user_filter.run_filtering()


def filter_twitter_lists(location, input_file_filter, output_file_filter):
    list_filter = ListFilter(location, input_file_filter, output_file_filter)

    list_reader = ListReader(input_file_filter)
    lists_df = list_reader.create_df()

    print("Filtering dataframe for relevant lists")
    list_filter = ListFilter(lists_df)
    relevant_lists = list_filter.keep_relevant_lists()

    new_filename = input_file_filter.replace(".json", "_filtered.json")
    relevant_lists.to_json(f"{new_filename}", orient="records")


def retrieve_lists(location, input_file_lists, output_file_lists):
    list_getter = ListGetter(location, input_file_lists, output_file_lists)
    list_getter.get_lists()


def retrieve_user_data(location, input_file_total, output_file_total):
    user_getter = UserGetter(location, input_file_total, output_file_total)
    user_getter.get_users()


def additional_iterations_needed(count):
    return count <= 2  # Example: Perform 2 iterations
