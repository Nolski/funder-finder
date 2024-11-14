import argparse
import os
from typing import Union

import requests
import time

from ._finder import Finder, DATE_RANGE

"""
Retrieves project funding statistics from Opencollective. To run this script,
you must first set an OPENCOLLECTIVE_API_KEY environment variable. See:
https://graphql-docs-v2.opencollective.com/access
"""


class OpenCollectiveFinder(Finder):
    name = "Open Collective"
    API_KEY_NAME = "OPENCOLLECTIVE_API_KEY"

    def __init__(self):
        assert os.environ.get(
            self.API_KEY_NAME
        ), "Please `export OPENCOLLECTIVE_API_KEY=<your opencollective api key>"
        self.api_key = os.environ.get(self.API_KEY_NAME)

    def get_funding_stats(self, project_slug: str) -> dict:
        """
        Retrives funding statistics for a project. See:
        https://graphql-docs-v2.opencollective.com/queries/collective
        :param project_slug: identifier for the project (like 'babel' in
            'https://opencollective.com/babel')
        :return: Dict of funding stats
        """

        result_arr = []
        for date_range in DATE_RANGE:
            query = f"""
            query ($slug: String) {{
                collective (slug: $slug) {{
                    totalFinancialContributors
                    stats {{
                        totalAmountReceived(
                            dateFrom: "{date_range[0]}"
                            dateTo: "{date_range[1]}"
                        ) {{
                            currency
                            value
                        }}
                    }}
                }}
            }}
            """
            variables = {"slug": project_slug}

            result = requests.post(
                f"https://api.opencollective.com/graphql/v2/{self.api_key}",
                json={"query": query, "variables": variables},
            )
            data = result.json()
            if "errors" in data:
                print(data)
                if "No collective found with slug" in data.get("errors")[0].get("message") or\
                    "Not Found" in data.get("errors")[0].get("message"):
                    return None

            if "error" in data:
                print(data)
                time.sleep(15)
                return self.get_funding_stats(project_slug)
            else:
                collective = data.get('data', {}).get('collective', {})
                if collective.get('totalFinancialContributors', None) == 0:
                    return None 
                stats = collective
                if stats:
                    result_arr.append(
                        {
                            "num_contributors": stats["totalFinancialContributors"],
                            "Amount_of_funding_usd": stats["stats"][
                                "totalAmountReceived"
                            ]["value"],
                            "datesFrom": date_range[0],
                            "datesTo": date_range[1],
                        }
                    )
        return result_arr

    def get_accounts(self, offset=0) -> dict:
        query = f"""
        {{
          accounts(limit:100, offset:{offset}, type:COLLECTIVE) {{
            totalCount
            nodes {{
              id
              slug
              type
              totalFinancialContributors
            }}
          }}
        }}
        """

        result = requests.post(
            f"https://api.opencollective.com/graphql/v2/{self.api_key}",
            json={"query": query},
        )
        return result.json()['data']['accounts']

        
    def get_host_projects(self, slug: str) -> list:
        query = """
        query($slug: String!, $limit: Int, $offset: Int) {
            connectedAccounts(slug: $slug) {
                ... on Host {
                collectives(limit: $limit, offset: $offset) {
                        totalCount
                        nodes {
                            id
                            slug
                            name
                            description
                            balance {
                                value
                                currency
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "slug": slug,
            "limit": 100,
            "offset": 0 
        }
        
        response = requests.post(
            'https://api.opencollective.com/graphql/v2',
            json={'query': query, 'variables': variables}
        )
        return response.json()


    def run(self, gh_project_slug: Union[str, None] = None) -> list:
        stats = self.get_funding_stats(self.get_repo_name(gh_project_slug))
        return [stats] if stats else []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project_slug",
        help="identifier for the project (like 'babel' in \
                'https://opencollective.com/babel')",
    )
    args = parser.parse_args()
    finder = OpenCollectiveFinder()
    # stats = finder.get_funding_stats(args.project_slug)
    # print(stats)
    print(finder.get_hosts())
