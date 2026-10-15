import argparse
import logging
import os
from helper import parse_user_date, end_of_day
from logging_util import configure_logging
from fetch_cves import fetch_cves
from oss_url_validator import validate_and_dispatch_oss

#Parse command line arguments when running the script.
def parse_args():
    parser = argparse.ArgumentParser(description="Get CVEs from NVD")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--api-key", default=None, help="NVD API key if available")
    parser.add_argument("--log", default="INFO", help="Logging level")
    parser.add_argument("--log-file", default=None, help="Save logs to a file")
    parser.add_argument("--dry-run", action="store_true", help="Just show info, don't fetch data")
    return parser.parse_args()

def main():
    args = parse_args()
    configure_logging(args.log, args.log_file)

    try:
        # Convert user input to datetime objects
        start_dt = parse_user_date(args.start)
        end_dt = end_of_day(parse_user_date(args.end))

        start_str = args.start
        end_str = args.end
        folder_name = f"{start_str}_to_{end_str}"  # folder for results
        patch_result_folder = os.path.join(folder_name, "patch_result")
        os.makedirs(patch_result_folder, exist_ok=True)

        logging.info(f"Output folder: {folder_name}")

        if args.dry_run:
            logging.info(f"Dry run: fetching CVEs from {start_dt} to {end_dt}")
            return

        # Fetch CVEs from NVD
        summary = fetch_cves(start_dt, end_dt, start_str, end_str, api_key=args.api_key)
        logging.info(f"Fetch summary: {summary}")

        # Validate patch URLs and save per-platform JSON files
        patch_file = os.path.join(folder_name, f"patch_cves_{start_str}_to_{end_str}.json")
        validate_and_dispatch_oss(patch_file, patch_result_folder)

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
