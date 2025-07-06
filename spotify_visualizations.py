import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import webbrowser
import os
import warnings
warnings.filterwarnings('ignore')

"""
IMPORTANT DATA LIMITATION NOTICE:
=====================================
This script analyzes CURRENT listening preferences across different time windows,
NOT historical trends over time.

The data shows:
- short_term: Your current favorites from the last ~4 weeks
- medium_term: Your current favorites from the last ~6 months  
- long_term: Your current favorites from the last ~several years

All data was collected on the same dates (June 2025), so this does NOT show
how your preferences changed from 2020-2025. It shows different time windows
of your current listening patterns.

For true historical analysis, data would need to be collected over time.
=====================================
"""

def load_data():
    """Load data from the database"""
    try:
        conn = sqlite3.connect('../outputs/listening_trends.db')
        tracks_df = pd.read_sql_query("SELECT * FROM tracks", conn)
        artists_df = pd.read_sql_query("SELECT * FROM artists", conn)
        conn.close()
        
        if tracks_df.empty:
            print("❌ No data found! Please run spotify_data_analysis.py first to fetch data.")
            return None, None
        
        print(f"✅ Loaded {len(tracks_df)} track entries and {len(artists_df)} artist entries")
        return tracks_df, artists_df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None

def create_artist_visualizations(tracks_df, artists_df):
    """Create current listening preferences dashboard across different time windows"""
    print("🎨 Creating current listening preferences dashboard...")
    
    # Create interactive dashboard with 6 subplots
    # NOTE: These are NOT historical trends - they show current preferences across different time windows
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            '🔥 Current Top (4 weeks)', '📅 Recent Favorites (6 months)', '⏳ Long-term Preferences (several years)',
            '🔄 Cross-Window Consistency', '👑 Overall Current Top Artists', '� Time Window Comparison'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.08
    )
    
    time_labels = {
        'short_term': '🔥 Current (4 weeks)',
        'medium_term': '📅 Recent (6 months)',
        'long_term': '⏳ Long-term (several years)'
    }
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    # 1-3. Top Artists by Time Period (first row)
    for i, (time_range, label) in enumerate(time_labels.items()):
        period_artists = artists_df[artists_df['time_range'] == time_range].nlargest(10, 'track_count')
        
        if not period_artists.empty:
            col = i + 1
            
            fig.add_trace(
                go.Bar(
                    y=period_artists['artist_name'],
                    x=period_artists['track_count'],
                    orientation='h',
                    marker_color=colors[i],
                    name=f"Artists - {time_range}",
                    showlegend=False,
                    hovertemplate='<b>%{y}</b><br>Top Tracks: %{x}<br>Avg Rank: %{customdata:.1f}<extra></extra>',
                    customdata=period_artists['avg_rank']
                ),
                row=1, col=col
            )
    
    # 4. Artist Consistency (bottom left)
    consistency_query = '''
    SELECT artist_name, COUNT(DISTINCT time_range) as periods,
           SUM(track_count) as total_tracks,
           AVG(avg_rank) as avg_ranking
    FROM artists
    GROUP BY artist_name
    HAVING periods > 1
    ORDER BY periods DESC, total_tracks DESC
    LIMIT 12
    '''
    
    conn = sqlite3.connect('../outputs/listening_trends.db')
    consistency_df = pd.read_sql_query(consistency_query, conn)
    
    if not consistency_df.empty:
        scatter_colors = ['#FF6B6B' if p == 3 else '#4ECDC4' if p == 2 else '#45B7D1' 
                         for p in consistency_df['periods']]
        
        fig.add_trace(
            go.Bar(
                y=consistency_df['artist_name'],
                x=consistency_df['total_tracks'],
                orientation='h',
                marker_color=scatter_colors,
                name="Consistent Artists",
                showlegend=False,
                hovertemplate='<b>%{y}</b><br>Total Tracks: %{x}<br>Periods: %{customdata}P<br>Avg Rank: %{text:.1f}<extra></extra>',
                customdata=consistency_df['periods'],
                text=consistency_df['avg_ranking']
            ),
            row=2, col=1
        )
    
    # 5. Overall top artists (bottom middle)
    overall_query = '''
    SELECT artist_name, SUM(track_count) as total_tracks,
           COUNT(DISTINCT time_range) as periods,
           AVG(avg_rank) as overall_avg_rank
    FROM artists
    GROUP BY artist_name
    ORDER BY total_tracks DESC
    LIMIT 12
    '''
    
    overall_df = pd.read_sql_query(overall_query, conn)
    
    if not overall_df.empty:
        colors_map = {1: '#FF6B6B', 2: '#FFEAA7', 3: '#55A3FF'}
        bar_colors = [colors_map.get(p, '#96CEB4') for p in overall_df['periods']]
        
        fig.add_trace(
            go.Bar(
                y=overall_df['artist_name'],
                x=overall_df['total_tracks'],
                orientation='h',
                marker_color=bar_colors,
                name="Top Artists Overall",
                showlegend=False,
                hovertemplate='<b>%{y}</b><br>Total Tracks: %{x}<br>Periods: %{customdata}P<br>Avg Rank: %{text:.1f}<extra></extra>',
                customdata=overall_df['periods'],
                text=overall_df['overall_avg_rank']
            ),
            row=2, col=2
        )
    
    # 6. Artist ranking trends (bottom right)
    if not tracks_df.empty:
        artist_trends = {}
        for artist in tracks_df['artist_name'].unique():
            artist_data = tracks_df[tracks_df['artist_name'] == artist]
            if len(artist_data['time_range'].unique()) > 1:
                period_order = {'long_term': 1, 'medium_term': 2, 'short_term': 3}
                artist_data = artist_data.copy()
                artist_data['period_num'] = artist_data['time_range'].map(period_order)
                
                if len(artist_data) > 1:
                    try:
                        X = artist_data[['period_num']].values
                        y = artist_data['rank_position'].values
                        reg = LinearRegression().fit(X, y)
                        trend_slope = reg.coef_[0]
                        artist_trends[artist] = {
                            'slope': trend_slope,
                            'track_count': len(artist_data)
                        }
                    except:
                        pass
        
        if artist_trends:
            improving = [(k, v) for k, v in artist_trends.items() if v['slope'] < -1]
            declining = [(k, v) for k, v in artist_trends.items() if v['slope'] > 1]
            
            trend_artists = []
            trend_values = []
            trend_colors = []
            trend_directions = []
            
            for artist, data in sorted(improving, key=lambda x: x[1]['slope'])[:6]:
                trend_artists.append(f"{artist}")
                trend_values.append(abs(data['slope']))
                trend_colors.append('#4ECDC4')
                trend_directions.append('Improving ↗️')
            
            for artist, data in sorted(declining, key=lambda x: x[1]['slope'], reverse=True)[:6]:
                trend_artists.append(f"{artist}")
                trend_values.append(data['slope'])
                trend_colors.append('#FF6B6B')
                trend_directions.append('Declining ↘️')
            
            if trend_artists:
                fig.add_trace(
                    go.Bar(
                        y=trend_artists,
                        x=trend_values,
                        orientation='h',
                        marker_color=trend_colors,
                        name="Artist Trends",
                        showlegend=False,
                        hovertemplate='<b>%{y}</b><br>%{customdata}<br>Trend Strength: %{x:.1f}<extra></extra>',
                        customdata=trend_directions
                    ),
                    row=2, col=3
                )
    
    conn.close()
    
    # Update layout
    fig.update_layout(
        title="🎵 Current Spotify Listening Preferences Dashboard",
        height=800,
        template="plotly_dark",
        font=dict(size=10),
        showlegend=False
    )
    
    # Save and display
    html_file = "spotify_artist_visualizations.html"
    fig.write_html(html_file)
    print(f"📊 Saved interactive artist visualizations to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive dashboard")
    
    # Also show in the environment
    fig.show()

