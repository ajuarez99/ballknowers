import datetime
from datetime import timedelta
import cloudscraper
from bs4 import BeautifulSoup
import requests
import json
import difflib
import argparse
import time

# Hardcoded scoring based on your league's settings
scoring = {
    'pts': 0.5,
    'reb': 1.0,
    'ast': 1.0,
    'stl': 2.0,
    'blk': 2.0,
    'to': -1.0,
    'fg3m': 0.5,
    'ff': -2.0,
    'bonus_dd': 1.0,
    'bonus_td': 2.0,
    'bonus_40p': 2.0,
    'bonus_50p': 2.0,
    'bonus_15a': 0.0,
    'bonus_20r': 0.0,
}

stat_mapping = {
    'points': 'pts',
    'total_rebounds': 'reb',
    'assists': 'ast',
    'steals': 'stl',
    'blocks': 'blk',
    'turnovers': 'to',
    'made_three_point_field_goals': 'fg3m',
    'personal_fouls': 'pf',
}

def calculate_fantasy_points(stat, scoring):
    fp = 0.0
    for box_key, score_key in stat_mapping.items():
        if box_key in stat and score_key in scoring:
            fp += stat[box_key] * scoring[score_key]
    
    doubles_count = sum(1 for key in ['points', 'total_rebounds', 'assists', 'steals', 'blocks'] if stat.get(key, 0) >= 10)
    if doubles_count >= 2:
        fp += scoring.get('bonus_dd', 0)
    if doubles_count >= 3:
        fp += scoring.get('bonus_td', 0)
    
    if stat.get('points', 0) >= 40:
        fp += scoring.get('bonus_40p', 0)
    if stat.get('points', 0) >= 50:
        fp += scoring.get('bonus_50p', 0)
    if stat.get('assists', 0) >= 15:
        fp += scoring.get('bonus_15a', 0)
    if stat.get('total_rebounds', 0) >= 20:
        fp += scoring.get('bonus_20r', 0)
    
    return fp

def normalize_name(name):
    suffixes = [' Jr.', ' Sr.', ' II', ' III', ' IV', ' V', ' Jr', ' Sr', '.']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    return name

