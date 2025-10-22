from dataclasses import dataclass
from enum import Enum
from time import sleep
import requests


class GH_SC(Enum):
    OK = 1
    BAD_URL = 2
    TIMEOUT = 3
    REQ_FAIL_H = 4
    HTTP_ERROR = 5


@dataclass
class GHResponse:
    status: GH_SC
    response: str = ""


def parse_gh_url(gh_url: str) -> str:
    parse = gh_url.split('/')
    if len(parse) < 4:
        return ""
    return (f"https://raw.githubusercontent.com/{parse[3]}/{parse[4]}/refs/heads/main/")


class GHController:
    async def get_gh_team_name(self, gh_url: str) -> GHResponse:
        sleep(1)
        parsed_url = parse_gh_url(gh_url)

        # catches some bad urls, but not all
        if parsed_url == "":
            return GHResponse(
                status=GH_SC.BAD_URL
            )

        url = parse_gh_url(gh_url) + "teamname"

        try:
            response = requests.get(url)
        except requests.exceptions.Timeout:
            return GHResponse(status=GH_SC.TIMEOUT)
        except requests.exceptions.HTTPError:
            print(
                "ERROR: Failed to request team name. Probably a private repo"
            )
            return GHResponse(status=GH_SC.HTTP_ERROR)
        except requests.exceptions.RequestException as e:
            print(e)
            return GHResponse(status=GH_SC.REQ_FAIL_H)

        print(len(response.text))

        return GHResponse(
            response=response.text,
            status=GH_SC.OK
        )

    async def get_gh_team_member_names(self, gh_url: str) -> GHResponse:
        sleep(1)
        return GHResponse(
            response="Ruby Engelhart",
            status=GH_SC.OK
        )
