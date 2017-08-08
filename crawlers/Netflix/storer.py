from crawlers.Netflix.parser import Parser
import json

from pprint import pprint


class Storer(object):
    def __init__(self):
        self.name = 'db'

    @staticmethod
    def write_profiles_to_file(profile_name=None):
        """
        If profile_name is not specified then write all profiles' viewing activity to file.
        Otherwise write specific profile's viewing activity to file.
        :param profile_name:
        :return:
        """
        p = Parser()
        if profile_name and profile_name not in p.driver.user_profiles:
            raise Exception("This profile name does not exist")
        if profile_name:
            data = p.parse_viewing_activity_by_profile(profile_name)
            file_name = './data/{0}_viewing_activity.txt'.format(profile_name)
        else:
            data = p.parse_all_profiles_viewing_activity()
            file_name = './data/all_viewing_activity.txt'

        with open(file_name, 'w') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)

        p.driver.quit()

    @staticmethod
    def read_from_file(file_name):
        file_name = './data/{0}'.format(file_name)
        with open(file_name, 'r') as json_file:
            data = json.load(json_file)

        return data


if __name__ == '__main__':
    # Storer.write_profiles_to_file()
    # Storer.write_profiles_to_file('Nomadic')
    Storer.write_profiles_to_file()



