import json
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Assume PRODUCTION_FINDERS is defined somewhere in your code
from sources.config import PRODUCTION_FINDERS


def get_project_funders(repo_name: str) -> list:
    """
    Attempts to retrieve funding data from each source for matching projects. When funding sources are found, adds the
    source's name, a boolean is_funded field with value True, and the date the funding data was retrieved to the
    metadata of each source of funding that was found
    :param repo_name: Github identifier for the project (e.g. georgetown-cset/funder-finder)
    :return: An array of funding metadata
    """
    obj = {}

    for finder_class in PRODUCTION_FINDERS:
        finder = finder_class()
        print("Finding in", finder.name)

        # The below run function is in every file of sources
        funding = finder.run(repo_name)
        print("Funding count")

        if funding:
            funding = funding[0]
            if type(funding) == list:
                obj[finder.name] = funding

    print("Done finding everywhere")
    print([x['Amount_of_funding_usd'] for x in obj['Open Collective']])
    print([x['datesTo'] for x in obj['Open Collective']])
    print("....................")

    return obj


def plot_graph(dates_from, values):
    plt.figure(figsize=(10, 6))
    plt.plot(dates_from, values, label="Value", marker="o")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("Total Amount Received Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)


def getting_all_repos():
    # script to read all the repos and
    print("here")
    pass


def getting_top_15_change():
    repo_names = getting_all_repos()
    for repo_name in repo_names:
        v0 = get_project_funders(repo_name)
        v0 = convert_date_format2(v0)

    print("in getting top_15_change")

    print("after after")


def convert_date_format2(data):
    formatted_data = {}

    for key, value in data.items():
        formatted_data[key] = []
        for entry in value:
            if "datesFrom" in entry:
                if convert_date_format(entry["datesFrom"]):
                    entry["datesFrom"] = convert_date_format(entry["datesFrom"])
                    entry["datesTo"] = convert_date_format(entry["datesTo"])

            # if 'datesTo' in entry:
            #     entry['datesTo'] = datetime.strptime(entry['datesTo'], "%Y-%m-%dT%H:%M:%SZ").strftime(
            #         "%Y-%m-%d %H:%M:%S")
            formatted_data[key].append(entry)

    return formatted_data


def convert_date_format(date_string):
    try:
        # Parse the input date string
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        # Convert the date object to the desired format
        formatted_date = datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")
        return formatted_date
    except ValueError:
        print("Invalid date format provided.")
        return None


def processing_data(repo_name):
    if st.button("Plot Graph"):
        v0 = get_project_funders(repo_name)
        v0 = convert_date_format2(v0)

        if v0:
            # Extract first and last dates
            all_dates = []
            for funding_source in v0.values():
                for item in funding_source:
                    if "datesFrom" in item:
                        all_dates.append(item["datesFrom"])

            all_dates = sorted(list(set(all_dates)))
            # Iterate over the dictionary keys

            for key, project_data in v0.items():
                funding_amounts = []
                for date in all_dates:
                    amount = 0
                    for obj in project_data:
                        if "datesFrom" in obj and obj["datesFrom"] == date:
                            amount = obj["Amount_of_funding_usd"]
                    funding_amounts.append(amount)
                plt.plot(
                    all_dates, funding_amounts, label=key
                )  # Use dictionary key as label

            plt.xlabel("Date")
            plt.xticks(rotation=90)
            plt.ylabel("Amount of Funding (USD)")
            plt.title("Funding Over Time")
            plt.legend()
            plt.grid(True)
            st.pyplot(plt)

        else:

            st.warning("No funding data found for the given repository.")


def get_top_10_repos():
    with open(
        "./project_slopes.json",
        "r",
    ) as f:  # Replace 'path_to_json_file.json' with the path to your JSON file
        data = json.load(f)

    # Sort the data based on 'slope' in descending order
    # sorted_data = sorted(data,reverse=True)
    # sorted_data = sorted(data, key=lambda x: x['slope'], reverse=True)

    # Extract top 10 repositories
    # top_10_repos = sorted_data[:10]

    # Create a dictionary to store the smallest slope for each unique combination of source and project_name
    unique_data = {}
    for entry in data:
        key = (entry["source"], entry["project_name"])
        if key not in unique_data or entry["slope"] < unique_data[key]["slope"]:
            unique_data[key] = entry

    # Convert the unique dictionary values back to a list
    unique_data_list = list(unique_data.values())

    # Sort the unique data based on 'slope' in ascending order
    sorted_data = sorted(unique_data_list, key=lambda x: x["slope"], reverse=True)

    # Extract top 10 repositories
    top_10_repos = sorted_data[:50]

    return top_10_repos


def get_bottom_10_repos():
    with open(
        "./project_slopes.json",
        "r",
    ) as f:  # Replace 'path_to_json_file.json' with the path to your JSON file
        data = json.load(f)

    # Sort the data based on 'slope' in descending order
    # sorted_data = sorted(data,reverse=True)
    # sorted_data = sorted(data, key=lambda x: x['slope'], reverse=True)

    # Extract top 10 repositories
    # top_10_repos = sorted_data[:10]

    # Create a dictionary to store the smallest slope for each unique combination of source and project_name
    unique_data = {}
    for entry in data:
        key = (entry["source"], entry["project_name"])
        if key not in unique_data or entry["slope"] < unique_data[key]["slope"]:
            unique_data[key] = entry

    # Convert the unique dictionary values back to a list
    unique_data_list = list(unique_data.values())

    # Sort the unique data based on 'slope' in ascending order
    sorted_data = sorted(unique_data_list, key=lambda x: x["slope"], reverse=False)

    # Extract top 10 repositories
    top_10_repos = sorted_data[:50]

    return top_10_repos


def main():
    st.title("Funding Graph Streamlit App")
    if st.button("First 50 Companies with most changes"):
        top_10_repos = get_top_10_repos()
        st.table(top_10_repos)
    if st.button("First 50 Companies with lowest changes"):
        bottom_10_repos = get_bottom_10_repos()
        st.table(bottom_10_repos)

    repo_name = st.text_input(
        "Enter Github repository name (e.g., georgetown-cset/funder-finder):"
    )
    # st.button("First 15 Companies with most changes")
    processing_data(repo_name)


if __name__ == "__main__":
    main()
