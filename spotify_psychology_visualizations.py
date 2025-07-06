import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import webbrowser
import os
import warnings
warnings.filterwarnings('ignore')

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
        
        print(f"✅ Loaded {len(tracks_df)} track entries for psychology visualizations")
        return tracks_df, artists_df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None

def create_personality_radar_chart(tracks_df):
    """Create radar chart for musical personality dimensions"""
    print("🧠 Creating musical personality radar chart...")
    
    # Prepare data
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    # Calculate personality dimensions (same logic as psychology file)
    # 1. Reflective & Complex
    reflective_score = 0
    if tracks_df['song_age'].mean() > 15:
        reflective_score += 2
    elif tracks_df['song_age'].mean() > 8:
        reflective_score += 1
    
    if tracks_df['duration_minutes'].mean() > 4.5:
        reflective_score += 2
    elif tracks_df['duration_minutes'].mean() > 3.5:
        reflective_score += 1
    
    if tracks_df['popularity'].mean() < 70:
        reflective_score += 2
    elif tracks_df['popularity'].mean() < 80:
        reflective_score += 1
    
    # 2. Intense & Rebellious
    intense_score = 0
    explicit_rate = tracks_df['explicit'].mean() * 100
    if explicit_rate > 30:
        intense_score += 2
    elif explicit_rate > 15:
        intense_score += 1
    
    consistency_rate = len(tracks_df.groupby(['track_name', 'artist_name']).filter(lambda x: len(x) > 1)) / len(tracks_df) * 100
    if consistency_rate > 25:
        intense_score += 2
    elif consistency_rate > 15:
        intense_score += 1
    
    # 3. Upbeat & Conventional
    upbeat_score = 0
    if tracks_df['popularity'].mean() > 80:
        upbeat_score += 2
    elif tracks_df['popularity'].mean() > 70:
        upbeat_score += 1
    
    if tracks_df['song_age'].mean() < 5:
        upbeat_score += 2
    elif tracks_df['song_age'].mean() < 10:
        upbeat_score += 1
    
    if tracks_df['duration_minutes'].mean() < 3.5:
        upbeat_score += 2
    elif tracks_df['duration_minutes'].mean() < 4:
        upbeat_score += 1
    
    # 4. Energetic & Rhythmic
    energetic_score = 0
    if tracks_df['song_age'].mean() < 8:
        energetic_score += 1
    
    rank_variance = tracks_df.groupby(['track_name', 'artist_name'])['rank_position'].var().mean()
    if rank_variance > 100:
        energetic_score += 2
    elif rank_variance > 50:
        energetic_score += 1
    
    # Create radar chart
    categories = ['Reflective &<br>Complex', 'Intense &<br>Rebellious', 
                 'Upbeat &<br>Conventional', 'Energetic &<br>Rhythmic']
    values = [reflective_score, intense_score, upbeat_score, energetic_score]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255, 107, 107, 0.3)',
        line=dict(color='#FF6B6B', width=3),
        name='Your Musical Personality'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 6],
                tickvals=[1, 2, 3, 4, 5, 6],
                ticktext=['1', '2', '3', '4', '5', '6']
            )
        ),
        showlegend=True,
        title="🧠 Musical Personality Profile<br><sub>Based on Rentfrow & Gosling (2003) Research</sub>",
        template="plotly_dark",
        height=600
    )
    
    # Save and display
    html_file = "musical_personality_radar.html"
    fig.write_html(html_file)
    print(f"🧠 Saved musical personality radar chart to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive chart")
    
    # Also show in environment
    fig.show()
    
    return {
        'Reflective & Complex': reflective_score,
        'Intense & Rebellious': intense_score,
        'Upbeat & Conventional': upbeat_score,
        'Energetic & Rhythmic': energetic_score
    }