def create_song_dashboard(tracks_df):
    """Create interactive song analysis dashboard"""
    print("🎵 Creating interactive song dashboard...")
    
    # Create interactive Plotly dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Song Consistency Across Time Periods',
            'Popularity vs Duration Analysis',
            'Release Year Timeline',
            'Top Songs by Period'
        ),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "bar"}]],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # 1. Song Consistency Analysis
    consistency_query = '''
    SELECT track_name, artist_name, COUNT(DISTINCT time_range) as periods,
           AVG(popularity) as avg_popularity, AVG(rank_position) as avg_rank
    FROM tracks
    GROUP BY track_name, artist_name
    HAVING periods > 1
    ORDER BY periods DESC, avg_popularity DESC
    LIMIT 15
    '''
    
    conn = sqlite3.connect('../outputs/listening_trends.db')
    consistent_df = pd.read_sql_query(consistency_query, conn)
    
    if not consistent_df.empty:
        song_labels = [f"{row['track_name'][:25]}... - {row['artist_name'][:15]}" 
                      if len(row['track_name']) > 25 
                      else f"{row['track_name']} - {row['artist_name'][:15]}" 
                      for _, row in consistent_df.iterrows()]
        
        colors = ['#FF6B6B' if p == 3 else '#4ECDC4' if p == 2 else '#45B7D1' 
                 for p in consistent_df['periods']]
        
        fig.add_trace(
            go.Bar(
                y=song_labels,
                x=consistent_df['periods'],
                orientation='h',
                marker_color=colors,
                name='Consistent Songs',
                hovertemplate='<b>%{y}</b><br>Periods: %{x}<br>Avg Popularity: %{customdata}<extra></extra>',
                customdata=consistent_df['avg_popularity'].round(1)
            ),
            row=1, col=1
        )
    
    # 2. Popularity vs Duration
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    
    period_colors = {'short_term': '#FF6B6B', 'medium_term': '#4ECDC4', 'long_term': '#45B7D1'}
    
    for period in tracks_df['time_range'].unique():
        period_data = tracks_df[tracks_df['time_range'] == period]
        fig.add_trace(
            go.Scatter(
                x=period_data['duration_minutes'],
                y=period_data['popularity'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=period_colors[period],
                    opacity=0.7
                ),
                name=f"{period.replace('_', ' ').title()}",
                hovertemplate='<b>%{text}</b><br>Duration: %{x:.1f}min<br>Popularity: %{y}<extra></extra>',
                text=[f"{row['track_name']} - {row['artist_name']}" 
                     for _, row in period_data.iterrows()]
            ),
            row=1, col=2
        )
    
    # 3. Release Year Timeline
    year_data = tracks_df.groupby(['release_year', 'time_range']).agg({
        'popularity': 'mean',
        'track_name': 'count'
    }).reset_index()
    year_data.columns = ['release_year', 'time_range', 'avg_popularity', 'track_count']
    
    for period in year_data['time_range'].unique():
        period_year_data = year_data[year_data['time_range'] == period]
        fig.add_trace(
            go.Scatter(
                x=period_year_data['release_year'],
                y=period_year_data['avg_popularity'],
                mode='markers+lines',
                marker=dict(
                    size=period_year_data['track_count'] * 3,
                    color=period_colors[period],
                    opacity=0.7
                ),
                line=dict(color=period_colors[period], width=2),
                name=f"{period.replace('_', ' ').title()} Timeline",
                hovertemplate='<b>%{x}</b><br>Avg Popularity: %{y:.1f}<br>Track Count: %{customdata}<extra></extra>',
                customdata=period_year_data['track_count']
            ),
            row=2, col=1
        )
    
    # 4. Top Songs by Period
    top_songs_query = '''
    SELECT track_name, artist_name, time_range, rank_position, popularity
    FROM tracks
    WHERE rank_position <= 10
    ORDER BY time_range, rank_position
    '''
    
    top_songs_df = pd.read_sql_query(top_songs_query, conn)
    conn.close()
    
    for period in top_songs_df['time_range'].unique():
        period_songs = top_songs_df[top_songs_df['time_range'] == period]
        song_labels = [f"{row['track_name'][:20]}..." if len(row['track_name']) > 20 
                      else row['track_name'] for _, row in period_songs.iterrows()]
        
        fig.add_trace(
            go.Bar(
                y=song_labels,
                x=period_songs['popularity'],
                orientation='h',
                marker_color=period_colors[period],
                name=f"Top Songs - {period.replace('_', ' ').title()}",
                hovertemplate='<b>%{y}</b><br>Popularity: %{x}<br>Rank: %{customdata}<extra></extra>',
                customdata=[f"#{row['rank_position']}" for _, row in period_songs.iterrows()]
            ),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        title="🎵 Current Song Preferences Across Time Windows",
        height=800,
        showlegend=True,
        template="plotly_dark",
        font=dict(size=10)
    )
    
    # Save and display
    html_file = "spotify_song_dashboard.html"
    fig.write_html(html_file)
    print(f"📊 Saved interactive song dashboard to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive dashboard")
    
    # Also show in environment
    fig.show()

