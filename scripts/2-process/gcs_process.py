#!/usr/bin/env python
"""
This file is dedicated to processing Google Custom Search data
for analysis and comparison between quarters.
"""
# Standard library
import argparse
import csv
import os
import sys
import textwrap
import traceback

# Third-party
import pandas as pd
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonTracebackLexer

# Add parent directory so shared can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# First-party/Local
import shared  # noqa: E402

# Setup
LOGGER, PATHS = shared.setup(__file__)

# Constants
FILE1_COUNT = shared.path_join(PATHS["data_1-fetch"], "gcs_1_count.csv")
FILE2_LANGUAGE = shared.path_join(
    PATHS["data_1-fetch"], "gcs_2_count_by_language.csv"
)
FILE3_COUNTRY = shared.path_join(
    PATHS["data_1-fetch"], "gcs_3_count_by_country.csv"
)
QUARTER = os.path.basename(PATHS["data_quarter"])


def parse_arguments():
    """
    Parse command-line options, returns parsed argument namespace.
    """
    LOGGER.info("Parsing command-line options")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enable-save",
        action="store_true",
        help="Enable saving results",
    )
    parser.add_argument(
        "--enable-git",
        action="store_true",
        help="Enable git actions (fetch, merge, add, commit, and push)",
    )
    return parser.parse_args()


# def load_quarter_data(quarter):
#     """
#     Load data for a specific quarter.
#     """
#     file_path = os.path.join(PATHS["data"], f"{quarter}",
#       "1-fetch", "gcs_fetched.csv")
#     if not os.path.exists(file_path):
#         LOGGER.error(f"Data file for quarter {quarter} not found.")
#         return None
#     return pd.read_csv(file_path)


# def compare_data(current_quarter, previous_quarter):
#     """
#     Compare data between two quarters.
#     """
#     current_data = load_quarter_data(current_quarter)
#     previous_data = load_quarter_data(previous_quarter)

#     if current_data is None or previous_data is None:
#         return

#     # Process the data to compare by country
#     compare_by_country(current_data, previous_data,
#   current_quarter, previous_quarter)

#     # Process the data to compare by license
#     compare_by_license(current_data, previous_data,
#       current_quarter, previous_quarter)

#     # Process the data to compare by language
#     compare_by_language(current_data, previous_data,
#       current_quarter, previous_quarter)


# def compare_by_country(current_data, previous_data,
#       current_quarter, previous_quarter):
#     """
#     Compare the number of webpages licensed by country between two quarters.
#     """
#     LOGGER.info(f"Comparing data by country between
#       {current_quarter} and {previous_quarter}.")

#     # Get the list of country columns dynamically
#     columns = [col.strip() for col in current_data.columns.tolist()]
#     start_index = columns.index("United States")
#     end_index = columns.index("Japan") + 1

#     countries = columns[start_index:end_index]

#     current_country_data = current_data[countries].sum()
#     previous_country_data = previous_data[countries].sum()

#     comparison = pd.DataFrame({
#         'Country': countries,
#         f'{current_quarter}': current_country_data.values,
#         f'{previous_quarter}': previous_country_data.values,
#         'Difference': current_country_data.values
#            - previous_country_data.values
#     })

#     LOGGER.info(f"Country comparison:\n{comparison}")

#     # Visualization code to be added here


# def compare_by_license(current_data, previous_data,
#   current_quarter, previous_quarter):
#     """
#     Compare the number of webpages licensed by license type
#   between two quarters.
#     """
#     LOGGER.info(f"Comparing data by license type
#       between {current_quarter} and {previous_quarter}.")

#     current_license_data =
#       current_data.groupby('LICENSE TYPE').sum().sum(axis=1)
#     previous_license_data =
#       previous_data.groupby('LICENSE TYPE').sum().sum(axis=1)

#     comparison = pd.DataFrame({
#         'License Type': current_license_data.index,
#         f'{current_quarter}': current_license_data.values,
#         f'{previous_quarter}': previous_license_data.values,
#         'Difference': current_license_data.values
#           - previous_license_data.values
#     })

#     LOGGER.info(f"License type comparison:\n{comparison}")

#     # Visualization code to be added here