def create_listening_behavior_dashboard(tracks_df):
    """Create dashboard showing listening psychology patterns"""
    print("🎧 Creating listening behavior dashboard...")
    
    # Prepare data
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    # Create subplot dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Novelty Seeking vs Familiarity',
            'Era Preference Distribution',
            'Mainstream vs Independent Taste',
            'Artist Loyalty Pattern'
        ),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "pie"}]]
    )
    
    # 1. Novelty vs Familiarity Gauge
    song_persistence = tracks_df.groupby(['track_name', 'artist_name']).size()
    repeat_rate = (song_persistence > 1).mean() * 100
    novelty_score = 100 - repeat_rate
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=novelty_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Novelty Seeking %"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#FF6B6B"},
            'steps': [
                {'range': [0, 33], 'color': "#FFE5E5"},
                {'range': [33, 66], 'color': "#FFB3B3"},
                {'range': [66, 100], 'color': "#FF8080"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ), row=1, col=1)
    
    # 2. Era Distribution
    def categorize_era(year):
        if pd.isna(year):
            return "Unknown"
        if year >= 2020:
            return "Current (2020+)"
        elif year >= 2010:
            return "Recent (2010s)"
        elif year >= 2000:
            return "Millennial (2000s)"
        elif year >= 1990:
            return "90s"
        elif year >= 1980:
            return "80s"
        else:
            return "Classic (Pre-1980)"
    
    tracks_df['era'] = tracks_df['release_year'].apply(categorize_era)
    era_counts = tracks_df['era'].value_counts()
    
    fig.add_trace(go.Bar(
        x=era_counts.index,
        y=era_counts.values,
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'][:len(era_counts)],
        name='Era Distribution'
    ), row=1, col=2)
    
    # 3. Mainstream vs Independent (Popularity vs Duration)
    fig.add_trace(go.Scatter(
        x=tracks_df['popularity'],
        y=tracks_df['duration_minutes'],
        mode='markers',
        marker=dict(
            size=8,
            color=tracks_df['song_age'],
            colorscale='Viridis',
            colorbar=dict(title="Song Age (years)"),
            opacity=0.7
        ),
        text=[f"{row['track_name']} - {row['artist_name']}" for _, row in tracks_df.iterrows()],
        hovertemplate='<b>%{text}</b><br>Popularity: %{x}<br>Duration: %{y:.1f}min<br>Age: %{marker.color:.0f}yrs<extra></extra>',
        name='Songs'
    ), row=2, col=1)
    
    # 4. Artist Loyalty (Top artists pie chart)
    artist_counts = tracks_df['artist_name'].value_counts().head(8)
    other_count = len(tracks_df) - artist_counts.sum()
    
    labels = list(artist_counts.index) + ['Others']
    values = list(artist_counts.values) + [other_count]
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFB6C1', '#98FB98', '#87CEEB']),
        name='Artist Distribution'
    ), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title="🎧 Listening Psychology Behavior Dashboard",
        height=800,
        showlegend=False,
        template="plotly_dark"
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Era", row=1, col=2)
    fig.update_yaxes(title_text="Track Count", row=1, col=2)
    fig.update_xaxes(title_text="Popularity (0-100)", row=2, col=1)
    fig.update_yaxes(title_text="Duration (minutes)", row=2, col=1)
    
    # Save and display
    html_file = "listening_behavior_dashboard.html"
    fig.write_html(html_file)
    print(f"🎧 Saved listening behavior dashboard to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive dashboard")
    
    # Also show in environment
    fig.show()

