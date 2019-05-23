import argparse
import datetime
import glob
import os
import re
import pandas as pd

import common

logs_dir_default = r"C:\Users\ronensch\Box Sync\Blockchain\flaky-tests\passed-logs-archive"
logs_dir = ""


def find_times(log_file):
    with open(log_file, "r") as f:
        log = f.read()
        pattern = r"ok\s+github.com/hyperledger/fabric/(.+?)\s+([0-9.]+?)s"
        module_time_dict = dict(re.findall(pattern, log))
        return {key:float(val) for (key, val) in module_time_dict.items()}


def extract_date(file_path):
    file_name = os.path.basename(file_path)
    date_str = file_name.split("-")[0]
    return datetime.datetime.strptime(date_str, "%Y_%m_%d")


def main():
    parser = argparse.ArgumentParser(
        description="Script to analyze unit-test running times in logs from Jenkins that have already been saved to a a"
                    "local directory."
                    "It creates two files in the logs directory: time-report.csv and time-summary.csv")
    parser.add_argument("--logs-dir",
                        default=logs_dir_default,
                        help="The base directory where logs are saved")

    args = parser.parse_args()
    global logs_dir
    logs_dir = args.logs_dir

    log_files = glob.glob(os.path.join(logs_dir, "*.log"))

    # time_df[file][module] -> time[sec]
    time_df = pd.DataFrame()
    time_df.insert(0, "file_name", "")
    for file in log_files:
        module2time_dict = find_times(file)

        row = module2time_dict
        file_name = os.path.basename(file)
        row["date"] = file_name.split("-")[0]
        row["file_name"] = file_name
        time_df = time_df.append(row, ignore_index=True)

    # Reorder columns. Place `date` column next to `file_name`
    cols = list(time_df)
    cols.insert(1, cols.pop(cols.index("date")))
    time_df = time_df.loc[:, cols]

    # Create a report file
    report_file_name = "time-report.csv"
    report_file_path = os.path.join(logs_dir, report_file_name)
    print(report_file_path)
    time_df.to_csv(report_file_path, index=False)

    # Create a summary file
    summary_file_name = "time-summary.csv"
    summary_file_path = os.path.join(logs_dir, summary_file_name)
    print(summary_file_path)
    time_df.describe().T.to_csv(summary_file_path, header=True)


if __name__ == "__main__":
    main()
