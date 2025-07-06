import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

# Spotify API credentials
CLIENT_ID = '3e48c9a85a564cf9b2ec0e64298c5ad0'
CLIENT_SECRET = '4de91519fac7471fa7a7bc3f1bc39991'
REDIRECT_URI = 'http://127.0.0.1:8000/callback'
SCOPE = 'user-top-read user-read-recently-played'

def setup_spotify():
    """Initialize Spotify client"""
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def setup_database():
    """Create SQLite database for listening trends"""
    conn = sqlite3.connect('../outputs/listening_trends.db')
    cursor = conn.cursor()
    
    # Main tracks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracks (
        track_id TEXT,
        track_name TEXT NOT NULL,
        artist_name TEXT NOT NULL,
        album_name TEXT,
        release_date TEXT,
        popularity INTEGER,
        duration_ms INTEGER,
        explicit BOOLEAN,
        time_range TEXT NOT NULL,
        rank_position INTEGER,
        collected_date TEXT,
        spotify_url TEXT,
        PRIMARY KEY (track_id, time_range)
    )
    ''')
    
    # Artists table for easier querying
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artists (
        artist_name TEXT,
        time_range TEXT,
        track_count INTEGER,
        total_popularity INTEGER,
        avg_rank REAL,
        collected_date TEXT,
        PRIMARY KEY (artist_name, time_range)
    )
    ''')
    
    conn.commit()
    return conn

def fetch_listening_data(sp, conn):
    """Fetch top tracks from all time periods"""
    time_periods = {
        'short_term': 'Last 4 weeks',
        'medium_term': 'Last 6 months', 
        'long_term': 'Several years'
    }
    
    cursor = conn.cursor()
    collected_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("🎵 FETCHING LISTENING DATA FROM SPOTIFY")
    print("="*50)
    
    total_tracks = 0
    
    for time_range, description in time_periods.items():
        print(f"\n📊 Fetching top tracks for {description}...")
        
        try:
            # Get top tracks for this time period
            tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
            
            period_tracks = 0
            artist_stats = {}
            
            for rank, track in enumerate(tracks['items'], 1):
                # Insert track data
                cursor.execute('''
                INSERT OR REPLACE INTO tracks (
                    track_id, track_name, artist_name, album_name, 
                    release_date, popularity, duration_ms, explicit,
                    time_range, rank_position, collected_date, spotify_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    track['id'],
                    track['name'],
                    track['artists'][0]['name'],
                    track['album']['name'],
                    track['album']['release_date'],
                    track['popularity'],
                    track['duration_ms'],
                    track['explicit'],
                    time_range,
                    rank,
                    collected_date,
                    track['external_urls']['spotify']
                ))
                
                # Track artist stats
                artist = track['artists'][0]['name']
                if artist not in artist_stats:
                    artist_stats[artist] = {
                        'count': 0,
                        'total_pop': 0,
                        'ranks': []
                    }
                
                artist_stats[artist]['count'] += 1
                artist_stats[artist]['total_pop'] += track['popularity']
                artist_stats[artist]['ranks'].append(rank)
                
                period_tracks += 1
            
            # Insert artist summary data
            for artist, stats in artist_stats.items():
                avg_rank = sum(stats['ranks']) / len(stats['ranks'])
                cursor.execute('''
                INSERT OR REPLACE INTO artists (
                    artist_name, time_range, track_count, 
                    total_popularity, avg_rank, collected_date
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    artist,
                    time_range,
                    stats['count'],
                    stats['total_pop'],
                    avg_rank,
                    collected_date
                ))
            
            print(f"   ✅ {period_tracks} tracks collected")
            total_tracks += period_tracks
            
        except Exception as e:
            print(f"   ❌ Error fetching {time_range}: {e}")
    
    conn.commit()
    print(f"\n🎉 Total tracks collected: {total_tracks}")
    return total_tracks

