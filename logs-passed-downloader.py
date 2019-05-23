import argparse
import datetime
import feedparser
import os
import pprint
import requests
import re

import common

all_rss_link_default = "https://jenkins.hyperledger.org/job/fabric-verify-unit-tests-x86_64/rssAll"
fail_rss_link = ""

pass_logs_base_dir_default = r"C:\Users\ronensch\Box Sync\Blockchain\flaky-tests\passed-logs-archive"
pass_logs_base_dir = ""


STATS_NEW_PASSED_LOGS = "new_passed_logs"
STATS_OLD_PASSED_LOGS = "old_passed_logs"
STATS_TOTAL_LOGS = "total_logs"
stats = {
    STATS_NEW_PASSED_LOGS : 0,
    STATS_OLD_PASSED_LOGS : 0,
    STATS_TOTAL_LOGS : 0,
}


def extract_id(entry):
    return re.search(r":(\d+)$", entry["id"]).group(1)


def extract_date(entry):
    return datetime.datetime.strptime(entry["published"], "%Y-%m-%dT%H:%M:%SZ")


def build_file_name(entry):
    build_id = extract_id(entry)
    date = extract_date(entry)
    return "{}-{}.log".format(date.strftime("%Y_%m_%d"), build_id)


def is_log_file_exists(file_name):
    return os.path.isfile(os.path.join(pass_logs_base_dir, file_name)) or \
                    os.path.isfile(os.path.join(pass_logs_base_dir, file_name))


def is_fail(entry):
    return "broken" in entry.title or "aborted" in entry.title


def get_and_save_log(entry):
    log_link = entry["link"] + "consoleText"
    r = requests.get(log_link)
    log = r.text
    file_name = build_file_name(entry)
    file_path = os.path.join(pass_logs_base_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(log)


def main():
    parser = argparse.ArgumentParser(description="Script to download and save passed logs from Jenkins")
    parser.add_argument("--base-dir",
                        default=pass_logs_base_dir_default,
                        help="The base directory where the logs will be saved")
    parser.add_argument("--rss",
                        default=all_rss_link_default,
                        help="The RSS link to download from")

    args = parser.parse_args()
    global pass_logs_base_dir
    pass_logs_base_dir = args.base_dir

    if not os.path.exists(pass_logs_base_dir):
        os.makedirs(pass_logs_base_dir)

    feed = feedparser.parse(args.rss)
    for entry in feed.entries:
        if is_fail(entry):
            continue
        stats[STATS_TOTAL_LOGS] += 1
        file_name = build_file_name(entry)
        if is_log_file_exists(file_name):
            stats[STATS_OLD_PASSED_LOGS] += 1
            continue
        stats[STATS_NEW_PASSED_LOGS] += 1
        get_and_save_log(entry)

    pprint.pprint(stats)


if __name__ == "__main__":
    main()