def custom_player_box_scores(day, month, year, debug=True):
    url = f"https://www.basketball-reference.com/friv/dailyleaders.cgi?month={month}&day={day}&year={year}"
    
    print(f"\n{'='*60}")
    print(f"DEBUGGING Basketball Reference Fetch")
    print(f"{'='*60}")
    print(f"URL: {url}")
    
    try:
        # Try with cloudscraper first
        print("\n[1] Attempting with cloudscraper...")
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        response = scraper.get(url, allow_redirects=True, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Final URL after redirects: {response.url}")
        print(f"Response length: {len(response.text)} characters")
        
        # Check for common blocking indicators
        if "Access Denied" in response.text or "403 Forbidden" in response.text:
            print("⚠️  Detected access denied message")
        if "cf-browser-verification" in response.text:
            print("⚠️  Detected Cloudflare browser verification")
        if len(response.text) < 1000:
            print("⚠️  Response is suspiciously short")
        
        # Save debug file
        if debug:
            debug_file = f'debug_response_{year}-{month:02d}-{day:02d}.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✓ Saved raw response to: {debug_file}")
        
        response.raise_for_status()
        
    except Exception as e:
        print(f"❌ Cloudscraper failed: {e}")
        
        # Fallback to regular requests with headers
        print("\n[2] Attempting with requests + headers...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response length: {len(response.text)} characters")
            response.raise_for_status()
        except Exception as e2:
            print(f"❌ Regular requests also failed: {e2}")
            return []
    
    print("\n[3] Parsing HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Debug: Look for the table (try both old and new IDs)
    table = soup.find('table', id='dailyleaders')
    if not table:
        table = soup.find('table', id='stats')
    
    if not table:
        print("❌ Table with id='dailyleaders' or 'stats' not found")
        
        # Check what tables exist
        all_tables = soup.find_all('table')
        print(f"\nFound {len(all_tables)} total tables on page:")
        for i, t in enumerate(all_tables[:5]):  # Show first 5
            table_id = t.get('id', 'no-id')
            table_class = t.get('class', 'no-class')
            print(f"  Table {i+1}: id='{table_id}', class='{table_class}'")
        
        # Check for error messages
        error_div = soup.find('div', class_='error')
        if error_div:
            print(f"\n⚠️  Found error message: {error_div.get_text(strip=True)}")
        
        # Check page title
        title = soup.find('title')
        if title:
            print(f"\nPage title: {title.get_text(strip=True)}")
        
        return []
    
    print(f"✓ Found stats table (id='{table.get('id')}')")
    
    tbody = table.find('tbody')
    if not tbody:
        print("❌ No tbody found in table")
        return []
    
    rows = tbody.find_all('tr')
    print(f"✓ Found {len(rows)} rows in table")
    
    box_scores = []
    errors = []
    
    for idx, row in enumerate(rows):
        cells = row.find_all(['th', 'td'])
        
        if len(cells) < 25:
            if idx < 3:  # Only show first few skipped rows
                print(f"  Row {idx+1}: Skipped (only {len(cells)} cells)")
            continue
        
        try:
            name = cells[1].text.strip()
            team = cells[2].text.strip().upper()
            location = 'HOME' if cells[3].text.strip() == 'vs.' else 'AWAY'
            opponent = cells[4].text.strip().upper()
            outcome = 'WIN' if cells[5].text.strip().startswith('W') else 'LOSS'
            
            # Parse minutes - handle both "33" and "33:36" formats
            minutes_str = cells[6].text.strip()
            if ':' in minutes_str:
                mins, secs = minutes_str.split(':')
                minutes_played = int(mins)
            else:
                minutes_played = int(minutes_str or 0)
            made_field_goals = int(cells[7].text.strip() or 0)
            attempted_field_goals = int(cells[8].text.strip() or 0)
            made_three_point_field_goals = int(cells[10].text.strip() or 0)
            attempted_three_point_field_goals = int(cells[11].text.strip() or 0)
            made_free_throws = int(cells[13].text.strip() or 0)
            attempted_free_throws = int(cells[14].text.strip() or 0)
            offensive_rebounds = int(cells[16].text.strip() or 0)
            defensive_rebounds = int(cells[17].text.strip() or 0)
            assists = int(cells[19].text.strip() or 0)
            steals = int(cells[20].text.strip() or 0)
            blocks = int(cells[21].text.strip() or 0)
            turnovers = int(cells[22].text.strip() or 0)
            personal_fouls = int(cells[23].text.strip() or 0)
            points = int(cells[24].text.strip() or 0)
            plus_minus = int(cells[25].text.strip() or 0) if len(cells) > 25 and cells[25].text.strip() else 0
            
            box_scores.append({
                'name': name,
                'team': team,
                'location': location,
                'opponent': opponent,
                'outcome': outcome,
                'minutes_played': minutes_played,
                'made_field_goals': made_field_goals,
                'attempted_field_goals': attempted_field_goals,
                'made_three_point_field_goals': made_three_point_field_goals,
                'attempted_three_point_field_goals': attempted_three_point_field_goals,
                'made_free_throws': made_free_throws,
                'attempted_free_throws': attempted_free_throws,
                'offensive_rebounds': offensive_rebounds,
                'defensive_rebounds': defensive_rebounds,
                'total_rebounds': offensive_rebounds + defensive_rebounds,
                'assists': assists,
                'steals': steals,
                'blocks': blocks,
                'turnovers': turnovers,
                'personal_fouls': personal_fouls,
                'points': points,
                'plus_minus': plus_minus,
            })
            
        except (ValueError, IndexError) as e:
            errors.append(f"Row {idx+1} ({cells[1].text.strip() if len(cells) > 1 else 'unknown'}): {e}")
            continue
    
    print(f"✓ Successfully parsed {len(box_scores)} player stats")
    
    if errors and len(errors) <= 5:
        print(f"\nParsing errors:")
        for err in errors:
            print(f"  {err}")
    elif len(errors) > 5:
        print(f"\n⚠️  {len(errors)} parsing errors (showing first 5):")
        for err in errors[:5]:
            print(f"  {err}")
    
    print(f"{'='*60}\n")
    
    return box_scores

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Fantasy Basketball Report Generator")
parser.add_argument('--date', type=str, default='yesterday',
                    help="Date for the report: 'today', 'yesterday', 'day_before', or 'YYYY-MM-DD'")
parser.add_argument('--debug', action='store_true', help='Enable debug output')
args = parser.parse_args()

# Determine the target date
if args.date == 'today':
    target_date = datetime.date.today()
elif args.date == 'yesterday':
    target_date = datetime.date.today() - timedelta(days=1)
elif args.date == 'day_before':
    target_date = datetime.date.today() - timedelta(days=2)
else:
    try:
        target_date = datetime.date.fromisoformat(args.date)
    except ValueError:
        print("Invalid date format. Using yesterday's date.")
        target_date = datetime.date.today() - timedelta(days=1)

day, month, year = target_date.day, target_date.month, target_date.year

print(f"\nFetching NBA stats for: {target_date.strftime('%A, %B %d, %Y')}")

# Fetch box scores with debugging
box_scores = custom_player_box_scores(day, month, year, debug=args.debug)

# Filter players who played
box_scores = [s for s in box_scores if s.get('minutes_played', 0) > 0]

if not box_scores:
    print("\n❌ No player data available. Check the debug output above.")
    print("\nTroubleshooting tips:")
    print("1. Check if there were actually NBA games on this date")
    print("2. Look at the saved debug HTML file to see what Basketball-Reference returned")
    print("3. Try visiting the URL directly in your browser")
    print("4. Basketball-Reference may be blocking automated requests")
    exit(1)

print(f"\n✓ Loaded stats for {len(box_scores)} players who played\n")

# Calculate fantasy points
for stat in box_scores:
    stat['fantasy_points'] = calculate_fantasy_points(stat, scoring)

# Sort and get top 20
top_players = sorted(box_scores, key=lambda x: x['fantasy_points'], reverse=True)[:20]

# Output top fantasy players
print(f"{'='*60}")
print(f"Top Fantasy Players for {target_date.strftime('%Y-%m-%d')}:")
print(f"{'='*60}")
for i, player in enumerate(top_players, 1):
    pts = player.get('points', 0)
    reb = player.get('total_rebounds', 0)
    ast = player.get('assists', 0)
    stl = player.get('steals', 0)
    blk = player.get('blocks', 0)
    print(f"{i:2d}. {player['name']:5s} - {player['fantasy_points']:6.2f} FP")
    print(f"     {pts}pts, {reb}reb, {ast}ast")

# Sleeper API parts
print(f"\n{'='*60}")
print("Fetching Sleeper trending data...")
print(f"{'='*60}")

try:
    players_url = "https://api.sleeper.app/v1/players/nba"
    players_response = requests.get(players_url, timeout=10)
    players_response.raise_for_status()
    players = players_response.json()
    
    id_to_name = {}
    for pid, info in players.items():
        if isinstance(info, dict) and 'full_name' in info:
            id_to_name[pid] = info['full_name']
    
    trending_url = "https://api.sleeper.app/v1/players/nba/trending/add?lookback_hours=24&limit=25"
    trending_response = requests.get(trending_url, timeout=10)
    trending_response.raise_for_status()
    trending = trending_response.json()
    
    box_names_lower = [normalize_name(s['name']).lower() for s in box_scores]
    name_to_fp = {normalize_name(s['name']).lower(): (s['name'], s['fantasy_points']) for s in box_scores}
    
    print(f"\nSleeper Trending Players {target_date.strftime('%m-%d-%Y')}:")
    matched = 0
    for t in trending:
        pid = t['player_id']
        name = id_to_name.get(pid, "Unknown")
        adds = t['count']
        normalized_name = normalize_name(name).lower()
        
        if normalized_name not in name_to_fp:
            close_matches = difflib.get_close_matches(normalized_name, box_names_lower, n=1, cutoff=0.75)
            if close_matches:
                normalized_name = close_matches[0]
        
        if normalized_name in name_to_fp:
            original_name, fp = name_to_fp[normalized_name]
            # Find the full stat line for this player
            player_stat = next((s for s in box_scores if normalize_name(s['name']).lower() == normalized_name), None)
            if player_stat:
                pts = player_stat.get('points', 0)
                reb = player_stat.get('total_rebounds', 0)
                ast = player_stat.get('assists', 0)
                stl = player_stat.get('steals', 0)
                blk = player_stat.get('blocks', 0)
                team = player_stat.get('team', 'UNK')
                print(f"{matched + 1:2d}. {original_name:5s} - {fp:6.2f} FP")
                print(f"     {pts}pts, {reb}reb, {ast}ast")
            else:
                print(f"{matched + 1:2d}. {original_name:25s} - {fp:6.2f} FP - Adds: {adds:5d}")
            matched += 1
    
    print(f"\n✓ Matched {matched}/{len(trending)} trending players with game data")
    
    # Save to file
    filename = f"fantasy_report_{target_date.strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        report = {
            'date': target_date.strftime('%Y-%m-%d'),
            'top_players': top_players,
            'trending': trending,
            'total_players': len(box_scores)
        }
        json.dump(report, f, indent=4)
    print(f"\n✓ Report saved to: {filename}")
    
except Exception as e:
    print(f"❌ Error with Sleeper API: {e}")
    print("Continuing without trending data...")