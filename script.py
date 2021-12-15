import argparse
import csv
import logging
import os
import pandas as pd
import random
import requests
import time


class Reddit:
    def __init__(self):
        self._args = self._cmd()
        self._log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s", datefmt='%d.%m.%Y %H:%M:%S')

    def _cmd(self):
        now = int(time.time())
        parser = argparse.ArgumentParser(description="Python script to fetch reddit data!")
        parser.add_argument("-s", "--subreddit", type=str, default="wallstreetbets", help="define subreddit") #r/IndiaInvestments/,r/stocks,r/pennystocks, r/investing,r/stock_picks, r/stockmarket, r/wallstreetbets etc.
        parser.add_argument("-q", "--query", default="", type=str, help="define search keywords")
        parser.add_argument("-a", "--after", default=now - 86400, type=int, help="returns results after specified time")
        parser.add_argument("-b", "--before", default=now, type=int,
                            help="returns results before specified time")
        parser.add_argument("-c", "--count", type=int, default=100, help="defines number of results between [25,100]")
        return parser.parse_args()

    def fetch_submissions(self):
        self._log.info("Task started!")
        fields = ["author", "created_utc", "id", "link_flair_text", "num_comments", "removed_by_category",
                  "score", "selftext", "subreddit_subscribers", "title", "upvote_ratio"]
        file_exists = os.path.isfile(f"data/submissions_{self._args.subreddit}.csv")

        total = 0
        self._args.after = 1514764799 #Sunday, December 31, 2017 11:59:59 PM
        self._args.before = 1577833441 #31st dec, 2019
        while True:
            url = f"https://api.pushshift.io/reddit/search/submission?subreddit={self._args.subreddit}" \
                  f"&q={self._args.query}&fields={','.join(fields)}&after={self._args.after}" \
                  f"&before={self._args.before}&size={self._args.count}"
            response = requests.get(url)
            try:
                response_json = response.json().get("data")
                total += len(response_json)
                with open(f"data/submissions_{self._args.subreddit}.csv", mode="a", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=fields, delimiter=";")
                    if not file_exists:
                        writer.writeheader()

                    for data in response_json:
                        writer.writerow(data)

                self._args.after = response_json[-1]["created_utc"] + 1
                self._log.info(f"Received {total} submissions: {self._args.after}")

                if len(response_json) != self._args.count:
                    break

                t = random.randint(10, 30)
                self._log.info(f"Sleeping for {t} seconds")
                time.sleep(t)

            except Exception:
                self._log.info(f"Error occurred: {response}")
                t = random.randint(31, 60)
                self._log.info(f"Sleeping for {t} seconds")
                time.sleep(t)

        self._log.info("Task finished!")

    def fetch_comments(self):
        self._log.info("Task started!")
        fields = ["author", "body", "created_utc", "id", "link_id", "score"]
        df_ids = pd.read_csv(f"data/submissions_{self._args.subreddit}.csv", index_col="created_utc", delimiter=";", encoding="utf-8")
        file_exists = os.path.isfile(f"data/comments_{self._args.subreddit}.csv")

        ids = df_ids["id"]
        for author in ids:
            total = 0
            self._args.after = 1622591719 #Tuesday, June 1, 2021 11:55:19 PM
           # self._args.before = 1577833441 #31st dec, 2019
            while True:
                url = f"https://api.pushshift.io/reddit/comment/search?subreddit={self._args.subreddit}" \
                      f"&q={self._args.query}&fields={','.join(fields)}&after={self._args.after}" \
                      f"&before={self._args.before}&size={self._args.count}&link_id={author}"
                response = requests.get(url)
                try:
                    response_json = response.json().get("data")
                    total += len(response_json)
                    with open(f"data/comments_{self._args.subreddit}.csv", mode="a", encoding="utf-8") as csv_file:
                        writer = csv.DictWriter(csv_file, fieldnames=fields, delimiter=";")
                        if not file_exists:
                            writer.writeheader()

                        for data in response_json:
                            writer.writerow(data)

                    if len(response_json) < self._args.count:
                        self._log.info(f"Received {total} comments for {author}")
                        break

                    self._args.after = response_json[-1]["created_utc"] + 1
                    self._log.info(f"Received {total} comments for {author}: {self._args.after}")

                    t = random.randint(6, 8)
                    self._log.info(f"Sleeping for {t} seconds")
                    time.sleep(t)

                except Exception:
                    self._log.info(f"Error occurred: {response}")
                    t = random.randint(31, 60)
                    self._log.info(f"Sleeping for {t} seconds")
                    time.sleep(t)

            t = random.randint(6, 9)
            self._log.info(f"Sleeping for {t} seconds")
            time.sleep(0.10)

        self._log.info("Task finished!")


if __name__ == "__main__":    
    Reddit().fetch_submissions()
    #Reddit().fetch_comments()
    