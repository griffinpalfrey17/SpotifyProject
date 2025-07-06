#!/usr/bin/env python3
"""
Focused Artist Timeline Visualization
====================================
Creates a timeline showing specific artists' evolution over 2020-2025
"""

import pandas as pd
import plotly.graph_objects as go
import webbrowser
import os
import warnings
warnings.filterwarnings('ignore')

def create_focused_artist_timeline():
    """Create timeline for specific artists only"""
    print("🎵 Creating focused artist timeline...")
    
    # Load data
    try:
        df = pd.read_csv('../data/Spotify_data.csv')
        # Ensure proper data types
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
        # Remove any rows with invalid data
        df = df.dropna(subset=['year', 'rank'])
    except FileNotFoundError:
        print("❌ Error: Spotify_data.csv not found!")
        return
    
    # Focus on specific artists
    focus_artists = ['Zach Bryan', 'Morgan Wade', 'mike.', 'Bon Iver', 'Morgan Wallen']
    
    # Clean artist names and filter
    df['artist_name'] = df['artist_name'].str.strip()
    focused_df = df[df['artist_name'].isin(focus_artists)]
    
    if focused_df.empty:
        print("❌ No data found for the specified artists!")
        print(f"Available artists: {sorted(df['artist_name'].unique())}")
        return
    
    # Get all years
    years = sorted(df['year'].unique())
    print(f"📅 Years covered: {min(years)}-{max(years)}")
    print(f"🎤 Focus artists: {focus_artists}")
    
    # Create the line chart
    fig = go.Figure()
    
    # Color palette for each artist
    colors = {
        'Zach Bryan': '#9b59b6',
        'Morgan Wade': '#f39c12',
        'mike.': '#27ae60',
        'Bon Iver': '#3498db',
        'Morgan Wallen': '#e74c3c'
    }
    
    # Add a line for each focus artist
    for artist in focus_artists:
        artist_data = focused_df[focused_df['artist_name'] == artist]
        
        if artist_data.empty:
            print(f"⚠️  No data found for {artist}")
            continue
            
        # Create year-by-year data for this artist
        artist_years = []
        artist_scores = []
        
        for year in years:
            year_data = artist_data[artist_data['year'] == year]
            if not year_data.empty:
                # Use inverse rank (lower rank = higher on chart)
                # Count total songs for this artist this year
                song_count = len(year_data)
                # Average rank for this artist this year
                avg_rank = year_data['rank'].mean()
                # Convert to score: more songs = higher base, better average rank = bonus
                score = song_count + (51 - avg_rank) / 10  # Scale rank bonus
                artist_years.append(year)
                artist_scores.append(score)
            else:
                # Artist not in top list that year
                artist_years.append(year)
                artist_scores.append(0)
        
        # Only add line if artist has some listening data
        if sum(artist_scores) > 0:
            fig.add_trace(
                go.Scatter(
                    x=artist_years,
                    y=artist_scores,
                    mode='lines+markers',
                    name=artist,
                    line=dict(color=colors.get(artist, '#666666'), width=4),
                    marker=dict(size=10),
                    hovertemplate=f'<b>{artist}</b><br>Year: %{{x}}<br>Listening Score: %{{y:.1f}}<extra></extra>'
                )
            )
            
            max_score = max(artist_scores)
            max_year = artist_years[artist_scores.index(max_score)]
            print(f"✅ {artist}: Peak score {max_score:.1f} in {max_year}")
    
    # Update layout
    fig.update_layout(
        title={
            'text': "🎤 Musical Evolution: Key Artists Timeline (2020-2025)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#191414'}
        },
        xaxis_title="Year",
        yaxis_title="Listening Score (Songs + Rank Bonus)",
        height=600,
        template="plotly_white",
        font=dict(size=14),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Set axis ranges
    fig.update_xaxes(
        range=[min(years) - 0.5, max(years) + 0.5], 
        dtick=1,
        tickmode='linear'
    )
    
    # Add annotations for interesting patterns
    fig.add_annotation(
        text="Focus on 5 key artists<br>showing listening evolution",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1,
        font=dict(size=12)
    )
    
    # Save and display
    html_file = "../visualizations/spotify_wrapped_timeline.html"
    fig.write_html(html_file)
    print(f"\n📊 Saved focused timeline to: {html_file}")
    
    # Show summary
    print(f"\n📊 FOCUSED ARTIST SUMMARY:")
    for artist in focus_artists:
        artist_data = focused_df[focused_df['artist_name'] == artist]
        if not artist_data.empty:
            years_present = sorted(artist_data['year'].unique())
            total_songs = len(artist_data)
            print(f"   {artist}: {len(years_present)} years, {total_songs} total songs, years: {years_present}")
    
    return fig

if __name__ == "__main__":
    create_focused_artist_timeline()
