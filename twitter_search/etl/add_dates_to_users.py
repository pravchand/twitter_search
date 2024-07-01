"""
Reads the old JSONs and adds the corresponding dates from each tweet to 

"""

import os
import json
from argparse import ArgumentParser
from pathlib import Path

# df = pd.read_csv(
#     "twitter_search/data/cleaned_data/all_users.csv", encoding="utf-8-sig"
# )


# df_unique = df.drop_duplicates(subset=["user_id"])

# print(df_unique)


script_path = Path(__file__).resolve()
project_root = script_path.parents[1]


class DateAdder:
    # Construct the path to the cleaned_data directory
    RAW_DATA_PATH = project_root / "data" / "raw_data"
    CLEAN_DATA_PATH = project_root / "data" / "cleaned_data"

    def __init__(self, location):

        self.json_files = os.listdir(self.RAW_DATA_PATH)
        self.location = location
        self.date_digits = 10
        self.filter_json_files()

        self.file_type_column = {
            "user": "content_is_relevant",
            "list": "relevant",
        }

    def filter_json_files(self):
        """
        Filter the JSON files based on the location.

        Args:
            json_files (list): The list of JSON files.
            location (str): The location to filter on.

        Returns:
            list: The filtered JSON files.
        """
        # Filter the JSON files based on the location
        self.filtered_files = [
            file
            for file in self.json_files
            if self.location.lower() in file.lower()
        ]

        self.users_files = [
            filtered_file
            for filtered_file in self.filtered_files
            if "user" in filtered_file.lower()
            and "filtered" in filtered_file.lower()
        ]

        self.tweets_files = [
            filtered_file
            for filtered_file in self.filtered_files
            if "tweets" in filtered_file.lower()
        ]

        if not self.filtered_files:
            raise ValueError(f"No files found for location {self.location}")

    def add_date_to_users(self, tweets_dict, users_dict):
        """
        If there is a date associated to any tweet, add it to the user

        If the user does not have any tweet associated to her, the
        function adds a default datetime string
        """
        # Get authors and dates from the available tweets
        tweets_dict = self.remove_duplicate_records(tweets_dict)
        tweet_authors = [tweet["author_id"] for tweet in tweets_dict]
        tweet_dates = [tweet["created_at"] for tweet in tweets_dict]

        # Dictionary of dates and authors
        authors_dates_dict = dict(zip(tweet_authors, tweet_dates))

        # Add such date to the collected users
        for user_dict in users_dict:
            user_id = user_dict["user_id"]
            author_date = authors_dates_dict.get(user_id)

            if "tweet_date" in user_dict:
                if author_date:
                    # Just get 10 digits for year, month and day
                    user_dict["tweet_date"] = author_date[: self.date_digits]
            else:
                user_dict["tweet_date"] = None

            user_dict["user_date_id"] = f"{user_id}-{user_dict['tweet_date']}"

        return users_dict

    @staticmethod
    def load_json(file_path):
        """
        Loads a JSON file from the given path

        Reads the JSON file from the path and returns
        a dictionary
        """
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data

    @staticmethod
    def remove_duplicate_records(records):
        """
        Removes duplicate records, based on the new
        """

        unique_records = []
        seen_records = set()

        for record in records:
            if "user_date_id" in record:
                record_id = record["user_date_id"]

            elif "tweet_id" in record:
                record_id = record["tweet_id"]

            else:
                raise Exception(f"Record {record} should have date")

            if record_id not in seen_records:
                unique_records.append(record)
                seen_records.add(record_id)

        return unique_records

    def add_date_to_files(self):
        """
        Loops through each file and assigns a date to all the users, if available
        """
        self.final_users_list = []
        for tweets_file, users_file in zip(self.tweets_files, self.users_files):
            tweets_dict_list = self.load_json(
                f"{self.RAW_DATA_PATH}/{tweets_file}"
            )
            users_dict_list = self.load_json(
                f"{self.RAW_DATA_PATH}/{users_file}"
            )

            for tweets_dict, users_dict in zip(
                tweets_dict_list, users_dict_list
            ):
                users_dict = self.add_date_to_users(tweets_dict, users_dict)
                self.final_users_list.extend(users_dict)

        self.final_users_list = self.remove_duplicate_records(
            self.final_users_list
        )


if __name__ == "__main__":

    parser = ArgumentParser(
        description="Please add the location to parse the users"
    )
    parser.add_argument(
        "location", type=str, help="Location to parse the corresponding users"
    )

    args = parser.parse_args()

    date_adder = DateAdder(args.location)
    date_adder.add_date_to_files()

    print(len(date_adder.final_users_list))