def create_big_five_correlation_chart(tracks_df):
    """Create Big Five personality correlation visualization"""
    print("🧬 Creating Big Five personality correlations...")
    
    # Calculate psychological metrics
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    
    # Calculate Big Five correlations
    artist_diversity = len(tracks_df['artist_name'].unique()) / len(tracks_df) * 100
    openness_score = (artist_diversity + (100 - tracks_df['popularity'].mean())) / 2
    
    # Taste stability
    periods = ['long_term', 'medium_term', 'short_term']
    period_overlaps = []
    for i, period1 in enumerate(periods[:-1]):
        period2 = periods[i+1]
        artists1 = set(tracks_df[tracks_df['time_range'] == period1]['artist_name'].unique())
        artists2 = set(tracks_df[tracks_df['time_range'] == period2]['artist_name'].unique())
        if artists1 and artists2:
            overlap = len(artists1.intersection(artists2)) / len(artists1.union(artists2)) * 100
            period_overlaps.append(overlap)
    
    conscientiousness_score = np.mean(period_overlaps) if period_overlaps else 50
    extraversion_score = tracks_df['popularity'].mean()
    
    # Emotional stability (inverse of ranking volatility)
    rank_changes = []
    for track_artist in tracks_df.groupby(['track_name', 'artist_name']):
        track_data = track_artist[1]
        if len(track_data) > 1:
            rank_changes.append(track_data['rank_position'].std())
    
    avg_volatility = np.mean(rank_changes) if rank_changes else 10
    neuroticism_score = min(100, avg_volatility * 5)  # Higher volatility = higher neuroticism
    emotional_stability_score = 100 - neuroticism_score
    
    # Agreeableness (based on explicit content and mainstream preference)
    explicit_rate = tracks_df['explicit'].mean() * 100
    agreeableness_score = 100 - explicit_rate + (tracks_df['popularity'].mean() - 50)
    agreeableness_score = max(0, min(100, agreeableness_score))
    
    # Create radar chart for Big Five
    categories = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Emotional<br>Stability']
    values = [openness_score, conscientiousness_score, extraversion_score, agreeableness_score, emotional_stability_score]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(78, 205, 196, 0.3)',
        line=dict(color='#4ECDC4', width=3),
        name='Your Music-Based Big Five Profile'
    ))
    
    # Add average human scores for comparison
    avg_values = [50, 50, 50, 50, 50]  # Population average
    fig.add_trace(go.Scatterpolar(
        r=avg_values + [avg_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(128, 128, 128, 0.2)',
        line=dict(color='#808080', width=2, dash='dash'),
        name='Population Average'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20', '40', '60', '80', '100']
            )
        ),
        showlegend=True,
        title="🧬 Big Five Personality - Music Correlations<br><sub>Based on musical preference research</sub>",
        template="plotly_dark",
        height=600
    )
    
    # Save and display
    html_file = "big_five_correlation_chart.html"
    fig.write_html(html_file)
    print(f"🧬 Saved Big Five correlation chart to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive chart")
    
    # Also show in environment
    fig.show()
    
    return {
        'Openness': openness_score,
        'Conscientiousness': conscientiousness_score,
        'Extraversion': extraversion_score,
        'Agreeableness': agreeableness_score,
        'Emotional Stability': emotional_stability_score
    }