def print_listening_summary(conn):
    """Print comprehensive listening trends summary"""
    cursor = conn.cursor()
    
    print(f"\n🎵 LISTENING TRENDS SUMMARY")
    print("="*50)
    
    # Basic stats
    cursor.execute("SELECT COUNT(*) FROM tracks")
    total_tracks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT artist_name) FROM tracks")
    total_artists = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT track_name) FROM tracks")
    unique_songs = cursor.fetchone()[0]
    
    print(f"\n📊 OVERVIEW:")
    print(f"   • Total track entries: {total_tracks}")
    print(f"   • Unique songs: {unique_songs}")
    print(f"   • Unique artists: {total_artists}")
    
    # Top artists overall
    cursor.execute('''
    SELECT artist_name, SUM(track_count) as total_tracks,
           COUNT(DISTINCT time_range) as periods,
           AVG(avg_rank) as overall_avg_rank
    FROM artists
    GROUP BY artist_name
    ORDER BY total_tracks DESC
    LIMIT 10
    ''')
    
    print(f"\n🎤 TOP ARTISTS OVERALL:")
    for artist, tracks, periods, avg_rank in cursor.fetchall():
        consistency_emoji = "🔥" if periods == 3 else "💫" if periods == 2 else "⭐"
        print(f"   {consistency_emoji} {artist}: {tracks} tracks | {periods} periods | Avg rank: {avg_rank:.1f}")
    
    # Top artists by period
    time_labels = {
        'short_term': '🔥 Last 4 weeks',
        'medium_term': '📅 Last 6 months',
        'long_term': '⏳ Several years'
    }
    
    for time_range, label in time_labels.items():
        cursor.execute('''
        SELECT artist_name, track_count, avg_rank 
        FROM artists 
        WHERE time_range = ? 
        ORDER BY track_count DESC 
        LIMIT 5
        ''', (time_range,))
        
        print(f"\n{label}:")
        for artist, track_count, avg_rank in cursor.fetchall():
            print(f"   • {artist}: {track_count} tracks (avg rank: {avg_rank:.1f})")

def print_advanced_analysis(conn):
    """Print advanced statistical analysis of listening trends"""
    print("\n🔬 ADVANCED TREND ANALYSIS")
    print("="*50)
    
    tracks_df = pd.read_sql_query("SELECT * FROM tracks", conn)
    
    if tracks_df.empty:
        print("No data available for analysis.")
        return
    
    # 1. Song Survival Analysis
    print("\n📈 SONG SURVIVAL ANALYSIS:")
    song_survival = tracks_df.groupby(['track_name', 'artist_name']).agg({
        'time_range': lambda x: list(x.unique()),
        'rank_position': ['mean', 'min', 'max'],
        'popularity': 'mean'
    }).round(2)
    
    song_survival.columns = ['periods', 'avg_rank', 'best_rank', 'worst_rank', 'avg_popularity']
    song_survival['period_count'] = song_survival['periods'].apply(len)
    song_survival['rank_consistency'] = song_survival['worst_rank'] - song_survival['best_rank']
    
    survivors = song_survival[song_survival['period_count'] > 1].sort_values(['period_count', 'avg_rank'], ascending=[False, True])
    
    print("Top Songs by Longevity:")
    for i, (song_artist, data) in enumerate(survivors.head(10).iterrows(), 1):
        track_name, artist_name = song_artist
        periods_str = ' → '.join(data['periods'])
        print(f"   {i:2d}. '{track_name}' by {artist_name}")
        print(f"       Periods: {periods_str}")
        print(f"       Avg Rank: {data['avg_rank']:.1f} | Consistency: ±{data['rank_consistency']:.0f}")
        print(f"       Popularity: {data['avg_popularity']:.0f}")
    
    # 2. Artist Evolution Analysis
    print(f"\n🎤 ARTIST EVOLUTION ANALYSIS:")
    artist_trends = {}
    for artist in tracks_df['artist_name'].unique():
        artist_data = tracks_df[tracks_df['artist_name'] == artist]
        if len(artist_data['time_range'].unique()) > 1:
            period_order = {'long_term': 1, 'medium_term': 2, 'short_term': 3}
            artist_data = artist_data.copy()
            artist_data['period_num'] = artist_data['time_range'].map(period_order)
            
            if len(artist_data) > 1:
                X = artist_data[['period_num']].values
                y = artist_data['rank_position'].values
                
                try:
                    reg = LinearRegression().fit(X, y)
                    trend_slope = reg.coef_[0]
                    artist_trends[artist] = {
                        'slope': trend_slope,
                        'periods': len(artist_data['time_range'].unique()),
                        'avg_rank': artist_data['rank_position'].mean(),
                        'track_count': len(artist_data)
                    }
                except:
                    pass
    
    improving_artists = sorted(
        [(k, v) for k, v in artist_trends.items() if v['slope'] < -1],
        key=lambda x: x[1]['slope']
    )
    declining_artists = sorted(
        [(k, v) for k, v in artist_trends.items() if v['slope'] > 1],
        key=lambda x: x[1]['slope'], reverse=True
    )
    
    if improving_artists:
        print("Artists with Improving Trends (getting better ranks over time):")
        for i, (artist, data) in enumerate(improving_artists[:5], 1):
            print(f"   {i}. {artist}: Trend slope {data['slope']:.2f} (avg rank: {data['avg_rank']:.1f})")
    
    if declining_artists:
        print("Artists with Declining Trends (getting worse ranks over time):")
        for i, (artist, data) in enumerate(declining_artists[:5], 1):
            print(f"   {i}. {artist}: Trend slope {data['slope']:.2f} (avg rank: {data['avg_rank']:.1f})")
    
    # 3. Song Persistence Analysis
    print(f"\n🔮 SONG PERSISTENCE ANALYSIS:")
    tracks_features = tracks_df.copy()
    tracks_features['duration_minutes'] = tracks_features['duration_ms'] / 60000
    tracks_features['release_year'] = pd.to_datetime(tracks_features['release_date'], errors='coerce').dt.year
    tracks_features['song_age'] = datetime.now().year - tracks_features['release_year']
    
    song_persistence = tracks_features.groupby(['track_name', 'artist_name']).agg({
        'time_range': lambda x: len(x.unique()),
        'popularity': 'mean',
        'duration_minutes': 'mean',
        'song_age': 'mean',
        'rank_position': 'mean'
    })
    
    song_persistence['is_persistent'] = (song_persistence['time_range'] > 1).astype(int)
    
    total_unique_songs = len(song_persistence)
    persistent_songs = song_persistence['is_persistent'].sum()
    persistence_rate = persistent_songs / total_unique_songs * 100
    
    print(f"   • Total unique songs: {total_unique_songs}")
    print(f"   • Persistent songs (>1 period): {persistent_songs}")
    print(f"   • Persistence rate: {persistence_rate:.1f}%")
    
    persistent_data = song_persistence[song_persistence['is_persistent'] == 1]
    non_persistent_data = song_persistence[song_persistence['is_persistent'] == 0]
    
    if len(persistent_data) > 0 and len(non_persistent_data) > 0:
        print(f"\n   Characteristics of Persistent vs Non-Persistent Songs:")
        print(f"   • Average popularity: {persistent_data['popularity'].mean():.1f} vs {non_persistent_data['popularity'].mean():.1f}")
        print(f"   • Average duration: {persistent_data['duration_minutes'].mean():.1f} vs {non_persistent_data['duration_minutes'].mean():.1f} minutes")
        print(f"   • Average age: {persistent_data['song_age'].mean():.1f} vs {non_persistent_data['song_age'].mean():.1f} years")
        print(f"   • Average rank: {persistent_data['rank_position'].mean():.1f} vs {non_persistent_data['rank_position'].mean():.1f}")
    
    # 4. Genre and Era Analysis
    print(f"\n🎼 RELEASE ERA ANALYSIS:")
    tracks_features_clean = tracks_features.dropna(subset=['release_year'])
    
    def categorize_era(year):
        if year < 1980:
            return "Classic (Pre-1980)"
        elif year < 1990:
            return "80s"
        elif year < 2000:
            return "90s"
        elif year < 2010:
            return "2000s"
        elif year < 2020:
            return "2010s"
        else:
            return "2020s+"
    
    tracks_features_clean['era'] = tracks_features_clean['release_year'].apply(categorize_era)
    era_analysis = tracks_features_clean.groupby('era').agg({
        'track_name': 'count',
        'popularity': 'mean',
        'rank_position': 'mean',
        'duration_minutes': 'mean'
    }).round(2)
    
    era_analysis.columns = ['track_count', 'avg_popularity', 'avg_rank', 'avg_duration']
    era_analysis = era_analysis.sort_values('track_count', ascending=False)
    
    print("Your music taste by era:")
    for era, data in era_analysis.iterrows():
        print(f"   • {era}: {data['track_count']} tracks")
        print(f"     Avg popularity: {data['avg_popularity']:.0f} | Avg rank: {data['avg_rank']:.1f} | Avg duration: {data['avg_duration']:.1f}min")
    
    print("\n✅ Advanced analysis completed!")

