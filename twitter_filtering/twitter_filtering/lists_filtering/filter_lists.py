"""
This script does the initial filtering process for the twitter
lists
"""

# Global imports

import json
import pandas as pd

from twitter_filtering.utils.constants import PATH, LISTS_KEYWORDS, COLS_TO_KEEP

# Constants


# Functions and pipeline


class ListReader:

    PATH = PATH
    LISTS_KEYWORDS = LISTS_KEYWORDS
    COLS_TO_KEEP = COLS_TO_KEEP

    def __init__(self) -> None:
        pass

    def read_json(self):
        """
        Reads JSON file and returns a dictionary

        Args:
            file_path (str): Path to the JSON file
        Returns:
            data (dict): Dictionary with the JSON data
        """
        with open(self.PATH, "r") as file:
            data = json.load(file)
        self.twitter_lists = data

    def parse_into_df(self):
        """
        Creates a DataFrame from the JSON data

        Args:
            lists (list): List of dictionaries with the JSON data
        Returns:
            df (pd.DataFrame): DataFrame with the JSON data
        """

        self.lists_df = pd.DataFrame([])

        for twitter_list in self.twitter_lists:
            if not twitter_list:
                # remove entry if empty
                continue

            else:
                # create a dataframe from the list
                list_df = pd.DataFrame(twitter_list)
                self.lists_df = pd.concat([self.lists_df, list_df], ignore_index=True)

        self.lists_df = self.lists_df.loc[:, COLS_TO_KEEP].copy()

    def create_df(self):
        """
        Performs the complete pipeline to get dataframe of lists
        """
        self.read_json(f"{PATH}/Mumbai_lists.json")
        self.parse_into_df()
        self.lists_df.drop_duplicates(subset=["list_id"], inplace=True)

        return self.lists_df


class ListFilter:
    """
    Class to filter lists based on keywords
    """

    def __init__(self, df) -> None:
        self.df = df

    @staticmethod
    def clean_text(text):
        """
        Cleans text from special characters

        Args:
            text (str): Text to be cleaned
        Returns:
            text (str): Cleaned text
        """
        # remove special characters
        text = text.lower()

        return text

    @staticmethod
    def filter_text(text):
        """
        Determines if the text contains a keyword
        of interest
        """
        text = text.lower()
        text_list = text.strip().split()

        for keyword in LISTS_KEYWORDS:
            if keyword in text_list:
                return True

        return False

    def is_relevant(self, row):
        """
        Creates an additional column to determine if the
        list is relevant or not
        """

        relevant_name = self.filter_text(row["name"])

        # If name is not relevant, check description
        if not relevant_name:
            # If description is not relevant, return False
            relevant_description = self.filter_text(row["description"])
            return relevant_description

        # If name is relevant, return True
        else:
            return relevant_name


if __name__ == "__main__":

    print("Reading JSON to create Lists dataframe...")
    print(f"Reading {PATH}")
    list_reader = ListReader()
    lists_df = list_reader.create_df()

    print("Filtering dataframe for relevant lists")
    list_filter = ListFilter(lists_df)
    lists_df["relevant"] = lists_df.apply(list_filter.is_relevant, axis=1)
    relevant_lists = lists_df.loc[lists_df["relevant"].isin([True]), :]
    print("Done!")
