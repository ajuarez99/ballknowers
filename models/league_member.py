class LeagueMember:
    def __init__(self, username, user_id, avatar, display_name, is_bot):
        self.username = username
        self.user_id = user_id
        self.avatar = avatar
        self.display_name = display_name
        self.is_bot = is_bot

    def __repr__(self):
        return f"LeagueMember(username='{self.username}', display_name='{self.display_name}')"