def create_advanced_visualizations(tracks_df, artists_df):
    """Create advanced trend analysis visualizations"""
    print("🔬 Creating advanced trend visualizations...")
    
    # Prepare data
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Song Persistence Analysis',
            'Artist Evolution Trends',
            'Era Distribution & Characteristics',
            'Ranking Consistency vs Popularity'
        ),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # 1. Song Persistence Analysis
    song_persistence = tracks_df.groupby(['track_name', 'artist_name']).agg({
        'time_range': lambda x: len(x.unique()),
        'popularity': 'mean',
        'duration_minutes': 'mean',
        'song_age': 'mean',
        'rank_position': 'mean'
    }).reset_index()
    
    song_persistence['is_persistent'] = (song_persistence['time_range'] > 1).astype(int)
    
    for persistent in [0, 1]:
        data = song_persistence[song_persistence['is_persistent'] == persistent]
        name = "Persistent" if persistent else "Non-Persistent"
        color = '#4ECDC4' if persistent else '#FF6B6B'
        
        # Clean data to remove NaN values
        clean_data = data.dropna(subset=['duration_minutes', 'popularity', 'song_age'])
        
        if not clean_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=clean_data['duration_minutes'],
                    y=clean_data['popularity'],
                    mode='markers',
                    marker=dict(
                        size=clean_data['song_age']/2,
                        color=color,
                        opacity=0.6
                    ),
                    name=f"{name} Songs",
                    hovertemplate='<b>%{text}</b><br>Duration: %{x:.1f}min<br>Popularity: %{y}<br>Age: %{customdata:.0f}yrs<extra></extra>',
                    text=[f"{row['track_name']} - {row['artist_name']}" for _, row in clean_data.iterrows()],
                    customdata=clean_data['song_age']
                ),
                row=1, col=1
            )
    
    # 2. Artist Evolution Trends
    artist_trends = {}
    for artist in tracks_df['artist_name'].unique():
        artist_data = tracks_df[tracks_df['artist_name'] == artist]
        if len(artist_data['time_range'].unique()) > 1:
            period_order = {'long_term': 1, 'medium_term': 2, 'short_term': 3}
            artist_data = artist_data.copy()
            artist_data['period_num'] = artist_data['time_range'].map(period_order)
            
            if len(artist_data) > 1:
                try:
                    X = artist_data[['period_num']].values
                    y = artist_data['rank_position'].values
                    reg = LinearRegression().fit(X, y)
                    trend_slope = reg.coef_[0]
                    artist_trends[artist] = trend_slope
                except:
                    pass
    
    if artist_trends:
        improving = [(k, v) for k, v in artist_trends.items() if v < -0.5][:8]
        declining = [(k, v) for k, v in artist_trends.items() if v > 0.5][:8]
        
        # Improving artists
        if improving:
            artists, slopes = zip(*improving)
            fig.add_trace(
                go.Bar(
                    y=list(artists),
                    x=[abs(s) for s in slopes],
                    orientation='h',
                    marker_color='#4ECDC4',
                    name='Improving Artists',
                    hovertemplate='<b>%{y}</b><br>Improvement Rate: %{x:.2f}<extra></extra>'
                ),
                row=1, col=2
            )
        
        # Declining artists
        if declining:
            artists, slopes = zip(*declining)
            fig.add_trace(
                go.Bar(
                    y=list(artists),
                    x=list(slopes),
                    orientation='h',
                    marker_color='#FF6B6B',
                    name='Declining Artists',
                    hovertemplate='<b>%{y}</b><br>Decline Rate: %{x:.2f}<extra></extra>'
                ),
                row=1, col=2
            )
    
    # 3. Era Distribution
    def categorize_era(year):
        if pd.isna(year):
            return "Unknown"
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
    
    tracks_df['era'] = tracks_df['release_year'].apply(categorize_era)
    era_analysis = tracks_df.groupby('era').agg({
        'track_name': 'count',
        'popularity': 'mean',
        'rank_position': 'mean'
    }).reset_index()
    
    era_analysis.columns = ['era', 'track_count', 'avg_popularity', 'avg_rank']
    era_analysis = era_analysis.sort_values('track_count', ascending=False)
    
    fig.add_trace(
        go.Bar(
            x=era_analysis['era'],
            y=era_analysis['track_count'],
            marker_color='#45B7D1',
            name='Track Count by Era',
            hovertemplate='<b>%{x}</b><br>Tracks: %{y}<br>Avg Popularity: %{customdata[0]:.0f}<br>Avg Rank: %{customdata[1]:.1f}<extra></extra>',
            customdata=list(zip(era_analysis['avg_popularity'], era_analysis['avg_rank']))
        ),
        row=2, col=1
    )
    
    # 4. Ranking Consistency vs Popularity
    song_stats = tracks_df.groupby(['track_name', 'artist_name']).agg({
        'rank_position': ['mean', 'std'],
        'popularity': 'mean',
        'time_range': lambda x: len(x.unique())
    }).reset_index()
    
    song_stats.columns = ['track_name', 'artist_name', 'avg_rank', 'rank_std', 'avg_popularity', 'periods']
    song_stats['rank_consistency'] = 1 / (song_stats['rank_std'] + 1)  # Higher = more consistent
    song_stats = song_stats.dropna()
    
    colors = ['#FF6B6B' if p == 3 else '#4ECDC4' if p == 2 else '#45B7D1' for p in song_stats['periods']]
    
    fig.add_trace(
        go.Scatter(
            x=song_stats['rank_consistency'],
            y=song_stats['avg_popularity'],
            mode='markers',
            marker=dict(
                size=song_stats['periods'] * 5,
                color=colors,
                opacity=0.7
            ),
            name='Song Performance',
            hovertemplate='<b>%{text}</b><br>Consistency: %{x:.2f}<br>Avg Popularity: %{y}<br>Periods: %{customdata}<extra></extra>',
            text=[f"{row['track_name']} - {row['artist_name']}" for _, row in song_stats.iterrows()],
            customdata=song_stats['periods']
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title="🔬 Current Listening Patterns Analysis (NOT Historical Trends)",
        height=900,
        showlegend=True,
        template="plotly_dark",
        font=dict(size=10)
    )
    
    # Save and display
    html_file = "spotify_advanced_visualizations.html"
    fig.write_html(html_file)
    print(f"📊 Saved advanced visualizations to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive dashboard")
    
    # Also show in environment
    fig.show()

def main():
    """Main visualization application"""
    print("🎨 SPOTIFY VISUALIZATION DASHBOARD")
    print("="*50)
    
    # Load data
    tracks_df, artists_df = load_data()
    if tracks_df is None:
        return
    
    while True:
        print(f"\n📊 INTERACTIVE VISUALIZATION MENU")
        print("1. Interactive artist trend visualizations (web dashboard)")
        print("2. Interactive song dashboard (web dashboard)")
        print("3. Advanced trend analysis visualizations (web dashboard)")
        print("4. Generate all interactive visualizations")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            create_artist_visualizations(tracks_df, artists_df)
            
        elif choice == "2":
            create_song_dashboard(tracks_df)
            
        elif choice == "3":
            create_advanced_visualizations(tracks_df, artists_df)
            
        elif choice == "4":
            print("🎨 Generating all interactive visualizations...")
            create_artist_visualizations(tracks_df, artists_df)
            create_song_dashboard(tracks_df)
            create_advanced_visualizations(tracks_df, artists_df)
            print("✅ All interactive visualizations generated and saved as HTML files!")
            
        elif choice == "5":
            print("Goodbye! 🎨")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