def create_statistical_inference_charts(tracks_df):
    """Create visualizations for statistical tests"""
    print("📊 Creating statistical inference visualizations...")
    
    # Prepare data
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    # Create subplots for statistical tests
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Music Preference Evolution Across Time Periods',
            'Song Age vs Personal Ranking Correlation',
            'Artist Loyalty: Repeat vs New Discoveries',
            'Ranking Consistency Analysis'
        ),
        specs=[[{"type": "box"}, {"type": "scatter"}],
               [{"type": "bar"}, {"type": "histogram"}]]
    )
    
    # 1. Enhanced Popularity Distribution by Time Period with trend annotations
    period_colors = {'short_term': '#FF6B6B', 'medium_term': '#4ECDC4', 'long_term': '#45B7D1'}
    period_means = {}
    
    for period in ['long_term', 'medium_term', 'short_term']:  # Order matters for trend
        if period in tracks_df['time_range'].unique():
            period_data = tracks_df[tracks_df['time_range'] == period]
            period_means[period] = period_data['popularity'].mean()
            
            fig.add_trace(go.Box(
                y=period_data['popularity'],
                name=period.replace('_', ' ').title(),
                marker_color=period_colors[period],
                boxpoints='outliers',
                jitter=0.3,
                pointpos=-1.8,
                line=dict(width=2),
                fillcolor=period_colors[period],
                opacity=0.7
            ), row=1, col=1)
    
    # Add trend line for popularity evolution
    if len(period_means) >= 2:
        periods_order = ['long_term', 'medium_term', 'short_term']
        means_values = [period_means.get(p, 0) for p in periods_order if p in period_means]
        x_positions = list(range(len(means_values)))
        
        fig.add_trace(go.Scatter(
            x=x_positions,
            y=means_values,
            mode='lines+markers',
            line=dict(color='yellow', width=3, dash='dash'),
            marker=dict(size=8, color='yellow', symbol='diamond'),
            name='Popularity Trend',
            yaxis='y1',
            showlegend=True
        ), row=1, col=1)
    
    # 2. Song Age vs Ranking Correlation
    clean_data = tracks_df.dropna(subset=['song_age', 'rank_position'])
    if len(clean_data) > 10:
        correlation, p_value = stats.pearsonr(clean_data['song_age'], clean_data['rank_position'])
        
        fig.add_trace(go.Scatter(
            x=clean_data['song_age'],
            y=clean_data['rank_position'],
            mode='markers',
            marker=dict(
                size=6,
                color='#45B7D1',
                opacity=0.6
            ),
            name=f'Correlation: {correlation:.3f}<br>P-value: {p_value:.3f}',
            text=[f"{row['track_name']} - {row['artist_name']}" for _, row in clean_data.iterrows()],
            hovertemplate='<b>%{text}</b><br>Age: %{x} years<br>Rank: %{y}<extra></extra>'
        ), row=1, col=2)
        
        # Add trend line
        z = np.polyfit(clean_data['song_age'], clean_data['rank_position'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(clean_data['song_age'].min(), clean_data['song_age'].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name='Trend Line'
        ), row=1, col=2)
    
    # 3. Artist Loyalty: Repeat vs New Discoveries (Bar chart)
    # Analyze artists appearing in multiple periods vs single period artists
    artist_periods = tracks_df.groupby('artist_name')['time_range'].nunique().reset_index()
    artist_periods['category'] = artist_periods['time_range'].apply(
        lambda x: 'Highly Loyal (3 periods)' if x == 3 
        else 'Moderately Loyal (2 periods)' if x == 2 
        else 'New Discovery (1 period)'
    )
    
    loyalty_counts = artist_periods['category'].value_counts()
    loyalty_colors = {
        'Highly Loyal (3 periods)': '#FF6B6B',
        'Moderately Loyal (2 periods)': '#4ECDC4', 
        'New Discovery (1 period)': '#45B7D1'
    }
    
    for category in loyalty_counts.index:
        fig.add_trace(go.Bar(
            x=[category],
            y=[loyalty_counts[category]],
            name=category,
            marker_color=loyalty_colors.get(category, '#96CEB4'),
            text=[f'{loyalty_counts[category]} artists'],
            textposition='outside',
            hovertemplate=f'<b>{category}</b><br>Count: %{{y}}<br>Percentage: {loyalty_counts[category]/len(artist_periods)*100:.1f}%<extra></extra>'
        ), row=2, col=1)
    
    # Add percentage annotations
    total_artists = len(artist_periods)
    for i, (category, count) in enumerate(loyalty_counts.items()):
        percentage = count / total_artists * 100
        fig.add_annotation(
            text=f"{percentage:.1f}%",
            x=category,
            y=count + count * 0.1,
            xref=f"x3",
            yref=f"y3",
            showarrow=False,
            font=dict(size=12, color="white", family="Arial Black")
        )
    
    # 4. Ranking Consistency Histogram
    song_rankings = tracks_df.groupby(['track_name', 'artist_name'])['rank_position'].agg(['count', 'std']).reset_index()
    consistent_songs = song_rankings[song_rankings['count'] > 1]['std'].dropna()
    
    if len(consistent_songs) > 0:
        fig.add_trace(go.Histogram(
            x=consistent_songs,
            nbinsx=20,
            marker_color='#96CEB4',
            name='Ranking Std Dev',
            opacity=0.7
        ), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title="📊 Advanced Music Psychology Analytics<br><sub>Deep insights into your listening patterns and preferences</sub>",
        height=800,
        template="plotly_dark",
        showlegend=True
    )
    
    # Update axes labels
    fig.update_yaxes(title_text="Popularity Score", row=1, col=1)
    fig.update_xaxes(title_text="Song Age (years)", row=1, col=2)
    fig.update_yaxes(title_text="Personal Ranking", row=1, col=2)
    fig.update_yaxes(title_text="Number of Artists", row=2, col=1)
    fig.update_xaxes(title_text="Artist Loyalty Category", row=2, col=1)
    fig.update_xaxes(title_text="Ranking Standard Deviation", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=2)
    
    # Save and display
    html_file = "advanced_music_psychology_analytics.html"
    fig.write_html(html_file)
    print(f"📊 Saved advanced music psychology analytics to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive charts")
    
    # Also show in environment
    fig.show()

def create_mood_regulation_heatmap(tracks_df):
    """Create heatmap showing mood regulation patterns"""
    print("💭 Creating mood regulation pattern heatmap...")
    
    # Prepare data
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    # Create mood categories based on duration and popularity
    def categorize_mood(row):
        duration = row['duration_minutes']
        popularity = row['popularity']
        
        if duration > 4.5:
            if popularity < 60:
                return "Contemplative/Deep"
            else:
                return "Uplifting/Extended"
        elif duration < 3.5:
            if popularity > 70:
                return "Energetic/Popular"
            else:
                return "Quick/Niche"
        else:
            if popularity > 70:
                return "Balanced/Mainstream"
            else:
                return "Moderate/Independent"
    
    tracks_df['mood_category'] = tracks_df.apply(categorize_mood, axis=1)
    
    # Create era categories
    def categorize_era_simple(year):
        if pd.isna(year):
            return "Unknown"
        if year >= 2015:
            return "Recent"
        elif year >= 2000:
            return "2000s"
        elif year >= 1990:
            return "90s/Earlier"
        else:
            return "Classic"
    
    tracks_df['era_simple'] = tracks_df['release_year'].apply(categorize_era_simple)
    
    # Create cross-tabulation
    mood_era_crosstab = pd.crosstab(tracks_df['mood_category'], tracks_df['era_simple'])
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=mood_era_crosstab.values,
        x=mood_era_crosstab.columns,
        y=mood_era_crosstab.index,
        colorscale='Viridis',
        text=mood_era_crosstab.values,
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>Era: %{x}<br>Count: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title="💭 Mood Regulation Patterns by Era<br><sub>How you use different types of music across time periods</sub>",
        xaxis_title="Musical Era",
        yaxis_title="Mood/Energy Category",
        template="plotly_dark",
        height=500
    )
    
    # Save and display
    html_file = "mood_regulation_heatmap.html"
    fig.write_html(html_file)
    print(f"💭 Saved mood regulation heatmap to: {html_file}")
    
    # Open in browser
    try:
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print(f"🌐 Opening {html_file} in your web browser...")
    except:
        print(f"💡 Manually open {html_file} in your browser to view the interactive heatmap")
    
    # Also show in environment
    fig.show()
    
    return mood_era_crosstab

