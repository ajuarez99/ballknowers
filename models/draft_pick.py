class PlayerMetadata:
    def __init__(self, first_name, last_name, injury_status, news_updated, number, player_id, position, sport, status, team, team_abbr, team_changed_at, years_exp):
        self.first_name = first_name
        self.last_name = last_name
        self.injury_status = injury_status
        self.news_updated = news_updated
        self.number = number
        self.player_id = player_id
        self.position = position
        self.sport = sport
        self.status = status
        self.team = team
        self.team_abbr = team_abbr
        self.team_changed_at = team_changed_at
        self.years_exp = years_exp

    def __repr__(self):
        return f"{self.first_name} {self.last_name} ({self.team})"

class DraftPick:
    def __init__(self, draft_id, draft_slot, is_keeper, metadata, pick_no, picked_by, player_id, reactions, roster_id, round):
        self.draft_id = draft_id
        self.draft_slot = draft_slot
        self.is_keeper = is_keeper
        self.metadata = PlayerMetadata(**metadata)  # Convert metadata dictionary to a PlayerMetadata object
        self.pick_no = pick_no
        self.picked_by = picked_by
        self.player_id = player_id
        self.reactions = reactions
        self.roster_id = roster_id
        self.round = round

    def __repr__(self):
        return f"Pick #{self.pick_no}: {self.metadata}"


    
# Example Usage:
draft_data = {
    "draft_id": "1141438341108498432",
    "draft_slot": 1,
    "is_keeper": None,
    "metadata": {
        "first_name": "Victor",
        "injury_status": "DTD",
        "last_name": "Wembanyama",
        "news_updated": "1728750357037",
        "number": "1",
        "player_id": "2577",
        "position": "C",
        "sport": "nba",
        "status": "ACT",
        "team": "SAS",
        "team_abbr": "",
        "team_changed_at": "",
        "years_exp": "1"
    },
    "pick_no": 1,
    "picked_by": "1130198569467789312",
    "player_id": "2577",
    "reactions": None,
    "roster_id": 7,
    "round": 1
}

# Create an instance of the class
draft_pick = DraftPick(**draft_data)

# Print the draft pick
print(draft_pick)
