# Can get complete ball by ball season data for every match of IPL one season at a time from espn
import json
import requests
from concurrent.futures import ThreadPoolExecutor
import csv


# gets the usl for both innings for each match for any given season
def url_getter():
    match_id = int(input('what is the first match number u want data for:   '))
    # test match_id = 335982
    match_id_last = int(input('what is the last match number u want data for:   '))
    # test match_id_last = 336040
    series_id = int(input('what is the series number of the season u want data for:   '))
    # test series_id = 313494
    url_list1 = []
    while match_id <= match_id_last:
        for i in range(1, 3):
            url = (f'https://hs-consumer-api.espncricinfo.com/v1/pages/match/comments?lang=en'
                   f'&seriesId={series_id}&matchId={match_id}&inningNumber={i}&commentType=ALL&sortDirection=DESC')
            url_list1.append(url)
        match_id += 1
    return url_list1


# # gets the individual links from lazy loading website by checking for every change in address on scrolling dow
def url_():
    ur_list = url_getter()
    url_list2 = []
    for first in ur_list:

        for j in range(2, 19, 2):
            url_next = first + '&fromInningOver=' + str(j)
            url_list2.append(url_next)
        url_list2.append(first)

    print(len(url_list2))   # test value
    return url_list2


# actual data scraped from the website
def fetch_url(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None

        else:
            print("Failed to fetch data. Status code:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None


# logic selection to get data as required in future this will be expanded to include a lot more functionality
def collect_data(data_list):
    runs_scored = {}
    for file in data_list:
        comments = file.get('comments', [])

        for comment in comments:
            batsman_id = comment.get('batsmanPlayerId')
            bowler_id = comment.get('bowlerPlayerId')
            runs = comment.get('batsmanRuns', 0)

            if batsman_id not in runs_scored:
                runs_scored[batsman_id] = {}

            if bowler_id not in runs_scored[batsman_id]:
                runs_scored[batsman_id][bowler_id] = 0

            runs_scored[batsman_id][bowler_id] += runs

    with open("runs_scored_data.csv", "w", newline='') as csvfile:
        fieldnames = ['BatsmanPlayerId', 'BowlerPlayerId', 'Runs']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for batsman_id, bowler_runs in runs_scored.items():
            for bowler_id, runs in bowler_runs.items():
                writer.writerow({'BatsmanPlayerId': batsman_id, 'BowlerPlayerId': bowler_id, 'Runs': runs})


if __name__ == "__main__":
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }

    url_list = url_()
    combined_data = []

    with ThreadPoolExecutor(max_workers=15) as executor:
        results = executor.map(fetch_url, url_list)
        for result in results:
            if result is not None:
                combined_data.append(result)
        successful_responses = len(combined_data)
        print("no. of success response:  ", successful_responses)

    collect_data(combined_data)
