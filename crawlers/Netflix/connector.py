import requests
import os
from crawlers.Netflix.storer import Storer
from pprint import pprint


def year_match(query, year):
    return abs(year - query) <= 1


def title_match(result, criteria):
    criteria = criteria.lower()
    title = result['title'].lower()
    original_title = result['original_title'].lower()
    alternate_titles = [title.lower() for title in result['alternate_titles']]

    if title == criteria or original_title == criteria or criteria in alternate_titles:
        return True
    else:
        return False


def spoke_search(term):
    r = requests.get('http://api.dev.thespoke.co/search?type=1&query=' + term)
    results = r.json()['content']['results']
    return results


def manual_search():
    title = input('\nPlease enter a title: ')
    results = spoke_search(title)
    movie = manual_match(title, results)
    return movie


def manual_match(term, results):
    message = '\n' + str(len(results)) + ' search results for "' + term + '"\n'
    print(message)
    i = 1
    for result in results:
        print(str(i) + ' - ' + result['title'] + ' (' + str(result['release_year']) + ')')
        i += 1
    option = input('\nType item number or "search"/"skip": ')
    if option == 'search':
        manual_search()
    if option == 'skip':
        return None
    elif option.isdigit() and int(option) <= len(results) and int(option) > 0:
        return results[int(option) - 1]
    else:
        manual_match(term, results)


def find_movie(movie):
    title = movie['Title']
    year = movie['Year']

    results = spoke_search(title)
    for result in results:
        if title_match(result, title) and year_match(result['release_year'], year):
            return result

    # duplicate above for parenthetical_title

    if len(results) == 0:
        option = ''
        os.system('cls' if os.name == 'nt' else 'clear')
        while (option.lower() != 'search') and (option.lower() != 'skip'):
            option = input('\nThere were no results for ' + movie[
                'full_title'] + ' [' + year + ']. \n\nType "search" or "skip": ').lower()
        if option == 'search':
            return manual_search()
        if option == 'skip':
            return None
    else:
        return manual_match(title, results)


def process_list(list_items, collection_id):
    for list_item in list_items.values():
        movie = find_movie(list_item)
        if movie is not None:
            add_item(movie['id'], collection_id)
            # print(movie['title'] + ' (' + str(movie['release_year']) + ')')


def login(username, password):
    url = "http://api.dev.thespoke.co/rest-auth/login/"
    data = "{\"username\": \"" + username + "\",    \"password\": \"" + password + "\"}"
    headers = {'content-type': "application/json"}
    r = requests.request("POST", url, data=data, headers=headers)
    return r.json()['key']


def create_list(name, description, key):
    url = "http://api.dev.thespoke.co/collections/"
    data = "{\"title\": \"" + name + "\",    \"description\": \"" + description + "\",    \"item_type\": \"MO\"}"
    headers = {'content-type': "application/json", 'Authorization': "Token " + key}
    r = requests.request("POST", url, data=data, headers=headers)
    return r.json()['id']


def add_item(item_id, collection_id):
    url = "http://api.dev.thespoke.co/items/"
    data = "{\"external_id\": " + str(item_id) + ",    \"collection_id\": " + str(collection_id) + "}"
    headers = {'content-type': "application/json", 'Authorization': "Token " + key}
    r = requests.request("POST", url, data=data, headers=headers)
    if r.status_code != 201:
        print(r.status_code)
        print(r.json())
        input("hit enter")
    return r.json()


if __name__ == "__main__":
    username = input('username: ')
    password = input('password: ')

    name = 'Test'
    description = 'Nomadic\'s Netflix Viewing Activity'
    key = login(username, password)
    storer = Storer()

    collection_id = create_list(name, description, key)
    list_items = storer.read_from_file('Nomadic_viewing_activity.txt')
    process_list(list_items=list_items, collection_id=collection_id)
