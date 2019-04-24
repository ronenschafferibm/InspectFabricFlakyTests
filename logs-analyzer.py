import argparse
import datetime
import glob
import os
import pandas as pd

import common

fail_gossip_logs_dir_default = r"C:\Users\ronensch\Box Sync\Blockchain\flaky-tests\failed-logs-archive\gossip"


def find_failed_modules(log_file):
    failed_modules = []
    with open(log_file, "r") as f:
        log = f.read()
        for module in common.gossip_modules:
            fail_pattern = "{}\t{}\t".format("FAIL", module)
            if fail_pattern in log:
                failed_modules.append(module)
    return failed_modules


def extract_date(file_path):
    file_name = os.path.basename(file_path)
    date_str = file_name.split("-")[0]
    return datetime.datetime.strptime(date_str, "%Y_%m_%d")


def main():
    parser = argparse.ArgumentParser(
        description="Script to analyze gossip related failed logs from Jenkins that have already been saved to a local directory."
                    "It creates two files in the logs directory: report.csv and summary.csv")
    parser.add_argument("--logs-dir",
                        default=fail_gossip_logs_dir_default,
                        help="The base directory where logs are saved")

    args = parser.parse_args()
    global fail_gossip_logs_dir
    fail_gossip_logs_dir = args.logs_dir

    log_files = glob.glob(os.path.join(fail_gossip_logs_dir, "*.log"))

    # fail_tbl[file][module] -> 0/1
    fail_tbl = pd.DataFrame(columns=common.gossip_modules)
    fail_tbl.insert(0, "file_name", "")
    for file in log_files:
        failed_modules = find_failed_modules(file)
        row = {m: 1 for m in failed_modules}
        row["file_name"] = os.path.basename(file)
        fail_tbl = fail_tbl.append(row, ignore_index=True)

    # Strip the common prefix from all columns
    column_map = {m: m.split("github.com/hyperledger/fabric/gossip/")[1] for m in common.gossip_modules}
    fail_tbl.rename(columns=column_map, inplace=True)

    # Create a report file
    report_file_name = "report.csv"
    report_file_path = os.path.join(fail_gossip_logs_dir, report_file_name)
    print(report_file_path)
    fail_tbl.to_csv(report_file_path, index=False)

    # Create a summary file
    summary_file_name = "summary.csv"
    summary_file_path = os.path.join(fail_gossip_logs_dir, summary_file_name)
    print(summary_file_path)
    fail_tbl.count().to_csv(summary_file_path, header=False)


if __name__ == "__main__":
    main()
