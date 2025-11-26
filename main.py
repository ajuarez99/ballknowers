import requests
from models.league_member import LeagueMember  # Import the class
from models.draft_pick import DraftPick
from models.user_draft_pick import UserDraftPick
from models.roster import Roster
from bs4 import BeautifulSoup

# Constants
LEAGUE_ID = "1141438340626231296"
DRAFT_ID = "1141438341108498432"

league_members = [
    "popsharky",
    "njerickson",
    "ChedddaBob",
    "BamAddABio",
    "jstrobe",
    "theadambomb98",
    "jpelwell",
    "ImReallyHarry",
    "shajav",
    "bshewmon",
    "ChristianMaChilles",
    "GraftonCarlson"
]

def fetch_league_members(members, rosters):
    """Fetches user data for each league member and returns a dictionary."""
    members_data = {}

    for member in members:
        url = f"https://api.sleeper.app/v1/user/{member}"  
        response = requests.get(url)  

        if response.status_code == 200:  
            members_data[member] = response.json()  
        else:
            print(f"❌ Failed to fetch data for {member}, Status Code: {response.status_code}")

    
    return enrich_member_data(members_data, rosters)

def enrich_member_data(members_data, rosters):
    enriched_members = {}

    for member, data in members_data.items():
        user_id = data["user_id"]
        roster_id = None  

        for roster in rosters:
            if roster.owner_id == user_id:
                roster_id = roster.roster_id
                break

        enriched_members[member] = LeagueMember(
            user_id = user_id,
            username = member,
            display_name = data.get("display_name", ""),
            avatar = data.get("avatar", ""),
            is_bot = data.get("is_bot", ""),
            roster_id = roster_id
        )

    return enriched_members

def fetch_draft_picks(draft_id):
    """Fetches draft picks and returns a dictionary of DraftPick objects."""
    url = f"https://api.sleeper.app/v1/draft/{draft_id}/picks"
    response = requests.get(url)

    if response.status_code == 200:
        draft_picks_data = response.json()
        draft_picks_dict = {pick["pick_no"]: DraftPick(**pick) for pick in draft_picks_data}
        return draft_picks_dict
    else:
        print(f"❌ Failed to fetch draft picks, Status Code: {response.status_code}")
        return {}

def match_users_to_draft_picks(league_members_data, draft_picks_dict):
    """Matches draft picks to league members using user IDs."""
    # Create a lookup dictionary {user_id: username}
    user_id_to_username = {data.user_id: username for username, data in league_members_data.items()}
    user_draft_picks = []

    # Print draft picks with associated usernames
    print("\n📋 Draft Picks with Users:")
    for pick_no, draft_pick in draft_picks_dict.items():
        user_id = draft_pick.picked_by  # Get the user ID who made the pick
        username = user_id_to_username.get(user_id, "Unknown User")  # Find the username or default to "Unknown"
        print(f"Pick {pick_no}: {username} selected {draft_pick.metadata.first_name} {draft_pick.metadata.last_name}")
        user_draft_picks.append(UserDraftPick(pick_no, username, draft_pick))
    
    return user_draft_picks

def fetch_matchups(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/1"
    response = requests.get(url)

    if response.status_code == 200:
        matchupdata = response.json()
        print(matchupdata)

def fetch_rosters(league_id):
    url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    response = requests.get(url)

    if response.status_code == 200:
        roster_data = response.json()
        return [
            Roster(
                roster_id=roster["roster_id"],
                owner_id=roster["owner_id"],
                league_id=roster["league_id"],
                metadata=roster.get("metadata", {}),
                players=roster.get("players", []),
                starters=roster.get("starters", []),
                reserve=roster.get("reserve", []),
                settings=roster.get("settings", {})
            )
            for roster in roster_data
        ]
    else:
        print(f"Failed to fetch rosters. Status Code: {response.status_code}")
        return []
    
def web_scrape():
    # URL of the webpage
    url = "https://www.fantasypros.com/nba/adp/overall.php"

    # Send a request to fetch the HTML content
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the ADP data
    table = soup.find("table", {"id": "data"})  # Looking for table with the data

    # Extract player names and ADP
    players = []
    adp_values = []

    if table:
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:  # Ensure we have enough columns
                player_name = cols[1].text.strip()
                adp = cols[2].text.strip()
                players.append(player_name)
                adp_values.append(adp)

    # Print results
    for name, adp in zip(players, adp_values):
        print(f"{name}: {adp}")


def main():
    """Main function that runs the script."""

    rosters = fetch_rosters(LEAGUE_ID)
    league_members_data = fetch_league_members(league_members, rosters)
    draft_picks_dict = fetch_draft_picks(DRAFT_ID)
    user_draft_picks = match_users_to_draft_picks(league_members_data, draft_picks_dict)
    fetch_matchups(LEAGUE_ID)
    print_league_members(league_members_data)
    web_scrape()


def print_league_members(members_data):
    """Prints all league members with their enriched data."""
    for username, member in members_data.items():
        print(f"Username: {username}")
        print(f"User ID: {member.user_id}")
        print(f"Display Name: {member.display_name}")
        print(f"Roster ID: {member.roster_id}")  # Ensure roster_id was added
        print("-" * 40)
# Run the script only if executed directly
if __name__ == "__main__":
    main()


## jabari smith award - whoever had jabari smith the longest
## the observatory award - top 3 the most times in a season
## box of scraps award - lowest adr that was locked in
## domestic disturbance award - most troubled players on fantasy roster at one point
## joel embiid injury award - most out status on roster
## ghost award - shaheen
## least the locked amount