# def compare_by_language(current_data, previous_data,
#           current_quarter, previous_quarter):
#     """
#     Compare the number of webpages licensed by language between two quarters.
#     """
#     LOGGER.info(f"Comparing data by language between
#                   {current_quarter} and {previous_quarter}.")

#     # Get the list of language columns dynamically
#     columns = [col.strip() for col in current_data.columns.tolist()]
#     start_index = columns.index("English")
#     languages = columns[start_index:]

#     current_language_data = current_data[languages].sum()
#     previous_language_data = previous_data[languages].sum()

#     comparison = pd.DataFrame({
#         'Language': languages,
#         f'{current_quarter}': current_language_data.values,
#         f'{previous_quarter}': previous_language_data.values,
#         'Difference': current_language_data.values
#           - previous_language_data.values
#     })

#     LOGGER.info(f"Language comparison:\n{comparison}")


# def parse_arguments():
#     """
#     Parses command-line arguments, returns parsed arguments.
#     """
#     LOGGER.info("Parsing command-line arguments")
#     parser = argparse.ArgumentParser(
#       description="Google Custom Search Comparison Report")
#     parser.add_argument(
#         "--current_quarter", type=str, required=True,
#       help="Current quarter for comparison (e.g., 2024Q3)"
#     )
#     parser.add_argument(
#         "--previous_quarter", type=str, required=True,
#           help="Previous quarter for comparison (e.g., 2024Q2)"
#     )
#     return parser.parse_args()


def data_to_csv(args, data, file_path):
    if not args.enable_save:
        return
    os.makedirs(PATHS["data_phase"], exist_ok=True)
    # emulate csv.unix_dialect
    data.to_csv(
        file_path, index=False, quoting=csv.QUOTE_ALL, lineterminator="\n"
    )


def process_top_25_tools(args, count_data):
    LOGGER.info("Processing top 25 tools")
    data = count_data.sort_values("COUNT", ascending=False)
    data.reset_index(drop=True, inplace=True)
    data = data.iloc[:25]
    data.rename(
        columns={"TOOL_IDENTIFIER": "CC legal tool", "COUNT": "Count"},
        inplace=True,
    )
    file_path = shared.path_join(PATHS["data_phase"], "gcs_top_25_tools.csv")
    data_to_csv(args, data, file_path)


def process_totals_by_product(args, count_data):
    LOGGER.info("Processing totals by product")
    data = {
        "Licenses version 4.0": 0,
        "Licenses version 3.0": 0,
        "Licenses version 2.x": 0,
        "Licenses version 1.0": 0,
        "CC0 1.0": 0,
        "Public Domain Mark 1.0": 0,
        "Certification 1.0 US": 0,
    }
    for row in count_data.itertuples(index=False):
        tool = row[0]
        count = row[1]
        if tool.startswith("PDM"):
            key = "Public Domain Mark 1.0"
        elif "CC0" in tool:
            key = "CC0 1.0"
        elif "PUBLICDOMAIN" in tool:
            key = "Certification 1.0 US"
        elif "4.0" in tool:
            key = "Licenses version 4.0"
        elif "3.0" in tool:
            key = "Licenses version 3.0"
        elif "2." in tool:
            key = "Licenses version 2.x"
        elif "1.0" in tool:
            key = "Licenses version 1.0"
        else:
            raise shared.QuantifyingException("Invalid TOOL_IDENTIFIER")
        data[key] += count

    data = pd.DataFrame(
        data.items(), columns=["CC legal tool product", "Count"]
    )
    file_path = shared.path_join(
        PATHS["data_phase"], "gcs_totals_by_product.csv"
    )
    data_to_csv(args, data, file_path)


def process_totals_by_unit(args, count_data):
    LOGGER.info("Processing totals by unit")
    data = {}
    for row in count_data.itertuples(index=False):
        tool = row[0]
        count = row[1]
        if tool.startswith("PDM"):
            key = "mark"
        elif "CC0" in tool:
            key = "cc0"
        elif "PUBLICDOMAIN" in tool:
            key = "certification"
        else:
            parts = tool.split()
            key = parts[1].lower()
            if key == "by-nd-nc":
                key = "by-nc-nd"
        if key not in data.keys():
            data[key] = count
        else:
            data[key] += count

    data = pd.DataFrame(data.items(), columns=["Legal Tool Unit", "Count"])
    data.sort_values("Count", ascending=False, inplace=True)
    data.reset_index(drop=True, inplace=True)
    file_path = shared.path_join(PATHS["data_phase"], "gcs_totals_by_unit.csv")
    data_to_csv(args, data, file_path)


