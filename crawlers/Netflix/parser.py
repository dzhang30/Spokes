from bs4 import BeautifulSoup
from crawlers.Netflix.driver import Driver
import re
import requests
import json
from pprint import pprint

LOGIN_URL = 'https://www.netflix.com/login'
VIEWING_ACTIVITY = 'https://www.netflix.com/viewingactivity'


class Parser(object):
    def __init__(self):
        self.driver = Driver()
        self.viewing_activity_url = VIEWING_ACTIVITY

    def parse_all_profiles_viewing_activity(self):
        results = {}
        profile_names = self.driver.user_profiles
        for profile_name in profile_names:
            viewing_activity = self.parse_viewing_activity_by_profile(profile_name)
            results[profile_name] = viewing_activity

        return results

    def parse_viewing_activity_by_profile(self, name):
        if self.driver.current_url != self.viewing_activity_url:
            self.driver.get(self.viewing_activity_url)

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        current_profile_name = soup.find("span", "name").getText()

        if name != current_profile_name:
            # the profile we are looking for is in the drop down list
            self.driver.switch_profile(name)

        self.driver.scroll_to_end(self.viewing_activity_url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        shows = {}
        title_ids = [title for title in soup.find_all("a")]
        for title_id in title_ids:
            if '/title/' in str(title_id):
                title_name = title_id.getText()
                shows[title_id["href"][7:]] = {
                    "Title": title_name,
                    "Year": '',
                    "Type": '',
                    "User Rating": ''
                }
        self.get_movie_type_and_year(shows)

        return shows

    @staticmethod
    def get_movie_type_and_year(shows):
        paths = []
        for title_id in shows.keys():
            paths.append(["videos", title_id, ["title", "summary", "userRating", "releaseYear"]])

        print('Find Cookie in Chrome Dev Tools -> Network Tab -> XHR -> Request Header in https://www.netflix.com/api/shakti/a86e250d/pathEvaluator?withSize=true&materialize=true&model=harris&method=call')
        cookie = input("Cookie: ")
        print("Find authURL in Chrome Dev Tools -> Network Tab -> XHR -> Request Payload in https://www.netflix.com/api/shakti/a86e250d/pathEvaluator?withSize=true&materialize=true&model=harris&method=call")
        auth_url = input("authURL: ")

        header = {
            'Cookie': cookie,
            'Content-Type': 'application/json'
        }

        data = {
            "paths": paths,
            "authURL": auth_url
        }

        s = requests.post(
            url='https://www.netflix.com/api/shakti/0965f1e8/pathEvaluator?withSize=true&materialize=true&model=harris',
            headers=header,
            json=data
        )

        result_json = json.loads(s.text)
        videos = result_json['value']['videos']
        videos.__delitem__('size')
        videos.__delitem__('$size')
        for k,v in videos.items():
            curr_vid_id = str(v['summary']['id'])
            if v['summary']['type'] == 'movie':
                shows[curr_vid_id]["Type"] = v['summary']['type']
                shows[curr_vid_id]["Year"] = v['releaseYear']
                shows[curr_vid_id]["User Rating"] = v['userRating']['userRating']
            else:
                shows.__delitem__(curr_vid_id)

    @staticmethod
    def is_movie(title):
        regex1 = re.compile(r"Season [0-9]*:")
        regex2 = re.compile(r"Collection [0-9]*:")
        if regex1.search(title) or regex2.search(title):
            return False
        return True

if __name__ == "__main__":
    print('parser')
    # parser = Parser()
    # r = parser.parse_all_profiles_viewing_activity()
    # pprint(r)
    # parser.driver.quit()
