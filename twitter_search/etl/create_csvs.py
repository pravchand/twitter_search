"""
This script converts the JSON files into CSV files for easier data manipulation.
"""

# General imports
import pandas as pd
import json
import os
from pathlib import Path


# Lists_filtering constants

script_path = Path(__file__).resolve()
project_root = script_path.parents[1]

# Construct the path to the cleaned_data directory
RAW_DATA_PATH = project_root / "data" / "raw_data"
CLEAN_DATA_PATH = project_root / "data" / "cleaned_data"


def filter_json_files(json_files, location):
    """
    Filter the JSON files based on the location.

    Args:
        json_files (list): The list of JSON files.
        location (str): The location to filter on.

    Returns:
        list: The filtered JSON files.
    """
    # Filter the JSON files based on the location
    filtered_files = [
        file for file in json_files if location.lower() in file.lower()
    ]

    return filtered_files


def convert_to_csv(input_file):
    """
    Convert JSON files into CSV files.

    Args:
        input_file (str): The input JSON file.
        output_file (str): The output CSV file.

    Returns:
        None
    """
    # Load the JSON file
    with open(input_file, "r") as json_file:
        data = json.load(json_file)

    # Convert the JSON data into a DataFrame

    # If nested list

    if isinstance(data[0], list):
        df = pd.DataFrame(data[0])

    else:
        df = pd.DataFrame(data)

    # # Save the DataFrame as a CSV file
    # df.to_csv(output_file, index=False)

    return df


if __name__ == "__main__":

    # See which JSON files are available
    json_files = os.listdir(RAW_DATA_PATH)

    # Filter the JSON files based on the location
    location = "Mumbai"

    filtered_files = filter_json_files(json_files, location)

    user_files = [file for file in filtered_files if "users" in file]
    list_files = [file for file in filtered_files if "lists" in file]

    for user_file in user_files:
        input_file = RAW_DATA_PATH / user_file
        df = convert_to_csv(input_file)
        print(df.head())
        # output_file = CLEAN_DATA_PATH / user_file.replace(".json", ".csv")
        # convert_to_csv(input_file, output_file)