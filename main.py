import requests
from models.league_member import LeagueMember  # Import the class
from models.draft_pick import DraftPick

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
    "ChristianMaChilles",
    "GraftonCarlson",
    "bshewmon"
]

def fetch_league_members(members):
    """Fetches user data for each league member and returns a dictionary."""
    members_data = {}

    for member in members:
        url = f"https://api.sleeper.app/v1/user/{member}"  
        response = requests.get(url)  

        if response.status_code == 200:  
            members_data[member] = response.json()  
        else:
            print(f"❌ Failed to fetch data for {member}, Status Code: {response.status_code}")

    return members_data

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
    user_id_to_username = {data["user_id"]: username for username, data in league_members_data.items()}

    # Print draft picks with associated usernames
    print("\n📋 Draft Picks with Users:")
    for pick_no, draft_pick in draft_picks_dict.items():
        user_id = draft_pick.picked_by  # Get the user ID who made the pick
        username = user_id_to_username.get(user_id, "Unknown User")  # Find the username or default to "Unknown"
        print(f"Pick {pick_no}: {username} selected {draft_pick.metadata.first_name} {draft_pick.metadata.last_name}")

def main():
    """Main function that runs the script."""
    league_members_data = fetch_league_members(league_members)
    draft_picks_dict = fetch_draft_picks(DRAFT_ID)

    # Print league members
    print("\n🏀 League Members:")
    for member, data in league_members_data.items():
        print(f"{member} - User ID: {data['user_id']}")

    # Print draft picks with user info
    match_users_to_draft_picks(league_members_data, draft_picks_dict)

# Run the script only if executed directly
if __name__ == "__main__":
    main()
