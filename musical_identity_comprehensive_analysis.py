#!/usr/bin/env python3
"""
Comprehensive Musical Identity Analysis
Analyzes Spotify Wrapped data for musical identity formation patterns from 2020-2025
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from collections import Counter
import numpy as np
import os

def load_data():
    """Load and preprocess the Spotify data"""
    print("📂 Loading Spotify Wrapped data...")
    try:
        # Load the new CSV file from data folder
        df = pd.read_csv('../data/Spotify_data.csv')
        
        # Clean up any whitespace issues
        df['artist_name'] = df['artist_name'].str.strip()
        df['dimension'] = df['dimension'].str.strip()
        
        print(f"✅ Loaded {len(df)} songs from {df['year'].min()}-{df['year'].max()}")
        print(f"📊 Years: {sorted(df['year'].unique())}")
        print(f"🎤 Total unique artists: {df['artist_name'].nunique()}")
        return df
    except FileNotFoundError:
        print("❌ Error: Spotify_data.csv not found!")
        return None

def create_artist_diversity_analysis(df):
    """Create artist diversity visualization"""
    print("🎨 Creating artist diversity analysis...")
    
    # Calculate unique artists per year
    diversity_data = df.groupby('year')['artist_name'].nunique().reset_index()
    diversity_data.columns = ['year', 'unique_artists']
    
    # Create the visualization
    fig = go.Figure()
    
    # Add line chart
    fig.add_trace(go.Scatter(
        x=diversity_data['year'],
        y=diversity_data['unique_artists'],
        mode='lines+markers',
        line=dict(color='#1DB954', width=4),
        marker=dict(size=12, color='#1DB954', symbol='circle'),
        name='Unique Artists',
        hovertemplate='<b>%{x}</b><br>Unique Artists: %{y}<extra></extra>'
    ))
    
    # Add bar chart overlay
    fig.add_trace(go.Bar(
        x=diversity_data['year'],
        y=diversity_data['unique_artists'],
        opacity=0.3,
        marker_color='#1DB954',
        name='Artist Count',
        showlegend=False,
        hovertemplate='<b>%{x}</b><br>Unique Artists: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '🎵 Musical Diversity Evolution: Unique Artists Per Year',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#191414'}
        },
        xaxis_title='Year',
        yaxis_title='Number of Unique Artists',
        template='plotly_white',
        height=600,
        font=dict(size=14),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Add annotations for key insights
    max_year = diversity_data.loc[diversity_data['unique_artists'].idxmax()]
    min_year = diversity_data.loc[diversity_data['unique_artists'].idxmin()]
    
    fig.add_annotation(
        x=max_year['year'], y=max_year['unique_artists'],
        text=f"Most Diverse<br>{max_year['unique_artists']} artists",
        showarrow=True, arrowhead=2, arrowcolor='green',
        bgcolor='lightgreen', bordercolor='green'
    )
    
    fig.add_annotation(
        x=min_year['year'], y=min_year['unique_artists'],
        text=f"Least Diverse<br>{min_year['unique_artists']} artists",
        showarrow=True, arrowhead=2, arrowcolor='red',
        bgcolor='lightcoral', bordercolor='red'
    )
    
    # Save the plot to visualizations folder
    pyo.plot(fig, filename='../visualizations/artist_diversity_evolution.html', auto_open=False)
    return diversity_data

def create_genre_breakdown_analysis(df):
    """Create genre breakdown visualization"""
    print("🎭 Creating genre breakdown analysis...")
    
    # Calculate genre percentages by year
    genre_data = df.groupby(['year', 'dimension']).size().reset_index(name='count')
    total_by_year = df.groupby('year').size().reset_index(name='total')
    genre_data = genre_data.merge(total_by_year, on='year')
    genre_data['percentage'] = (genre_data['count'] / genre_data['total']) * 100
    
    # Create stacked bar chart
    fig = px.bar(
        genre_data,
        x='year',
        y='percentage',
        color='dimension',
        title='🎨 Genre/Dimension Breakdown Evolution (2020-2025)',
        labels={'percentage': 'Percentage (%)', 'year': 'Year', 'dimension': 'Genre/Dimension'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        title={
            'text': '🎨 Genre/Dimension Breakdown Evolution (2020-2025)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#191414'}
        },
        height=600,
        template='plotly_white',
        font=dict(size=14),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Save the plot
    pyo.plot(fig, filename='../visualizations/genre_breakdown_evolution.html', auto_open=False)
    return genre_data

def create_artist_leaderboard_analysis(df):
    """Create artist leaderboard visualizations for each year"""
    print("🏆 Creating artist leaderboard analysis...")
    
    years = sorted(df['year'].unique())
    
    # Create subplots for each year
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[f'{year} Top Artists' for year in years],
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    colors = ['#1DB954', '#1ed760', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
    
    for i, year in enumerate(years):
        year_data = df[df['year'] == year]
        artist_counts = year_data['artist_name'].value_counts().head(10)
        
        row = (i // 3) + 1
        col = (i % 3) + 1
        
        fig.add_trace(
            go.Bar(
                x=artist_counts.values,
                y=artist_counts.index,
                orientation='h',
                marker_color=colors[i],
                name=f'{year}',
                showlegend=False,
                text=artist_counts.values,
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Songs: %{x}<extra></extra>'
            ),
            row=row, col=col
        )
        
        fig.update_yaxes(title_text="Artists", row=row, col=col)
        fig.update_xaxes(title_text="Number of Songs", row=row, col=col)
    
    fig.update_layout(
        title={
            'text': '🏆 Artist Leaderboards by Year: Top 10 Artists Each Year',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#191414'}
        },
        height=800,
        template='plotly_white',
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Save the plot
    pyo.plot(fig, filename='../visualizations/artist_leaderboard_by_year.html', auto_open=False)
    
    return fig

def create_artist_persistence_analysis(df):
    """Create artist persistence analysis"""
    print("📈 Creating artist persistence analysis...")
    
    # Calculate how many years each artist appears
    artist_years = df.groupby('artist_name')['year'].nunique().reset_index()
    artist_years.columns = ['artist_name', 'years_present']
    
    # Also get total songs per artist
    artist_songs = df.groupby('artist_name').size().reset_index(name='total_songs')
    
    # Merge the data
    persistence_data = artist_years.merge(artist_songs, on='artist_name')
    persistence_data = persistence_data.sort_values(['years_present', 'total_songs'], ascending=[False, False])
    
    # Take top 20 most persistent artists
    top_persistent = persistence_data.head(20)
    
    # Create the visualization
    fig = go.Figure()
    
    # Add bars colored by number of years
    colors = ['#ff4444' if x == 6 else '#ff8800' if x == 5 else '#ffdd00' if x == 4 else 
              '#88dd00' if x == 3 else '#00dd88' if x == 2 else '#0088dd' 
              for x in top_persistent['years_present']]
    
    fig.add_trace(go.Bar(
        x=top_persistent['years_present'],
        y=top_persistent['artist_name'],
        orientation='h',
        marker_color=colors,
        text=[f"{years} years, {songs} songs" for years, songs in 
              zip(top_persistent['years_present'], top_persistent['total_songs'])],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Years Present: %{x}<br>Total Songs: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '🎯 Artist Persistence: Artists Ranked by Years in Top 50',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#191414'}
        },
        xaxis_title='Number of Years Present (2020-2025)',
        yaxis_title='Artist',
        height=800,
        template='plotly_white',
        font=dict(size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Add color legend
    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.02, y=1,
        text="<b>Years Present:</b><br>🔴 6 years<br>🟠 5 years<br>🟡 4 years<br>🟢 3 years<br>🔵 2 years<br>🔷 1 year",
        showarrow=False,
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1
    )
    
    # Save the plot
    pyo.plot(fig, filename='../visualizations/artist_persistence_analysis.html', auto_open=False)
    
    return persistence_data

def print_insights(df, diversity_data, persistence_data):
    """Print key insights from the analysis"""
    print("\n🔍 KEY INSIGHTS:")
    
    # Diversity insights
    max_diversity = diversity_data.loc[diversity_data['unique_artists'].idxmax()]
    min_diversity = diversity_data.loc[diversity_data['unique_artists'].idxmin()]
    print(f"   🎵 Most diverse year: {max_diversity['year']} ({max_diversity['unique_artists']} unique artists)")
    print(f"   🎵 Least diverse year: {min_diversity['year']} ({min_diversity['unique_artists']} unique artists)")
    
    # Genre insights by year
    print(f"   🎭 Dominant genres by year:")
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year]
        top_genre = year_data['dimension'].value_counts().iloc[0]
        top_genre_name = year_data['dimension'].value_counts().index[0]
        percentage = (top_genre / len(year_data)) * 100
        print(f"      {year}: {top_genre_name} ({percentage:.1f}%)")
    
    # Persistence insights
    most_persistent = persistence_data.iloc[0]
    all_years_artists = persistence_data[persistence_data['years_present'] == 6]
    print(f"   🎯 Most persistent artist: {most_persistent['artist_name']} ({most_persistent['years_present']} years, {most_persistent['total_songs']} total songs)")
    
    if len(all_years_artists) > 0:
        print(f"   🏆 Artists in ALL years: {', '.join(all_years_artists['artist_name'].tolist())}")
    else:
        print(f"   🏆 No artists appear in all 6 years")

def main():
    """Main analysis function"""
    print("🎵 MUSICAL IDENTITY COMPREHENSIVE ANALYSIS")
    print("============================================================")
    print("Analyzing your 6-year Spotify Wrapped data for identity formation patterns")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    print(f"\n🎵 CREATING COMPREHENSIVE MUSICAL IDENTITY ANALYSIS")
    print("============================================================")
    
    # Create all visualizations
    diversity_data = create_artist_diversity_analysis(df)
    genre_data = create_genre_breakdown_analysis(df)
    create_artist_leaderboard_analysis(df)
    persistence_data = create_artist_persistence_analysis(df)
    
    print(f"\n✅ Individual visualizations saved:")
    print(f"   📊 ../visualizations/artist_diversity_evolution.html")
    print(f"   🎨 ../visualizations/genre_breakdown_evolution.html")
    print(f"   🏆 ../visualizations/artist_leaderboard_by_year.html")
    print(f"   🎯 ../visualizations/artist_persistence_analysis.html")
    
    # Print insights
    print_insights(df, diversity_data, persistence_data)
    
    print(f"\n============================================================")
    print(f"🎯 ANALYSIS COMPLETE!")
    print(f"📊 Generated 4 comprehensive visualizations analyzing your musical identity evolution")
    print(f"🔍 Key research questions addressed:")
    print(f"   • Musical diversity trends over formative years (2020-2025)")
    print(f"   • Genre/dimension shifts during identity formation")
    print(f"   • Artist loyalty and consistency patterns")
    print(f"   • Period-based musical evolution")

if __name__ == "__main__":
    main()
