class UserDraftPick:
    def __init__(self, pick_no, username, draft_pick):
        self.pick_no = pick_no
        self.username = username
        self.draft_pick = draft_pick  # This is a DraftPick object

    def __repr__(self):
        """String representation for debugging."""
        return f"Pick {self.pick_no}: {self.username} selected {self.draft_pick.metadata.first_name} {self.draft_pick.metadata.last_name}"
