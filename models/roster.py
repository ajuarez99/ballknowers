class Roster:
    def __init__(self, roster_id, owner_id, league_id, metadata, players, starters, reserve, settings):
        self.roster_id = roster_id
        self.owner_id = owner_id
        self.league_id = league_id
        self.metadata = metadata  # Contains records and streak info
        self.players = players  # List of all players
        self.starters = starters  # List of starter player IDs
        self.reserve = reserve if reserve else []  # Handle missing reserve data
        self.settings = settings  # Stores wins, losses, points, etc.

    def __repr__(self):
        return (f"Roster {self.roster_id} | Owner: {self.owner_id} | "
                f"Record: {self.metadata.get('record', 'N/A')} | "
                f"Wins: {self.settings.get('wins', 0)}, Losses: {self.settings.get('losses', 0)}")
