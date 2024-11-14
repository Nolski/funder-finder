import json
from datetime import datetime

import numpy as np
from sklearn.preprocessing import StandardScaler
from sources.config import PRODUCTION_FINDERS


# Iterate over the projects and print their details
def get_project_funders(repo_name: str) -> list:
    """
    Attempts to retrieve funding data from each source for matching projects.
    When funding sources are found, adds the source's name, a boolean is_funded
    field with value True, and the date the funding data was retrieved to the
    metadata of each source of funding that was found
    :param repo_name: Github identifier for the project (e.g. georgetown-cset/funder-finder)
    :return: An array of funding metadata
    """
    obj = {}

    for finder_class in PRODUCTION_FINDERS:
        finder = finder_class()

        # The below run function is in every file of sources
        funding = finder.run(repo_name)

        if funding:
            funding = funding[0]
            if type(funding) == list:
                obj[finder.name] = funding
        # print("End here")

    return obj


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


def reading_all_projects():
    # Read the JSON file
    data = []
    urls = [
        "./data/gsoc.jsonl",
        "./data/numfocus.jsonl",
    ]
    for url in urls:
        with open(url, "r") as file:
            for line in file:
                data.append(json.loads(line))
    return data


class InvalidPolynomialFitError(Exception):
    def __init__(self, message="Invalid polynomial fit coefficients."):
        self.message = message
        super().__init__(self.message)


def start(data):
    results = []
    for slug, project in data.items():
        print("Name:", slug)
        v0 = {slug: project}
        v0 = convert_date_format2(v0)

        if v0:
            # Extract first and last dates
            all_dates = []
            for funding_source in v0.values():
                for item in funding_source:
                    if "datesFrom" in item:
                        all_dates.append(item["datesFrom"])

            all_dates = sorted(list(set(all_dates)))
            # all correct till here
            for key, project_data in v0.items():  # Iterate over the dictionary keys
                funding_amounts = []
                for date in all_dates:
                    amount = 0
                    for obj in project_data:
                        if "datesFrom" in obj and obj["datesFrom"] == date:
                            amount = obj["Amount_of_funding_usd"]
                    funding_amounts.append(amount)
                if max(funding_amounts) < 1000:
                    continue
                # print(funding_amounts,"Final funding amount")
                try:
                    # Normalize x and y values
                    x = np.arange(len(funding_amounts))
                    y = np.array(funding_amounts)
                    scaler = StandardScaler()
                    x_normalized = scaler.fit_transform(x.reshape(-1, 1)).flatten()
                    y_normalized = scaler.fit_transform(y.reshape(-1, 1)).flatten()

                    z = np.polyfit(x_normalized, y_normalized, 1)

                    # Check for NaN or infinite values in coefficients
                    if np.any(np.isnan(z)) or np.any(np.isinf(z)):
                        raise InvalidPolynomialFitError()
                except (InvalidPolynomialFitError, np.linalg.LinAlgError) as e:
                    print(
                        f"Error:  Skipping project: {project['name']} for source: {key}"
                    )
                    print(e)
                    continue

                result = {
                    "source": key,
                    "project_name": slug,
                    # Assuming project name is the same for all objects in project_data
                    "slope": z[0],
                }
                results.append(result)
        else:
            import ipdb
            ipdb.set_trace()
    with open("project_slopes.json", "w") as json_file:
        json.dump(results, json_file, indent=4)


if __name__ == "__main__":
    with open('./projects.json', 'r') as projects_file:
        data = json.load(projects_file)
        start(data)
