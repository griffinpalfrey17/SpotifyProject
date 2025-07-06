#!/usr/bin/env python3
"""
Historical Spotify Data Collector
=================================

This script should be run regularly (e.g., monthly) to build up
a true historical dataset of your listening preferences over time.

Each run collects your current Top 50 tracks and stores them with
a timestamp, allowing you to build up real historical trends.

Usage:
- Run this script monthly/weekly to collect data points
- After several collection periods, you'll have real historical data
- Then you can create meaningful year-over-year comparisons

Setup:
1. Make sure you have spotify_data_analysis.py working
2. Run this script regularly to build historical dataset
3. Use the collected data for true temporal analysis
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
import os
import sys
import warnings
warnings.filterwarnings('ignore')

def setup_historical_database():
    """Create or connect to historical data database"""
    conn = sqlite3.connect('spotify_historical_data.db')
    
    # Create tables for historical data
    conn.execute('''
    CREATE TABLE IF NOT EXISTS historical_tracks (
        collection_date TEXT,
        collection_month TEXT,
        collection_year INTEGER,
        track_id TEXT,
        track_name TEXT,
        artist_name TEXT,
        album_name TEXT,
        release_date TEXT,
        popularity INTEGER,
        duration_ms INTEGER,
        explicit BOOLEAN,
        time_range TEXT,
        rank_position INTEGER,
        spotify_url TEXT,
        PRIMARY KEY (collection_date, track_id, time_range)
    )
    ''')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS historical_artists (
        collection_date TEXT,
        collection_month TEXT,
        collection_year INTEGER,
        artist_name TEXT,
        time_range TEXT,
        track_count INTEGER,
        total_popularity INTEGER,
        avg_rank REAL,
        PRIMARY KEY (collection_date, artist_name, time_range)
    )
    ''')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS collection_log (
        collection_date TEXT PRIMARY KEY,
        collection_timestamp TEXT,
        tracks_collected INTEGER,
        artists_collected INTEGER,
        notes TEXT
    )
    ''')
    
    conn.commit()
    return conn

def collect_current_data():
    """Collect current data from the main database"""
    try:
        conn = sqlite3.connect('../outputs/listening_trends.db')
        
        tracks_df = pd.read_sql_query("""
            SELECT * FROM tracks 
            ORDER BY time_range, rank_position
        """, conn)
        
        artists_df = pd.read_sql_query("""
            SELECT * FROM artists 
            ORDER BY time_range, track_count DESC
        """, conn)
        
        conn.close()
        
        if tracks_df.empty:
            print("❌ No data found in main database!")
            print("💡 Run spotify_data_analysis.py first to fetch current data")
            return None, None
            
        return tracks_df, artists_df
        
    except Exception as e:
        print(f"❌ Error loading current data: {e}")
        return None, None

def store_historical_data(tracks_df, artists_df):
    """Store current data as a historical data point"""
    conn = setup_historical_database()
    
    today = date.today()
    collection_date = today.strftime('%Y-%m-%d')
    collection_month = today.strftime('%Y-%m')
    collection_year = today.year
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if we already have data for today
    existing = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM collection_log WHERE collection_date = ?",
        conn, params=[collection_date]
    )
    
    if existing.iloc[0]['count'] > 0:
        print(f"⚠️  Data for {collection_date} already exists!")
        print("🤔 Do you want to overwrite it? (y/n): ", end="")
        response = input().lower()
        if response != 'y':
            print("❌ Skipping data collection")
            conn.close()
            return False
        
        # Delete existing data for today
        conn.execute("DELETE FROM historical_tracks WHERE collection_date = ?", [collection_date])
        conn.execute("DELETE FROM historical_artists WHERE collection_date = ?", [collection_date])
        conn.execute("DELETE FROM collection_log WHERE collection_date = ?", [collection_date])
    
    # Add collection metadata to tracks (make a copy to avoid conflicts)
    tracks_clean = tracks_df.copy()
    # Remove any existing collection-related columns to avoid conflicts
    for col in ['collected_date', 'collection_date', 'collection_month', 'collection_year']:
        if col in tracks_clean.columns:
            tracks_clean = tracks_clean.drop(columns=[col])
    
    tracks_clean['collection_date'] = collection_date
    tracks_clean['collection_month'] = collection_month
    tracks_clean['collection_year'] = collection_year
    
    # Add collection metadata to artists (make a copy to avoid conflicts)
    artists_clean = artists_df.copy()
    # Remove any existing collection-related columns to avoid conflicts
    for col in ['collected_date', 'collection_date', 'collection_month', 'collection_year']:
        if col in artists_clean.columns:
            artists_clean = artists_clean.drop(columns=[col])
    
    artists_clean['collection_date'] = collection_date
    artists_clean['collection_month'] = collection_month
    artists_clean['collection_year'] = collection_year
    
    # Store historical data
    tracks_clean.to_sql('historical_tracks', conn, if_exists='append', index=False)
    artists_clean.to_sql('historical_artists', conn, if_exists='append', index=False)
    
    # Log the collection
    log_data = {
        'collection_date': collection_date,
        'collection_timestamp': timestamp,
        'tracks_collected': len(tracks_clean),
        'artists_collected': len(artists_clean),
        'notes': f'Automated collection - {len(tracks_clean)} tracks, {len(artists_clean)} artist entries'
    }
    
    pd.DataFrame([log_data]).to_sql('collection_log', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    
    return True

def show_collection_history():
    """Show the history of data collections"""
    try:
        conn = sqlite3.connect('spotify_historical_data.db')
        
        log_df = pd.read_sql_query("""
            SELECT collection_date, tracks_collected, artists_collected, notes
            FROM collection_log 
            ORDER BY collection_date DESC
        """, conn)
        
        if log_df.empty:
            print("📭 No historical data collected yet")
            print("💡 Run this script to start collecting historical data")
        else:
            print("📊 HISTORICAL DATA COLLECTION LOG")
            print("=" * 50)
            for _, row in log_df.iterrows():
                print(f"📅 {row['collection_date']}: {row['tracks_collected']} tracks, {row['artists_collected']} artists")
            
            print(f"\n✅ Total collection periods: {len(log_df)}")
            
            # Show time span
            if len(log_df) > 1:
                earliest = log_df['collection_date'].min()
                latest = log_df['collection_date'].max()
                print(f"📈 Data span: {earliest} to {latest}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading collection history: {e}")

def main():
    """Main function - collect and store historical data"""
    print("📊 HISTORICAL SPOTIFY DATA COLLECTOR")
    print("=" * 45)
    print("This script builds a true historical dataset of your listening preferences")
    print("Run it regularly (monthly/weekly) to track changes over time\n")
    
    # Show current collection history
    show_collection_history()
    print()
    
    # Check if current data is available
    print("🔍 Checking for current Spotify data...")
    tracks_df, artists_df = collect_current_data()
    
    if tracks_df is None:
        print("❌ Cannot collect historical data - no current data available")
        return
    
    print(f"✅ Found {len(tracks_df)} current tracks and {len(artists_df)} artist entries")
    
    # Store as historical data point
    print("💾 Storing current data as historical data point...")
    success = store_historical_data(tracks_df, artists_df)
    
    if success:
        today = date.today().strftime('%Y-%m-%d')
        print(f"✅ Successfully stored data for {today}")
        print("📈 Historical dataset updated!")
        print("\n💡 NEXT STEPS:")
        print("- Run this script regularly to build up historical data")
        print("- After several collection periods, you can analyze true trends")
        print("- Create meaningful year-over-year comparisons")
    else:
        print("❌ Failed to store historical data")

if __name__ == "__main__":
    main()
