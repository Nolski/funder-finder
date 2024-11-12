from typing import Union
from datetime import datetime, timedelta
import pandas as pd


def get_date_range():
    # Current date
    now = datetime.now()

    # Calculate the start date 5 years ago
    start_date = now - timedelta(days=5 * 365)

    # Generate a list of tuples representing 6-month blocks with the required
    # time format
    date_ranges = pd.date_range(start=start_date, end=now, freq='6ME')

    return [
        (
            date_ranges[i].strftime('%Y-%m-%dT00:00:00Z'),
            date_ranges[i + 1].strftime('%Y-%m-%dT00:00:00Z')
        )
        for i in range(len(date_ranges) - 1)
    ]


DATE_RANGE = get_date_range()


class Finder:
    name = "Abstract Funder Finder"

    @staticmethod
    def get_repo_name(project: str) -> str:
        """
        Extracts a repo name from a github identifier or url (i.e. funder-finder from georgetown-cset/funder-finder or
        https://github.com/georgetown-cset/funder-finder)
        :param project: Github project name
        :return: Repo name
        """
        return project.strip().split("/")[-1]

    @staticmethod
    def get_owner_name(project: str) -> str:
        """
        Extracts an owner (user or organization) name from a github identifier or url (i.e. georgetown-cset
        from georgetown-cset/funder-finder or https://github.com/georgetown-cset/funder-finder)
        :param project: Github project name
        :return: Owner name
        """
        if "/" not in project:
            # then we already have the owner
            return project.strip()
        return project.strip().split("/")[-2]

    @staticmethod
    def get_owner_and_repo_name_from_github_url(gh_url: str) -> str:
        """
        Returns GitHub owner and repo name from a GitHub URL,
        e.g. https://github.com/georgetown-cset/funder-finder -> georgetown-cset/funder-finder
        :param gh_url: identifier for the GitHub organization
        :return: str
        """
        return "/".join(gh_url.split("/")[-2:])

    def run(self, gh_project_slug: Union[str, None] = None) -> list:
        """
        This method should be implemented for subclasses and, if funding is found for a given source, return an
        array containing a nonempty subset of the following information for each type of funding provided
        by that source
        {
          "funding_type": string,
          "num_contributors": int,
          "total_funding_usd": int,
          "contributors": [{
                  "contributor_name": string,
                  "amount_received_usd": int,
                  "is_affiliated": bool
          }],
          "contributions": [{
                  "date_contribution_made": YYYY-MM-DD,
                  "amount_recieved_usd": int,
                  "contributor_name": string,
          }],
          If the only information available is whether the source funds the project or not, return
          [{ "is_funded": True }]
        }
        :param gh_project_slug: Identifier for the project owner and repo, e.g. georgetown-cset/funder-finder
        :return: A dict of metadata about the project's funding, if funded, else None
        """
        return []
