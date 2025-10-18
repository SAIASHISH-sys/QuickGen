"""
Data Processor - Extract scoreboard data from match_data.json
"""
import json
import re


def extract_scoreboard_data(match_data_json):
    """
    Extract scoreboard data from match_data.json structure.
    
    Args:
        match_data_json: Dictionary containing match data
        
    Returns:
        List of scoreboard dictionaries (one per innings)
    """
    all_innings_scoreboards = []
    
    # Get innings from the nested structure
    innings_list = match_data_json.get("match_data", {}).get("innings", [])
    
    for inning_raw in innings_list:
        # Clean team name - remove non-breaking spaces and extra info
        team_name = inning_raw['name'].split('(')[0].strip()
        team_name = team_name.replace("\u00a0", " ").strip()
        
        scoreboard = {
            "name": team_name,
            "batting_entries": [],
            "extras": {
                "label": "",  # e.g., "Extras (lb 8, w 11)"
                "value": 0    # e.g., 19
            },
            "total_score": "",
            "overs": "20.0"  # Default for T20
        }

        total_runs_from_players = 0

        # Process batting entries
        for entry in inning_raw['batting']:
            if "player" in entry:
                player_name = entry['player']
                player_runs = int(entry['runs'])
                
                # Handle strike rate - convert '-' to 0.0
                strike_rate_str = entry['strike_rate']
                strike_rate = 0.0 if strike_rate_str == '-' else float(strike_rate_str)
                
                scoreboard["batting_entries"].append({
                    "player": player_name,
                    "dismissal_status": "not out",  # Default, can be enhanced
                    "dismissal_bowler": "",
                    "runs": player_runs,
                    "balls": int(entry['balls']),
                    "fours": int(entry['fours']),
                    "sixes": int(entry['sixes']),
                    "strike_rate": strike_rate
                })
                total_runs_from_players += player_runs
                
            elif "Extras" in entry:
                # Format: "Extras(b 4, lb 5, nb 1, w 4)14(b 4, lb 5, nb 1, w 4)"
                extras_text = entry['Extras']
                
                # Extract the breakdown and total
                match = re.search(r'Extras\((.*?)\)(\d+)', extras_text)
                if match:
                    breakdown = match.group(1)
                    extras_value = int(match.group(2))
                    scoreboard["extras"]["label"] = f"Extras ({breakdown})"
                    scoreboard["extras"]["value"] = extras_value
                else:
                    # Fallback
                    scoreboard["extras"]["label"] = "Extras"
                    scoreboard["extras"]["value"] = 0

        # Calculate total score
        total_extras = scoreboard["extras"]["value"]
        scoreboard["total_score"] = str(total_runs_from_players + total_extras)

        all_innings_scoreboards.append(scoreboard)
    
    return all_innings_scoreboards


if __name__ == "__main__":
    # Test with example match data
    import sys
    
    if len(sys.argv) > 1:
        match_data_path = sys.argv[1]
    else:
        match_data_path = '../commentaries/match_22_KXIP_vs_KKR/match_data.json'
    
    try:
        with open(match_data_path, 'r', encoding='utf-8') as f:
            ipl_json = json.load(f)
            team_scoreboards = extract_scoreboard_data(ipl_json)
            print(json.dumps(team_scoreboards, indent=2))
    except FileNotFoundError:
        print(f"Error: File not found: {match_data_path}")
    except Exception as e:
        print(f"Error: {e}")