import argparse
import datetime
import glob
import os
import pandas as pd
import re

import common

fail_non_gossip_logs_dir_default = r"C:\Users\ronensch\Box Sync\Blockchain\flaky-tests\failed-logs-archive\non-gossip"


def find_failed_modules(log_file):
    failed_modules = []
    with open(log_file, "r", encoding="unicode_escape") as f:
        log = f.read()
        fail_pattern = r"FAIL\s+github.com/hyperledger/fabric/(.*?)\s"
        failed_modules = re.findall(fail_pattern, log)
        if not failed_modules:
            failed_modules = ['???']
    return failed_modules


def extract_date(file_path):
    file_name = os.path.basename(file_path)
    date_str = file_name.split("-")[0]
    return datetime.datetime.strptime(date_str, "%Y_%m_%d")


def main():
    parser = argparse.ArgumentParser(
        description="Script to analyze non-gossip related failed logs from Jenkins that have already been saved to a local directory."
                    "It creates two files in the logs directory: report.csv and summary.csv")
    parser.add_argument("--logs-dir",
                        default=fail_non_gossip_logs_dir_default,
                        help="The base directory where logs are saved")

    args = parser.parse_args()
    global fail_non_gossip_logs_dir
    fail_non_gossip_logs_dir = args.logs_dir

    log_files = glob.glob(os.path.join(fail_non_gossip_logs_dir, "*.log"))

    # fail_tbl[file][module] -> 0/1
    fail_tbl = pd.DataFrame()
    fail_tbl.insert(0, "file_name", "")
    for file in log_files:
        failed_modules = find_failed_modules(file)
        failed_tests = common.find_failed_tests(file)
        row = {**{m: 1 for m in failed_modules} , **{t: 1 for t in failed_tests}}
        file_name = os.path.basename(file)
        row["date"] = file_name.split("-")[0]
        row["file_name"] = file_name
        fail_tbl = fail_tbl.append(row, ignore_index=True)

    # Reorder columns. Place `date` column next to `file_name`
    cols = list(fail_tbl)
    cols.insert(1, cols.pop(cols.index("date")))
    fail_tbl = fail_tbl.loc[:, cols]

    # Create a report file
    report_file_name = "report.csv"
    report_file_path = os.path.join(fail_non_gossip_logs_dir, report_file_name)
    print(report_file_path)
    fail_tbl.to_csv(report_file_path, index=False)

    # Create a summary file
    summary_file_name = "summary.csv"
    summary_file_path = os.path.join(fail_non_gossip_logs_dir, summary_file_name)
    print(summary_file_path)
    fail_tbl.count().to_csv(summary_file_path, header=False)
    print(fail_tbl.count())


if __name__ == "__main__":
    main()
