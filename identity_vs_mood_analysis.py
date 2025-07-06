#!/usr/bin/env python3
"""
Identity vs. Mood-Driven Music Preference Analysis
==================================================
Analyzes Spotify listening data to distinguish between:
- Identity-driven preferences (stable, niche, value-expressive)
- Mood-driven preferences (temporary, mainstream, emotion-regulating)

Based on research from Schäfer & Sedlmeier (2009) and others.
"""

import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from collections import Counter
import webbrowser
import os
import warnings
warnings.filterwarnings('ignore')

class IdentityMoodAnalyzer:
    def __init__(self, db_path='../outputs/listening_trends.db'):
        self.db_path = db_path
        self.load_data()
    
    def load_data(self):
        """Load data from SQLite database"""
        conn = sqlite3.connect(self.db_path)
        self.tracks = pd.read_sql_query("SELECT * FROM tracks", conn)
        self.artists = pd.read_sql_query("SELECT * FROM artists", conn)
        conn.close()
        
        print(f"✅ Loaded {len(self.tracks)} tracks for identity vs mood analysis")
    
    def calculate_identity_signals(self):
        """Calculate markers that suggest identity-driven preferences"""
        
        print("\n🎭 IDENTITY-DRIVEN PREFERENCE SIGNALS")
        print("=" * 60)
        
        # 1. Temporal Persistence (Identity marker)
        song_persistence = self.tracks.groupby(['track_name', 'artist_name']).agg({
            'time_range': 'count',
            'rank_position': 'mean',
            'popularity': 'first'
        }).rename(columns={'time_range': 'period_count'})
        
        persistent_songs = song_persistence[song_persistence['period_count'] >= 2]
        identity_persistence_score = len(persistent_songs) / len(song_persistence) * 100
        
        print(f"🔄 Temporal Persistence Score: {identity_persistence_score:.1f}%")
        print(f"   → Songs appearing in 2+ periods: {len(persistent_songs)}")
        print(f"   → Total unique songs: {len(song_persistence)}")
        print(f"   → Interpretation: Higher = more identity-driven")
        
        # 2. Niche Preference (Identity marker)
        niche_threshold = 50  # Below 50 popularity = niche
        niche_tracks = self.tracks[self.tracks['popularity'] < niche_threshold]
        niche_percentage = len(niche_tracks) / len(self.tracks) * 100
        
        print(f"\n🎯 Niche Music Preference: {niche_percentage:.1f}%")
        print(f"   → Tracks with popularity < {niche_threshold}: {len(niche_tracks)}")
        print(f"   → Average popularity: {self.tracks['popularity'].mean():.1f}")
        print(f"   → Interpretation: Higher niche % = more identity expression")
        
        # 3. Artist Devotion (Identity marker)
        artist_counts = self.tracks['artist_name'].value_counts()
        top_artist_dominance = artist_counts.iloc[0] / len(self.tracks) * 100
        artists_with_multiple_tracks = len(artist_counts[artist_counts > 1])
        
        print(f"\n🎤 Artist Devotion Patterns:")
        print(f"   → Top artist dominance: {top_artist_dominance:.1f}%")
        print(f"   → Artists with 2+ tracks: {artists_with_multiple_tracks}")
        print(f"   → Total unique artists: {len(artist_counts)}")
        print(f"   → Artist diversity ratio: {len(artist_counts)/len(self.tracks):.2f}")
        
        # 4. Deep Cuts vs Hits Analysis
        print(f"\n🎵 Deep Cuts vs Mainstream Hits:")
        for artist in artist_counts.head(5).index:
            artist_tracks = self.tracks[self.tracks['artist_name'] == artist]
            avg_pop = artist_tracks['popularity'].mean()
            track_count = len(artist_tracks)
            devotion_score = track_count / (avg_pop/10 + 1)  # Normalized devotion
            
            print(f"   → {artist}: {track_count} tracks, avg popularity {avg_pop:.0f}, devotion score {devotion_score:.1f}")
        
        return {
            'persistence_score': identity_persistence_score,
            'niche_percentage': niche_percentage,
            'artist_dominance': top_artist_dominance,
            'artist_diversity': len(artist_counts)/len(self.tracks)
        }
    
    def calculate_mood_signals(self):
        """Calculate markers that suggest mood-driven preferences"""
        
        print("\n\n😊 MOOD-DRIVEN PREFERENCE SIGNALS")
        print("=" * 60)
        
        # 1. Ranking Volatility (Mood marker)
        song_rankings = self.tracks.groupby(['track_name', 'artist_name'])['rank_position'].agg(['std', 'count'])
        song_rankings = song_rankings[song_rankings['count'] > 1]  # Only songs appearing multiple times
        avg_volatility = song_rankings['std'].mean()
        
        print(f"📊 Ranking Volatility: {avg_volatility:.1f}")
        print(f"   → Average standard deviation of rankings")
        print(f"   → Higher volatility = more mood-dependent preferences")
        
        # 2. Era Diversity (Mood marker - mood seekers sample widely)
        release_years = pd.to_datetime(self.tracks['release_date'], errors='coerce').dt.year
        era_diversity = len(release_years.value_counts())
        year_span = release_years.max() - release_years.min()
        
        print(f"\n📅 Temporal Diversity:")
        print(f"   → Unique release years: {era_diversity}")
        print(f"   → Year span: {year_span} years")
        print(f"   → Average song age: {2024 - release_years.mean():.1f} years")
        
        # 3. Popularity Variance (Mood marker)
        popularity_std = self.tracks['popularity'].std()
        popularity_range = self.tracks['popularity'].max() - self.tracks['popularity'].min()
        
        print(f"\n🎯 Popularity Variance:")
        print(f"   → Standard deviation: {popularity_std:.1f}")
        print(f"   → Range: {popularity_range}")
        print(f"   → Higher variance = more mood-driven sampling")
        
        # 4. Explicit Content Ratio (Mood regulation marker)
        explicit_ratio = self.tracks['explicit'].mean() * 100
        print(f"\n🔞 Explicit Content: {explicit_ratio:.1f}%")
        print(f"   → May indicate emotional regulation needs")
        
        return {
            'ranking_volatility': avg_volatility,
            'era_diversity': era_diversity,
            'popularity_variance': popularity_std,
            'explicit_ratio': explicit_ratio
        }
    
    def identity_vs_mood_classification(self):
        """Classify listening behavior as primarily identity or mood-driven"""
        
        print("\n\n🔬 IDENTITY vs MOOD-DRIVEN CLASSIFICATION")
        print("=" * 60)
        
        # Calculate composite scores
        identity_signals = self.calculate_identity_signals()
        mood_signals = self.calculate_mood_signals()
        
        # Identity score (0-100)
        identity_score = (
            identity_signals['persistence_score'] * 0.3 +  # Temporal consistency
            identity_signals['niche_percentage'] * 0.3 +   # Niche preference
            (100 - identity_signals['artist_dominance']) * 0.2 +  # Artist diversity
            (identity_signals['artist_diversity'] * 100) * 0.2    # Overall diversity
        )
        
        # Mood score (0-100) 
        mood_score = (
            min(mood_signals['ranking_volatility'] * 10, 100) * 0.4 +  # Volatility
            min(mood_signals['popularity_variance'] * 2, 100) * 0.3 +   # Pop variance
            min(mood_signals['era_diversity'] * 3, 100) * 0.3           # Era diversity
        )
        
        print(f"\n📊 COMPOSITE SCORES:")
        print(f"🎭 Identity-Driven Score: {identity_score:.1f}/100")
        print(f"😊 Mood-Driven Score: {mood_score:.1f}/100")
        
        # Determine primary driver
        if identity_score > mood_score:
            primary_driver = "IDENTITY-DRIVEN"
            confidence = identity_score - mood_score
        else:
            primary_driver = "MOOD-DRIVEN"
            confidence = mood_score - identity_score
        
        print(f"\n🎯 PRIMARY LISTENING MOTIVATION: {primary_driver}")
        print(f"🔍 Confidence Level: {confidence:.1f} points")
        
        # Detailed interpretation
        print(f"\n📝 PSYCHOLOGICAL INTERPRETATION:")
        if primary_driver == "IDENTITY-DRIVEN":
            print("✅ Your music choices primarily serve identity expression and value communication")
            print("   → You use music to define and communicate who you are")
            print("   → Preferences likely stable over long periods")
            print("   → Music acts as a 'social badge' of your personality")
            print("   → Resistant to external influence/trends")
        else:
            print("✅ Your music choices primarily serve emotional regulation and mood management")
            print("   → You use music as a tool for feeling better")
            print("   → Preferences change based on circumstances and mood")
            print("   → Music acts as 'emotional medicine'")
            print("   → More responsive to situational needs")
        
        return {
            'identity_score': identity_score,
            'mood_score': mood_score,
            'primary_driver': primary_driver,
            'confidence': confidence
        }
    
    def deep_identity_analysis(self):
        """Deeper analysis of identity-driven patterns"""
        
        print("\n\n🎭 DEEP IDENTITY EXPRESSION ANALYSIS")
        print("=" * 60)
        
        # 1. Symbolic Boundary Analysis (groups you identify with/against)
        mainstream_threshold = 70
        mainstream_tracks = self.tracks[self.tracks['popularity'] >= mainstream_threshold]
        underground_tracks = self.tracks[self.tracks['popularity'] < 30]
        
        print(f"🚧 Musical Boundary Markers:")
        print(f"   → Mainstream rejection rate: {(1 - len(mainstream_tracks)/len(self.tracks)) * 100:.1f}%")
        print(f"   → Underground affinity: {len(underground_tracks)/len(self.tracks) * 100:.1f}%")
        
        # 2. Aesthetic Coherence (do your choices form a coherent identity?)
        artist_genres = self.tracks['artist_name'].value_counts()
        top_artists = artist_genres.head(10).index.tolist()
        
        print(f"\n🎨 Aesthetic Identity Coherence:")
        print(f"   → Core artist cluster: {len(top_artists)} artists represent {artist_genres.head(10).sum()/len(self.tracks)*100:.1f}% of listening")
        
        # 3. Counter-cultural indicators
        explicit_ratio = self.tracks['explicit'].mean()
        avg_popularity = self.tracks['popularity'].mean()
        
        counter_cultural_score = (
            (1 - avg_popularity/100) * 50 +  # Low popularity
            explicit_ratio * 30 +            # Explicit content
            (len(underground_tracks)/len(self.tracks)) * 20  # Underground music
        )
        
        print(f"\n🔥 Counter-Cultural Expression Score: {counter_cultural_score:.1f}/100")
        if counter_cultural_score > 50:
            print("   → High: Music expresses non-conformist identity")
        elif counter_cultural_score > 25:
            print("   → Medium: Balanced mainstream/alternative identity")
        else:
            print("   → Low: Conventional aesthetic preferences")
    
    def visualize_identity_mood_patterns(self):
        """Create interactive visualizations of identity vs mood patterns"""
        
        print("📊 Creating interactive identity vs mood analysis dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Identity Signal: Niche + Persistent Songs = Identity Expression',
                'Artist Devotion Distribution (Track Count per Artist)',
                'Artist Loyalty vs Exploration (Deep Connections)',
                'Popularity Distribution (Mainstream vs Niche Preference)'
            ),
            specs=[[{"type": "scatter"}, {"type": "histogram"}],
                   [{"type": "scatter"}, {"type": "histogram"}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.10
        )
        
        # 1. Enhanced Persistence vs Popularity (Identity marker) - More compelling visualization
        song_data = self.tracks.groupby(['track_name', 'artist_name']).agg({
            'time_range': 'count',
            'popularity': 'first',
            'rank_position': 'mean',
            'explicit': 'first'
        }).rename(columns={'time_range': 'persistence'})
        
        # Create identity categories
        song_data['identity_category'] = 'Mood-Driven'
        song_data.loc[(song_data['persistence'] >= 2) & (song_data['popularity'] < 60), 'identity_category'] = 'Strong Identity'
        song_data.loc[(song_data['persistence'] >= 2) & (song_data['popularity'] >= 60), 'identity_category'] = 'Popular Favorite'
        song_data.loc[(song_data['persistence'] == 1) & (song_data['popularity'] < 40), 'identity_category'] = 'Niche Discovery'
        
        category_colors = {
            'Strong Identity': '#FF6B6B',     # Red - high identity signal
            'Popular Favorite': '#4ECDC4',   # Teal - mixed signal
            'Niche Discovery': '#45B7D1',    # Blue - potential identity
            'Mood-Driven': '#96CEB4'         # Green - mood-driven
        }
        
        for category in song_data['identity_category'].unique():
            cat_data = song_data[song_data['identity_category'] == category]
            fig.add_trace(
                go.Scatter(
                    x=cat_data['popularity'],
                    y=cat_data['persistence'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=category_colors[category],
                        opacity=0.8,
                        line=dict(width=1, color='white')
                    ),
                    text=[f"{idx[0]} - {idx[1]}" for idx in cat_data.index],
                    hovertemplate=f'<b>{category}</b><br><b>%{{text}}</b><br>Popularity: %{{x}}<br>Persistence: %{{y}} periods<br>Avg Rank: {cat_data["rank_position"].mean():.1f}<extra></extra>',
                    name=category,
                    legendgroup="identity"
                ),
                row=1, col=1
            )
        
        # Add enhanced threshold zones with annotations
        fig.add_shape(
            type="rect", x0=0, y0=2, x1=60, y1=3,
            fillcolor="rgba(255, 107, 107, 0.2)", opacity=0.5,
            line=dict(width=0), row=1, col=1
        )
        fig.add_annotation(
            text="🎭 IDENTITY ZONE<br>Low popularity + High persistence",
            x=30, y=2.5, xref="x1", yref="y1",
            showarrow=False, font=dict(size=10, color="red", family="Arial Black"),
            bgcolor="rgba(255,255,255,0.8)", bordercolor="red", borderwidth=1
        )
        
        # 2. Artist Devotion Distribution
        artist_counts = self.tracks['artist_name'].value_counts()
        
        fig.add_trace(
            go.Histogram(
                x=artist_counts.values,
                nbinsx=20,
                marker_color='skyblue',
                marker_line_color='black',
                marker_line_width=1,
                name='Artist Distribution',
                hovertemplate='Tracks per Artist: %{x}<br>Count: %{y}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # Add mean line
        fig.add_vline(x=artist_counts.mean(), line_dash="dash", line_color="red",
                     annotation_text=f"Mean: {artist_counts.mean():.1f}", row=1, col=2)
        
        # 3. Artist Loyalty vs Exploration (Replaces temporal distribution)
        # Analyze deep vs shallow artist connections
        artist_stats = self.tracks.groupby('artist_name').agg({
            'track_name': 'count',
            'time_range': 'nunique',
            'rank_position': 'mean',
            'popularity': 'mean'
        }).rename(columns={'track_name': 'track_count', 'time_range': 'period_span'})
        
        # Create loyalty categories
        artist_stats['loyalty_type'] = 'Casual Listen'
        artist_stats.loc[(artist_stats['track_count'] >= 5) & (artist_stats['period_span'] >= 2), 'loyalty_type'] = 'Deep Connection'
        artist_stats.loc[(artist_stats['track_count'] >= 3) & (artist_stats['period_span'] >= 2), 'loyalty_type'] = 'Consistent Favorite'
        artist_stats.loc[(artist_stats['track_count'] >= 5) & (artist_stats['period_span'] == 1), 'loyalty_type'] = 'Binge Phase'
        
        loyalty_colors = {
            'Deep Connection': '#FF6B6B',      # Red - highest identity signal
            'Consistent Favorite': '#4ECDC4',  # Teal - moderate identity
            'Binge Phase': '#FFD93D',          # Yellow - mood-driven spike
            'Casual Listen': '#96CEB4'         # Green - mood-driven
        }
        
        for loyalty_type in artist_stats['loyalty_type'].unique():
            type_data = artist_stats[artist_stats['loyalty_type'] == loyalty_type]
            fig.add_trace(
                go.Scatter(
                    x=type_data['track_count'],
                    y=type_data['period_span'],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color=loyalty_colors[loyalty_type],
                        opacity=0.8,
                        line=dict(width=1, color='white')
                    ),
                    text=type_data.index,
                    hovertemplate=f'<b>{loyalty_type}</b><br><b>%{{text}}</b><br>Tracks: %{{x}}<br>Periods: %{{y}}<br>Avg Rank: {type_data["rank_position"].mean():.1f}<br>Avg Popularity: {type_data["popularity"].mean():.0f}<extra></extra>',
                    name=loyalty_type,
                    legendgroup="loyalty"
                ),
                row=2, col=1
            )
        
        # Add identity zones
        fig.add_shape(
            type="rect", x0=5, y0=2, x1=25, y1=3,
            fillcolor="rgba(255, 107, 107, 0.2)", opacity=0.5,
            line=dict(width=0), row=2, col=1
        )
        fig.add_annotation(
            text="🎯 DEEP LOYALTY<br>High tracks + Multi-period",
            x=15, y=2.5, xref="x3", yref="y3",
            showarrow=False, font=dict(size=9, color="red", family="Arial Black"),
            bgcolor="rgba(255,255,255,0.8)", bordercolor="red", borderwidth=1
        )
        
        # 4. Popularity Distribution
        fig.add_trace(
            go.Histogram(
                x=self.tracks['popularity'],
                nbinsx=30,
                marker_color='lightcoral',
                marker_line_color='black',
                marker_line_width=1,
                name='Popularity Distribution',
                hovertemplate='Popularity: %{x}<br>Count: %{y}<extra></extra>'
            ),
            row=2, col=2
        )
        
        # Add mean and niche threshold lines
        mean_pop = self.tracks['popularity'].mean()
        fig.add_vline(x=mean_pop, line_dash="dash", line_color="blue",
                     annotation_text=f"Mean: {mean_pop:.1f}", row=2, col=2)
        fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.7,
                     annotation_text="Niche Threshold", row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title="🎭 Identity vs Mood-Driven Music Preference Analysis Dashboard",
            height=800,
            showlegend=False,
            template="plotly_dark",
            font=dict(size=11)
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Popularity (Mainstream ←→ Niche)", row=1, col=1)
        fig.update_yaxes(title_text="Persistence (# Time Periods)", row=1, col=1)
        fig.update_xaxes(title_text="Tracks per Artist", row=1, col=2)
        fig.update_yaxes(title_text="Number of Artists", row=1, col=2)
        fig.update_xaxes(title_text="Tracks per Artist", row=2, col=1)
        fig.update_yaxes(title_text="Time Periods Spanned", row=2, col=1)
        fig.update_xaxes(title_text="Popularity Score", row=2, col=2)
        fig.update_yaxes(title_text="Number of Tracks", row=2, col=2)
        
        # Save and display
        html_file = "identity_vs_mood_analysis.html"
        fig.write_html(html_file)
        print(f"🎭 Saved identity vs mood analysis to: {html_file}")
        
        # Open in browser
        try:
            webbrowser.open(f'file://{os.path.abspath(html_file)}')
            print(f"🌐 Opening {html_file} in your web browser...")
        except:
            print(f"💡 Manually open {html_file} in your browser to view the interactive dashboard")
        
        # Also show in environment
        fig.show()
        
        print("\n📊 Interactive Dashboard Features:")
        print("   ✨ Hover over data points for detailed information")
        print("   🔍 Zoom and pan to explore specific regions")
        print("   📱 Responsive design works on all devices")
        print("\n🔍 What to Look For:")
        print("   → Top-left: Identity-driven songs (low popularity + high persistence)")
        print("   → Top-right: Artist devotion patterns (long tail = deep connections)")
        print("   → Bottom-left: Artist loyalty (high tracks + multiple periods = deep identity)")
        print("   → Bottom-right: Niche preference (left-skewed = identity expression)")

def main():
    """Run the identity vs mood analysis"""
    
    print("🎭 IDENTITY vs MOOD-DRIVEN MUSIC PREFERENCE ANALYSIS")
    print("=" * 70)
    print("Based on Schäfer & Sedlmeier (2009) research on music functions")
    print("Distinguishing identity expression from emotional regulation")
    
    try:
        analyzer = IdentityMoodAnalyzer()
        
        # Run comprehensive analysis
        results = analyzer.identity_vs_mood_classification()
        analyzer.deep_identity_analysis()
        
        print("\n" + "="*70)
        print("🎯 RESEARCH IMPLICATIONS:")
        print("This analysis helps answer: 'Do you choose music to express who you are")
        print("or to regulate how you feel?' Your data suggests the answer!")
        
        # Create visualizations
        print("\n📊 Generating visualizations...")
        analyzer.visualize_identity_mood_patterns()
        
    except FileNotFoundError:
        print("❌ Database not found. Please run spotify_data_analysis.py first to collect data.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()
