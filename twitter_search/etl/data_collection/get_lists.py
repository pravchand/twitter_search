import time
from datetime import datetime
from pathlib import Path

from config_utils import util
from config_utils.constants import MAX_RESULTS, COUNT_THRESHOLD


class ListGetter:
    """
    This class is in charge of parsing all of the lists of the twitter users
    """

    MAX_RESULTS = MAX_RESULTS
    COUNT_THRESHOLD = COUNT_THRESHOLD

    def __init__(self, location):
        self.location = location

    def getlists_fromusers(self, client, users_list, output_file, k=None):
        """
        Get lists from users.

        Parameters
        ----------
        client : tweepy.Client
            An authenticated Twitter API client.
        users_list : _type_
            _description_
        output_file : _type_
            _description_
        k : _type_, optional
            _description_, by default None
        """
        if k is None:
            k = len(users_list) - 1
        count = 0
        for user in users_list[:k]:
            response_user_list = client.get_list_memberships(
                id=user["user_id"],
                list_fields=util.LIST_FIELDS,
                max_results=self.MAX_RESULTS,
            )
            only_lists = self.isolate_lists(response_user_list)
            # Append data to the JSON file for each user
            list_entries = util.list_dictmaker({user["user_id"]: only_lists})
            util.json_maker(output_file, list_entries)
            # except Exception as e:
            #     print(f"Incomplete, currently at user {count}. Error: {e}")
            count += 1
            if count > self.COUNT_THRESHOLD:
                print("You have to wait for 15 mins")
                time_block = 1
                while time_block <= 3:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    time.sleep(300)
                    print(f"{current_time} - {time_block * 5} minutes done out of 15")
                    time_block += 1
                count = 0
            time.sleep(1)
            # TODO
            # client = util.client_creator()

    def isolate_lists(self, uncleaned_list):
        """
        TODO: Add docstring
        """
        isolated_lists = []
        for sublist in uncleaned_list:
            if sublist[0].id:
                print(sublist[0].id)
                if sublist not in isolated_lists:
                    isolated_lists += sublist

        return isolated_lists

    def get_lists(self):
        """
        Reads lists of users from a JSON file, parses them
        and returns them.
        """
        try:
            dir = Path(__file__).parent.parent.parent / "data/raw_data"
            output_file = dir / f"{self.location}_lists.json"
            input_file = dir / f"{self.location}_users.json"

            client = util.client_creator()
            users_list = util.load_json(input_file)
            isolated_lists = util.flatten_and_remove_empty(users_list)
            print("Now obtaining lists that the users are a part of: ", isolated_lists)
            self.getlists_fromusers(client, isolated_lists, output_file)
            # cleaned_lists = isolate_lists(all_lists)
            # list_dicts = util.list_dictmaker(all_lists)

            # util.json_maker_lists(output_file,list_dicts)

        except Exception as e:
            print(f"An error occurred: {e}")
