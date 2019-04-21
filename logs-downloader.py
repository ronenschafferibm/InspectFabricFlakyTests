import argparse
import datetime
import feedparser
import os
import pprint
import requests
import re

all_rss_link_default = "https://jenkins.hyperledger.org/job/fabric-verify-unit-tests-x86_64/rssAll"
fail_rss_link_default = "https://jenkins.hyperledger.org/job/fabric-verify-unit-tests-x86_64/rssFailed"
fail_rss_link = ""

fail_logs_base_dir_default = r"C:\Users\ronensch\Box Sync\Blockchain\flaky-tests\failed-logs-archive"
fail_logs_base_dir = ""
fail_gossip_logs_dir = ""
fail_non_gossip_logs_dir = ""


STATS_NEW_GOSSIP_LOGS = "new_gossip_logs"
STATS_NEW_NON_GOSSIP_LOGS = "new_non_gossip_logs"
STATS_OLD_LOGS = "old_logs"
STATS_TOTAL_LOGS = "total_logs"
stats = {
    STATS_NEW_GOSSIP_LOGS : 0,
    STATS_NEW_NON_GOSSIP_LOGS : 0,
    STATS_OLD_LOGS : 0,
    STATS_TOTAL_LOGS : 0,
}


def is_gossip_failed(log):
    for module in common.gossip_modules:
        fail_pattern = "{}\t{}\t".format("FAIL", module)
        if fail_pattern in log:
            return True
    return False


def extract_id(entry):
    return re.search(r":(\d+)$", entry["id"]).group(1)


def extract_date(entry):
    return datetime.datetime.strptime(entry["published"], "%Y-%m-%dT%H:%M:%SZ")


def build_file_name(entry):
    build_id = extract_id(entry)
    date = extract_date(entry)
    return "{}-{}.log".format(date.strftime("%Y_%m_%d"), build_id)


def is_log_file_exists(file_name):
    return os.path.isfile(os.path.join(fail_gossip_logs_dir, file_name)) or \
                    os.path.isfile(os.path.join(fail_non_gossip_logs_dir, file_name))


def get_and_save_log(entry):
    log_link = entry["link"] + "consoleText"
    r = requests.get(log_link)
    log = r.text
    if is_gossip_failed(log):
        stats[STATS_NEW_GOSSIP_LOGS] += 1
        log_dir = fail_gossip_logs_dir
    else:
        stats[STATS_NEW_NON_GOSSIP_LOGS] += 1
        log_dir = fail_non_gossip_logs_dir
    file_name = build_file_name(entry)
    file_path = os.path.join(log_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(log)


def main():
    parser = argparse.ArgumentParser(description="Script to download and save failed logs from Jenkins")
    parser.add_argument("--base-dir",
                        default=fail_logs_base_dir_default,
                        help="The base directory where the logs will be saved")
    parser.add_argument("--rss",
                        default=fail_rss_link_default,
                        help="The RSS link to download from")

    args = parser.parse_args()
    global fail_logs_base_dir, fail_gossip_logs_dir, fail_non_gossip_logs_dir
    fail_logs_base_dir = args.base_dir
    fail_gossip_logs_dir = os.path.join(fail_logs_base_dir, "gossip")
    fail_non_gossip_logs_dir = os.path.join(fail_logs_base_dir, "non-gossip")

    if not os.path.exists(fail_gossip_logs_dir):
        os.makedirs(fail_gossip_logs_dir)
    if not os.path.exists(fail_non_gossip_logs_dir):
        os.makedirs(fail_non_gossip_logs_dir)

    feed = feedparser.parse(args.rss)
    for entry in feed.entries:
        stats[STATS_TOTAL_LOGS] += 1
        file_name = build_file_name(entry)
        if is_log_file_exists(file_name):
            stats[STATS_OLD_LOGS] += 1
            continue
        get_and_save_log(entry)

    pprint.pprint(stats)


if __name__ == "__main__":
    main()
