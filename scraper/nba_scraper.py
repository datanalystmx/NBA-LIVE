import requests
import json
import time
import os
from datetime import datetime
import pytz

PROXIES_LIST = [
    'http://pblneydf:j53331earxr3@31.59.20.176:6754',
    'http://pblneydf:j53331earxr3@23.95.150.145:6114',
    'http://pblneydf:j53331earxr3@198.23.239.134:6540',
    'http://pblneydf:j53331earxr3@45.38.107.97:6014',
    'http://pblneydf:j53331earxr3@107.172.163.27:6543',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com',
    'Accept': 'application/json',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
}

def get_proxy():
    for proxy in PROXIES_LIST:
        try:
            r = requests.get('https://ipv4.webshare.io/',
                proxies={'http': proxy, 'https': proxy}, timeout=8)
            if r.status_code < 500:
                return {'http': proxy, 'https': proxy}
        except:
            continue
    return None

PROXY = get_proxy()
print(f"Proxy: {'OK' if PROXY else 'Sin proxy'}")

def get_scoreboard():
    ct = pytz.timezone('America/Chicago')
    today = datetime.now(ct).strftime('%m/%d/%Y')
    url = f'https://stats.nba.com/stats/scoreboardv3?GameDate={today}&LeagueID=00&DayOffset=0'
    try:
        r = requests.get(url, headers=HEADERS, proxies=PROXY, timeout=15)
        data = r.json()
        games = data['scoreboard']['games']
        result = []
        for g in games:
            result.append({
                'game_id': g['gameId'],
                'status': g['gameStatus'],
                'status_text': g['gameStatusText'],
                'home': g['homeTeam']['teamTricode'],
                'away': g['awayTeam']['teamTricode'],
                'home_score': g['homeTeam']['score'],
                'away_score': g['awayTeam']['score'],
                'period': g['period'],
                'clock': g.get('gameClock', ''),
            })
        return result
    except Exception as e:
        print(f"Error scoreboard: {e}")
        return []

def get_boxscore_half(game_id, half='1stHalf'):
    url = f'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json'
    try:
        r = requests.get(url, headers=HEADERS, proxies=PROXY, timeout=15)
        data = r.json()
        game = data['game']
        players = []
        for team_key in ['homeTeam', 'awayTeam']:
            team = game[team_key]
            team_abbr = team['teamTricode']
            for p in team['players']:
                s = p.get('statistics', {})
                fg = s.get('fieldGoalsMade', 0)
                fga = s.get('fieldGoalsAttempted', 0)
                tp = s.get('threePointersMade', 0)
                tpa = s.get('threePointersAttempted', 0)
                players.append({
                    'game_id': game_id,
                    'half': half,
                    'team': team_abbr,
                    'player_id': p.get('personId'),
                    'name': p.get('name'),
                    'min': s.get('minutesCalculated', 'PT0M').replace('PT','').replace('M',''),
                    'pts': s.get('points', 0),
                    'reb': s.get('reboundsTotal', 0),
                    'oreb': s.get('reboundsOffensive', 0),
                    'dreb': s.get('reboundsDefensive', 0),
                    'ast': s.get('assists', 0),
                    'stl': s.get('steals', 0),
                    'blk': s.get('blocks', 0),
                    'pf': s.get('foulsPersonal', 0),
                    'tov': s.get('turnovers', 0),
                    'fgm': fg,
                    'fga': fga,
                    'fg_pct': round(fg/fga*100, 1) if fga > 0 else 0,
                    'tpm': tp,
                    'tpa': tpa,
                    'tp_pct': round(tp/tpa*100, 1) if tpa > 0 else 0,
                    'ftm': s.get('freeThrowsMade', 0),
                    'fta': s.get('freeThrowsAttempted', 0),
                    'plus_minus': s.get('plusMinusPoints', 0),
                })
        return players
    except Exception as e:
        print(f"Error boxscore {game_id}: {e}")
        return []

def main():
    print("=== NBA LIVE PROPS SCRAPER ===")
    games = get_scoreboard()
    print(f"Juegos hoy: {len(games)}")

    output = {
        'timestamp': datetime.now(pytz.timezone('America/Chicago')).isoformat(),
        'games': [],
    }

    for g in games:
        print(f"  {g['away']} vs {g['home']} | Status: {g['status']} | Period: {g['period']}")
        game_data = {**g, 'halftime_stats': [], 'live_stats': []}

        if g['status'] >= 2 and g['period'] >= 3:
            print(f"    → Jalando 1stHalf stats...")
            players = get_boxscore_half(g['game_id'], '1stHalf')
            game_data['halftime_stats'] = players
            print(f"    → {len(players)} jugadores")

        if g['status'] == 2:
            players_live = get_boxscore_half(g['game_id'], 'live')
            game_data['live_stats'] = players_live

        output['games'].append(game_data)
        time.sleep(0.5)

    os.makedirs('data', exist_ok=True)
    with open('data/live_games.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ data/live_games.json — {len(games)} juegos")

if __name__ == '__main__':
    main()
```

Abajo del editor donde dice **Commit changes** escribe:
```
add nba scraper
