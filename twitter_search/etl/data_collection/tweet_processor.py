from config_utils import util,constants


class TweetProcessor:
    def __init__(self, location, input_file_tuple, output_file):
        self.location = location
        self.gmaps_client = util.gmaps_client()
        self.input_file_tweets, self.input_file_users = input_file_tuple
        self.output_file = output_file

    @staticmethod
    def get_coordinates(client, location):
        """
        Get the latitude and longitude coordinates of a location.
        """
        if location is None:
            return (None, None)
        try:
            # Geocode the location using Google Maps Geocoding API
            geocode_result = client.geocode(location)

            # Check if any results were returned
            if geocode_result:
                lat = geocode_result[0]["geometry"]["location"]["lat"]
                lng = geocode_result[0]["geometry"]["location"]["lng"]
                return (lat, lng)
            else:
                return (None, None)

        except Exception as e:
            print(f"Error geocoding location '{location}': {e}")
            return (None, None)

    def process_tweets_for_users(self):
        """
        Adds tweets to each user's dictionary.

        Args:
            data: Response data containing tweets and users.

        Returns:
            None
        """
        for tweet in self.tweet_list:
            for annotation in tweet["context_annotations"]:
                domain_name = annotation["domain"]["name"]
                entity_name = annotation["entity"].get("name", "").lower()
                is_relevant = (domain_name == "Local News" or \
                               domain_name == "Journalist" or \
                                domain_name == "News") and \
                                (entity_name == constants.\
                                 STATE_CAPITALS[self.location] or \
                                    entity_name == self.location)
                
            author_id = tweet.get("author_id", None)
            if author_id:
                for user in self.user_list:
                    if user["user_id"] == author_id:
                        user["tweets"].append(tweet["text"])
                        try:
                            if is_relevant:
                                user['detected_loc'] = self.location
                                user['detected_cat'] = "News"
                        except:
                                user['detected_loc'] = ""
                                user['detected_cat'] = ""

    def geo_coder(self):
        """
        Runs the geocoding process for all users.
        """
        for user in self.user_list:
            user["geo_location"] = self.get_coordinates(
                self.gmaps_client, user["location"]
            )

    def store_users(self):
        """
        convert the user list to a json and store it.

        Args:
            None

        Returns:
            None
        """
        util.json_maker(self.output_file, self.user_list)
        print("Total number of users:", len(self.user_list))

    def run_processing(self):

        tweet_list_raw = util.load_json(self.input_file_tweets)
        user_list_raw = util.load_json(self.input_file_users)
        self.tweet_list = util.flatten_and_remove_empty(tweet_list_raw)
        self.user_list = util.flatten_and_remove_empty(user_list_raw)
        self.process_tweets_for_users()
        self.geo_coder()
        self.store_users()
