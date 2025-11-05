from dataclasses import dataclass
from enum import IntEnum
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GH_MIN_REQUIRED_PARSE_LENGTH = 4


class GH_SC(IntEnum):
    TEAM_NAME_TOO_LONG = -6
    TEAM_MEMBER_TOO_LONG = -5
    HTTP_ERROR = -4
    REQ_FAIL_H = -3
    TIMEOUT = -2
    BAD_URL = -1
    OK = 0


@dataclass
class GHResponse:
    status: GH_SC
    response: str = ""


def parse_gh_url(gh_url: str) -> str:
    parse = gh_url.split('/')
    if len(parse) < GH_MIN_REQUIRED_PARSE_LENGTH:
        return ""
    return (f"https://raw.githubusercontent.com/{parse[3]}/{parse[4]}"
            "/refs/heads/main/")


# TODO: These two methods are damn near the same.
class GHController:
    async def get_gh_team_name(self, gh_url: str) -> GHResponse:
        """Gets the teamname from the github repo"""
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

        # If team name too long, return
        if len(response.text) > int(os.getenv("MAX_TEAM_NAME_LEN")):
            return GHResponse(status=GH_SC.TEAM_NAME_TOO_LONG)

        return GHResponse(
            response=response.text,
            status=GH_SC.OK
        )

    async def get_gh_team_member_names(self, gh_url: str) -> GHResponse:
        """Gets the team members from the github repo"""
        parsed_url = parse_gh_url(gh_url)

        # catches some bad urls, but not all
        if parsed_url == "":
            return GHResponse(
                status=GH_SC.BAD_URL
            )

        url = parse_gh_url(gh_url) + "teammembers"

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

        if response.status_code != 200:
            return GHResponse(status=GH_SC.HTTP_ERROR)

        # If team name too long, return
        if len(response.text) > int(os.getenv("MAX_TEAM_MEMBER_LEN")):
            return GHResponse(status=GH_SC.TEAM_MEMBER_TOO_LONG)

        return GHResponse(
            response=response.text,
            status=GH_SC.OK
        )