def main():
    """Main psychology visualization application"""
    print("🧠 SPOTIFY PSYCHOLOGY VISUALIZATIONS")
    print("="*60)
    print("Visual representations of your musical psychology insights")
    
    # Load data
    tracks_df, artists_df = load_data()
    if tracks_df is None:
        return
    
    while True:
        print(f"\n🎨 INTERACTIVE PSYCHOLOGY VISUALIZATION MENU")
        print("1. Musical Personality Radar Chart (interactive web)")
        print("2. Listening Behavior Dashboard (interactive web)")
        print("3. Big Five Personality Correlations (interactive web)")
        print("4. Statistical Inference Charts (interactive web)")
        print("5. Mood Regulation Heatmap (interactive web)")
        print("6. Generate all interactive psychology visualizations")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            personality_scores = create_personality_radar_chart(tracks_df)
            print(f"\n📊 Your personality scores: {personality_scores}")
            
        elif choice == "2":
            create_listening_behavior_dashboard(tracks_df)
            
        elif choice == "3":
            big_five_scores = create_big_five_correlation_chart(tracks_df)
            print(f"\n🧬 Your Big Five scores: {big_five_scores}")
            
        elif choice == "4":
            create_statistical_inference_charts(tracks_df)
            
        elif choice == "5":
            mood_patterns = create_mood_regulation_heatmap(tracks_df)
            print(f"\n💭 Mood regulation patterns created")
            
        elif choice == "6":
            print("🎨 Generating all interactive psychology visualizations...")
            create_personality_radar_chart(tracks_df)
            create_listening_behavior_dashboard(tracks_df)
            create_big_five_correlation_chart(tracks_df)
            create_statistical_inference_charts(tracks_df)
            create_mood_regulation_heatmap(tracks_df)
            print("✅ All interactive psychology visualizations generated and saved as HTML files!")
            
        elif choice == "7":
            print("Thank you for exploring your musical psychology visually! 🧠🎨")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