def export_data(conn):
    """Export data to CSV files"""
    tracks_df = pd.read_sql_query("SELECT * FROM tracks", conn)
    artists_df = pd.read_sql_query("SELECT * FROM artists", conn)
    
    tracks_df.to_csv('spotify_tracks_data.csv', index=False)
    artists_df.to_csv('spotify_artists_data.csv', index=False)
    
    print(f"📁 Data export completed:")
    print(f"   • spotify_tracks_data.csv ({len(tracks_df)} track entries)")
    print(f"   • spotify_artists_data.csv ({len(artists_df)} artist entries)")

def main():
    """Main application for data analysis and text output"""
    print("🎵 SPOTIFY DATA ANALYSIS - TEXT REPORTS")
    print("="*50)
    
    # Setup
    try:
        sp = setup_spotify()
        conn = setup_database()
        
        # Get user info
        user = sp.current_user()
        print(f"Connected as: {user['display_name']} ({user['id']})")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return
    
    while True:
        print(f"\n📋 MAIN MENU - DATA ANALYSIS")
        print("1. Fetch new listening data from Spotify")
        print("2. Show listening summary")
        print("3. Run advanced trend analysis")
        print("4. Export data to CSV")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            fetch_listening_data(sp, conn)
            
        elif choice == "2":
            print_listening_summary(conn)
            
        elif choice == "3":
            print_advanced_analysis(conn)
            
        elif choice == "4":
            export_data(conn)
            
        elif choice == "5":
            conn.close()
            print("Goodbye! 🎵")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
