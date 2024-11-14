# Retrieves all funding information for a project from supported sources

import json
import argparse
from typing import List, Tuple, Dict
from sources.opencollective import OpenCollectiveFinder

import matplotlib.pyplot as plt
from sources.config import PRODUCTION_FINDERS


def get_project_funders(repo_name: str) -> list:
    """
    Attempts to retrieve funding data from each source for matching projects.
    When funding sources are found, adds the source's name, a boolean is_funded
    field with value True, and the date the funding data was retrieved to the
    metadata of each source of funding that was found
    :param repo_name: Github identifier for the project \
            (e.g. georgetown-cset/funder-finder)
    :return: An array of funding metadata
    """
    project_funders = []
    datesFrom = []
    datesTo = []
    values = []
    for finder_class in PRODUCTION_FINDERS:
        finder = finder_class()
        funding = finder.run(repo_name)
        if funding:
            for source in funding:
                project_funders.append(source)
                print("------------------", project_funders)
                if len(project_funders) > 2:
                    print("------------------")
                    datesFrom.append(project_funders[2][0]["datesFrom"])

                    datesTo.append(project_funders[2][0]["datesTo"])
                    values.append(project_funders[2][0]["Amount_of_funding_usd"])
                    print(values[0], datesTo, datesFrom)
                    print("----------------")
    return project_funders, datesFrom, datesTo, values


def get_oc_collective_slugs(oc_finder: OpenCollectiveFinder) -> list:
    """
    Generates a list of slugs for every Collective that exists on Open Collective
    :param oc_finder: OpenCollectiveFinder object to run the query on
    :return list of slugs (str)
    """
    d = oc_finder.get_accounts()
    collective_slugs = []

    total = d['totalCount']
    i = len(d['nodes'])

    for account in d['nodes']:
        collective_slugs.append(account['slug'])

    while i < total:
        d = oc_finder.get_accounts(i)
        for account in d['nodes']:
            collective_slugs.append(account['slug'])
        i += len(d['nodes'])
        print(i) 
    
    return collective_slugs
        
    with open('collective_slugs.json', 'w') as slugs_file:
        json.dump(collective_slugs, slugs_file)

    

def get_oc_project_stats(slugs: list, oc_finder: OpenCollectiveFinder) -> Tuple[Dict[dict], List[dict], List[dict]]:
    """
    Gets timeseries data for the given slugs over the last 5 years

    Returns:
        Tuple[Dict[dict], List[dict], List[dict]]: A tuple containing:
            - projects (List[int]): A dictionary of Collectives that contain funding.
            - projects_statless (List[str]): A list of Collective slugs that don't contain funding.
            - errors (List[dict]): A list of errors encountered.
    """
    projects = {}
    projects_statless = []
    errors = []
    for slug in slugs:
        print(f"Finding stats for {slug}")
        try:
            stats = oc_finder.get_funding_stats(slug)
            if stats is not None:
                print("stats found")
                projects[slug] = stats
            else:
                print("stats not found") 
                projects_statless.append(slug) 
        except Exception as e:
            errors.append({"error": str(e), "slug": slug})
    
    return projects, projects_statless, errors

    with open('projects.json', 'w') as projects_file:
        json.dump(projects, projects_file)
    with open('statless_projects.json', 'w') as projects_file:
        json.dump(projects_statless, projects_file)
    with open('errors.json', 'w') as errors_file:
        json.dump(errors, errors_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    oc_finder = OpenCollectiveFinder()
    slugs = get_oc_collective_slugs()

    with open('collective_slugs.json', 'w') as slugs_file:
        json.dump(collective_slugs, slugs_file)
    
    with open('collective_slugs.json', 'r') as slugs_file:
        slugs = json.load(slugs_file)
        get_oc_project_stats(slugs, oc_finder)
        
    projects, projects_statless, errors = get_oc_project_stats(slugs, oc_finder)

    with open('projects.json', 'w') as projects_file:
        json.dump(projects, projects_file)
    with open('statless_projects.json', 'w') as projects_file:
        json.dump(projects_statless, projects_file)
    with open('errors.json', 'w') as errors_file:
        json.dump(errors, errors_file)



def old_main():
    parser.add_argument(
        "repo_name",
        help="Identifier for GitHub repo, in the form `owner_name/repo_name` "
        "(e.g. georgetown-cset/funder-finder)",
    )
    args = parser.parse_args()
    v0 = get_project_funders(args.repo_name)
    print("v0", v0)
    datesFrom = [f'({i["datesFrom"]},{i["datesTo"]})' for i in v0[0][2]]
    # datesTo=[i["datesTo"] for i in v0[0][2]]
    values = [i["Amount_of_funding_usd"] for i in v0[0][2]]
    print("datesFrom", datesFrom)

    print(v0)
    plt.figure(figsize=(10, 6))
    plt.plot(datesFrom, values, label="datesRange", marker="o")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("Total Amount Received Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()