def process_totals_by_free_cultural(args, count_data):
    LOGGER.info("Processing totals by Approved for Free Cultural Works")
    data = {
        "Approved for Free Cultural Works": 0,
        "Limited uses": 0,
    }
    for row in count_data.itertuples(index=False):
        tool = row[0]
        count = row[1]
        if tool.startswith("PDM") or "CC0" in tool or "PUBLICDOMAIN" in tool:
            key = "Approved for Free Cultural Works"
        else:
            parts = tool.split()
            unit = parts[1].lower()
            if unit in ["by-sa", "by", "sa", "sampling+"]:
                key = "Approved for Free Cultural Works"
            else:
                key = "Limited uses"
        data[key] += count

    data = pd.DataFrame(data.items(), columns=["Category", "Count"])
    data.sort_values("Count", ascending=False, inplace=True)
    data.reset_index(drop=True, inplace=True)
    file_path = shared.path_join(
        PATHS["data_phase"], "gcs_totals_by_free_cultural.csv"
    )
    data_to_csv(args, data, file_path)


def process_totals_by_restrictions(args, count_data):
    LOGGER.info("Processing totals by restriction")
    data = {"level 0": 0, "level 1": 0, "level 2": 0, "level 3": 0}
    for row in count_data.itertuples(index=False):
        tool = row[0]
        count = row[1]
        if tool.startswith("PDM") or "CC0" in tool or "PUBLICDOMAIN" in tool:
            key = "level 0"
        else:
            parts = tool.split()
            unit = parts[1].lower()
            if unit in ["by-sa", "by", "sa", "sampling+"]:
                key = "level 1"
            elif unit in ["by-nc", "by-nc-sa", "sampling", "nc", "nc-sa"]:
                key = "level 2"
            else:
                key = "level 3"
        data[key] += count

    data = pd.DataFrame(data.items(), columns=["Category", "Count"])
    file_path = shared.path_join(
        PATHS["data_phase"], "gcs_totals_by_restrictions.csv"
    )
    data_to_csv(args, data, file_path)


def main():
    args = parse_arguments()
    shared.log_paths(LOGGER, PATHS)
    shared.git_fetch_and_merge(args, PATHS["repo"])

    # Count data
    count_data = pd.read_csv(FILE1_COUNT, usecols=["TOOL_IDENTIFIER", "COUNT"])
    process_top_25_tools(args, count_data)
    process_totals_by_product(args, count_data)
    process_totals_by_unit(args, count_data)
    process_totals_by_free_cultural(args, count_data)
    process_totals_by_restrictions(args, count_data)

    # # Langauge data
    # langauge_data = pd.read_csv(
    #     FILE2_LANGUAGE, usecols=["TOOL_IDENTIFIER", "LANGUAGE", "COUNT"]
    # )

    # # Country data
    # country_data = pd.read_csv(
    #     FILE3_COUNTRY, usecols=["TOOL_IDENTIFIER", "COUNTRY", "COUNT"]
    # )

    args = shared.git_add_and_commit(
        args,
        PATHS["repo"],
        PATHS["data_quarter"],
        f"Add and commit new Google Custom Search (GCS) data for {QUARTER}",
    )
    shared.git_push_changes(args, PATHS["repo"])


if __name__ == "__main__":
    try:
        main()
    except shared.QuantifyingException as e:
        if e.exit_code == 0:
            LOGGER.info(e.message)
        else:
            LOGGER.error(e.message)
        sys.exit(e.exit_code)
    except SystemExit as e:
        LOGGER.error(f"System exit with code: {e.exit_code}")
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        LOGGER.info("(130) Halted via KeyboardInterrupt.")
        sys.exit(130)
    except Exception:
        traceback_formatted = textwrap.indent(
            highlight(
                traceback.format_exc(),
                PythonTracebackLexer(),
                TerminalFormatter(),
            ),
            "    ",
        )
        LOGGER.critical(f"(1) Unhandled exception:\n{traceback_formatted}")
        sys.exit(1)
