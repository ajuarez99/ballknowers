# analytics/draft_report.py
import requests
import pandas as pd

def fetch_draft_picks(draft_id):
    url = f'https://api.sleeper.app/v1/draft/{draft_id}/picks'
    return requests.get(url).json()

def fetch_users(league_id):
    url = f'https://api.sleeper.app/v1/league/{league_id}/users'
    return requests.get(url).json()

def fetch_rosters(league_id):
    url = f'https://api.sleeper.app/v1/league/{league_id}/rosters'
    return requests.get(url).json()

def generate_report(league_id, draft_id):
    picks = fetch_draft_picks(draft_id)
    users = fetch_users(league_id)
    rosters = fetch_rosters(league_id)
    
    # Map owner_id to display_name and team_name
    user_map = {u['user_id']: {'display_name': u['display_name'], 'team_name': u.get('metadata', {}).get('team_name', 'N/A')} for u in users}
    
    # Map roster_id to owner details
    roster_map = {r['roster_id']: user_map.get(r['owner_id'], {'display_name': 'Unknown', 'team_name': 'N/A'}) for r in rosters}
    
    # Process picks
    df_picks = pd.DataFrame(picks)
    df_picks['player_name'] = df_picks['metadata'].apply(lambda m: f"{m['first_name']} {m['last_name']}")
    df_picks['team_pos'] = df_picks['metadata'].apply(lambda m: f"{m.get('team', 'N/A')}, {m.get('position', 'N/A')}")
    df_picks['username'] = df_picks['roster_id'].map(lambda rid: roster_map.get(rid, {})['display_name'])
    df_picks['team_name'] = df_picks['roster_id'].map(lambda rid: roster_map.get(rid, {})['team_name'])
    
    # Clean: Drop unwanted columns
    drop_cols = ['draft_id', 'is_keeper', 'metadata', 'player_id']
    df_picks = df_picks.drop(columns=drop_cols, errors='ignore')
    
    # Sort and save
    df_picks = df_picks.sort_values('pick_no')
    df_picks.to_csv('draft_report.csv', index=False)
    return df_picks

# Run
league_id = '1229352720222134272'
draft_id = '1229352720230514688'
report = generate_report(league_id, draft_id)
print(report.head(144))  # First 3 rounds for console check