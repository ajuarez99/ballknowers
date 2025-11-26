class Matchup:
    def __init__(self, points, players, roster_id, matchup_id, starters, starters_points, players_points, custom_points=None):
        self.points = points
        self.players_id = players
        self.roster_id = roster_id
        self.matchup_id = matchup_id
        self.starters = starters
        self.starters_points = starters_points
        self.players_points = players_points
        self.custom_points = custom_points

    def __repr__(self):
        return (f"Matchup(roster_id={self.roster_id}, matchup_id={self.matchup_id}, points={self.points}, "
                f"starters={self.starters}, starters_points={self.starters_points})")

# Example: Converting a list of matchups from JSON data
def create_matchups(matchup_data):
    return [Matchup(**matchup) for matchup in matchup_data]

# Example Usage:
matchup_data = [  # Your provided list of matchups here
    {
        "points": 239.0,
        "players": ["1240", "1526", "1583", "1707", "1739", "1934", "2054", "2157", "2297", "2304", "2441", "2455", "2564", "2578", "2582"],
        "roster_id": 1,
        "custom_points": None,
        "matchup_id": 1,
        "starters": ["1240", "1526", "2304", "2455", "1739", "2054", "1583", "2297", "2564"],
        "starters_points": [30.5, 24.0, 21.5, 42.5, 42.0, 32.0, 22.0, 15.5, 9.0],
        "players_points": {
            "1240": 30.5, "1526": 24.0, "1583": 22.0, "1707": 12.5, "1739": 42.0, "1934": 0.0, "2054": 32.0,
            "2157": 0.0, "2297": 15.5, "2304": 21.5, "2441": 34.0, "2455": 42.5, "2564": 9.0, "2578": 18.5, "2582": 14.0
        }
    },
    # Add more matchups here...
]

# Create Matchup objects
matchups = create_matchups(matchup_data)

# Print all matchups to verify
for matchup in matchups:
    print(matchup)
