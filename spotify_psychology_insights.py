import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        
        print(f"✅ Loaded {len(tracks_df)} track entries for psychological analysis")
        return tracks_df, artists_df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None

def analyze_musical_personality_profile(tracks_df):
    """Analyze music taste based on psychological research"""
    print("\n🧠 MUSICAL PERSONALITY PROFILE")
    print("="*60)
    print("Based on research from Rentfrow & Gosling (2003), North (2010), and others")
    
    # Prepare data
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    # Music Preference Dimensions Analysis
    print("\n📊 MUSIC PREFERENCE DIMENSIONS:")
    
    # 1. Reflective & Complex (Classical, Jazz, Blues, Folk)
    # Proxy: Older music, longer tracks, lower popularity (more niche)
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
    
    # 2. Intense & Rebellious (Rock, Alternative, Heavy Metal)
    # Proxy: Explicit content, medium-older music, consistent listening
    intense_score = 0
    explicit_rate = tracks_df['explicit'].mean() * 100
    if explicit_rate > 30:
        intense_score += 2
    elif explicit_rate > 15:
        intense_score += 1
    
    # Check for music consistency (rebellious people stick to their taste)
    consistency_rate = len(tracks_df.groupby(['track_name', 'artist_name']).filter(lambda x: len(x) > 1)) / len(tracks_df) * 100
    if consistency_rate > 25:
        intense_score += 2
    elif consistency_rate > 15:
        intense_score += 1
    
    # 3. Upbeat & Conventional (Pop, Country, Religious, Soundtracks)
    # Proxy: High popularity, recent music, shorter tracks
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
    
    # 4. Energetic & Rhythmic (Hip-hop, Electronic, Dance)
    # Proxy: Recent music, high ranking consistency, shorter duration
    energetic_score = 0
    if tracks_df['song_age'].mean() < 8:
        energetic_score += 1
    
    # Check for high-energy listening patterns (rapid ranking changes suggest energetic music)
    rank_variance = tracks_df.groupby(['track_name', 'artist_name'])['rank_position'].var().mean()
    if rank_variance > 100:  # High variance in rankings
        energetic_score += 2
    elif rank_variance > 50:
        energetic_score += 1
    
    # Display personality dimensions
    dimensions = {
        "Reflective & Complex": (reflective_score, "Sophisticated, introspective, enjoys complex music"),
        "Intense & Rebellious": (intense_score, "Independent, risk-taking, prefers edgy content"),
        "Upbeat & Conventional": (upbeat_score, "Social, cheerful, prefers mainstream music"),
        "Energetic & Rhythmic": (energetic_score, "Active, outgoing, enjoys rhythmic music")
    }
    
    print("\nYour Music Personality Scores (0-6 scale):")
    for dimension, (score, description) in dimensions.items():
        level = "High" if score >= 4 else "Medium" if score >= 2 else "Low"
        print(f"   • {dimension}: {score}/6 ({level})")
        print(f"     → {description}")
    
    # Dominant trait
    dominant_trait = max(dimensions.keys(), key=lambda x: dimensions[x][0])
    print(f"\n🎯 DOMINANT MUSICAL PERSONALITY: {dominant_trait}")
    print(f"   Score: {dimensions[dominant_trait][0]}/6")
    
    return dimensions

def analyze_listening_psychology_patterns(tracks_df):
    """Analyze psychological patterns in listening behavior"""
    print("\n🔍 LISTENING PSYCHOLOGY PATTERNS")
    print("="*60)
    
    # 1. Novelty Seeking vs Familiarity Preference
    print("\n1. NOVELTY SEEKING vs FAMILIARITY PREFERENCE:")
    
    # Calculate song persistence rate
    song_persistence = tracks_df.groupby(['track_name', 'artist_name']).size()
    repeat_rate = (song_persistence > 1).mean() * 100
    
    # Calculate artist diversity
    total_tracks = len(tracks_df)
    unique_artists = len(tracks_df['artist_name'].unique())
    artist_diversity = unique_artists / total_tracks * 100
    
    if repeat_rate > 30:
        familiarity_level = "High"
        novelty_desc = "You prefer familiar songs and tend to replay favorites"
    elif repeat_rate > 15:
        familiarity_level = "Medium"
        novelty_desc = "You balance familiar favorites with new discoveries"
    else:
        familiarity_level = "Low"
        novelty_desc = "You constantly seek new music and rarely repeat songs"
    
    print(f"   • Song Repeat Rate: {repeat_rate:.1f}% ({familiarity_level} familiarity preference)")
    print(f"   • Artist Diversity: {artist_diversity:.1f}% (unique artists per track)")
    print(f"   • Psychology: {novelty_desc}")
    
    # 2. Temporal Stability Analysis
    print("\n2. MUSICAL TASTE STABILITY:")
    
    # Analyze changes across time periods
    period_overlap = {}
    periods = ['long_term', 'medium_term', 'short_term']
    
    for i, period1 in enumerate(periods[:-1]):
        period2 = periods[i+1]
        artists1 = set(tracks_df[tracks_df['time_range'] == period1]['artist_name'].unique())
        artists2 = set(tracks_df[tracks_df['time_range'] == period2]['artist_name'].unique())
        
        if artists1 and artists2:
            overlap = len(artists1.intersection(artists2)) / len(artists1.union(artists2)) * 100
            period_overlap[f"{period1} → {period2}"] = overlap
    
    avg_stability = np.mean(list(period_overlap.values())) if period_overlap else 0
    
    if avg_stability > 60:
        stability_level = "High"
        stability_desc = "Your music taste is very stable over time"
    elif avg_stability > 40:
        stability_level = "Medium"
        stability_desc = "Your music taste evolves gradually"
    else:
        stability_level = "Low"
        stability_desc = "Your music taste changes significantly over time"
    
    print(f"   • Artist Overlap Between Periods: {avg_stability:.1f}% ({stability_level} stability)")
    print(f"   • Psychology: {stability_desc}")
    
    for transition, overlap in period_overlap.items():
        print(f"     - {transition}: {overlap:.1f}% artist overlap")
    
    # 3. Era Preference Analysis (Nostalgia vs Contemporaneity)
    print("\n3. TEMPORAL MUSIC PREFERENCE:")
    
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    avg_song_age = (datetime.now().year - tracks_df['release_year'].mean())
    
    era_distribution = {}
    for _, row in tracks_df.iterrows():
        year = row['release_year']
        if pd.notna(year):
            if year >= 2020:
                era = "Current (2020+)"
            elif year >= 2010:
                era = "Recent (2010s)"
            elif year >= 2000:
                era = "Millennial (2000s)"
            elif year >= 1990:
                era = "90s"
            elif year >= 1980:
                era = "80s"
            else:
                era = "Classic (Pre-1980)"
            
            era_distribution[era] = era_distribution.get(era, 0) + 1
    
    dominant_era = max(era_distribution.keys(), key=lambda x: era_distribution[x]) if era_distribution else "Unknown"
    
    if avg_song_age < 5:
        temporal_type = "Contemporary Focused"
        temporal_desc = "You prefer current music and trends"
    elif avg_song_age < 15:
        temporal_type = "Balanced"
        temporal_desc = "You enjoy both current and nostalgic music"
    else:
        temporal_type = "Nostalgic"
        temporal_desc = "You prefer older music and classic sounds"
    
    print(f"   • Average Song Age: {avg_song_age:.1f} years ({temporal_type})")
    print(f"   • Dominant Era: {dominant_era}")
    print(f"   • Psychology: {temporal_desc}")
    
    return {
        'novelty_seeking': 100 - repeat_rate,
        'taste_stability': avg_stability,
        'temporal_preference': temporal_type,
        'era_distribution': era_distribution
    }

def analyze_social_musical_behavior(tracks_df, artists_df):
    """Analyze social aspects of music taste"""
    print("\n👥 SOCIAL MUSICAL BEHAVIOR")
    print("="*60)
    
    # 1. Mainstream vs Independent Taste
    print("\n1. MAINSTREAM vs INDEPENDENT MUSIC PREFERENCE:")
    
    avg_popularity = tracks_df['popularity'].mean()
    popularity_std = tracks_df['popularity'].std()
    
    # Calculate artist concentration (few artists with many songs vs many artists with few songs)
    artist_track_counts = tracks_df.groupby('artist_name').size()
    concentration_score = artist_track_counts.std() / artist_track_counts.mean()
    
    if avg_popularity > 75:
        mainstream_level = "High Mainstream"
        social_desc = "You follow popular trends and enjoy widely-liked music"
    elif avg_popularity > 60:
        mainstream_level = "Moderate Mainstream"
        social_desc = "You balance popular hits with some unique choices"
    else:
        mainstream_level = "Independent"
        social_desc = "You prefer niche music and unique artists"
    
    print(f"   • Average Popularity: {avg_popularity:.1f}/100 ({mainstream_level})")
    print(f"   • Popularity Consistency: {popularity_std:.1f} (lower = more consistent taste)")
    print(f"   • Social Psychology: {social_desc}")
    
    # 2. Artist Loyalty vs Exploration
    print("\n2. ARTIST LOYALTY vs EXPLORATION:")
    
    top_artists = artists_df.groupby('artist_name')['track_count'].sum().sort_values(ascending=False)
    
    if len(top_artists) > 0:
        top_artist_dominance = top_artists.iloc[0] / top_artists.sum() * 100
        
        if top_artist_dominance > 20:
            loyalty_type = "High Loyalty"
            loyalty_desc = "You develop strong attachments to specific artists"
        elif top_artist_dominance > 10:
            loyalty_type = "Moderate Loyalty"
            loyalty_desc = "You have preferred artists but explore others"
        else:
            loyalty_type = "High Exploration"
            loyalty_desc = "You constantly discover new artists"
        
        print(f"   • Top Artist Dominance: {top_artist_dominance:.1f}% ({loyalty_type})")
        print(f"   • Total Unique Artists: {len(top_artists)}")
        print(f"   • Psychology: {loyalty_desc}")
    
    # 3. Conformity vs Individuality Analysis
    print("\n3. MUSICAL CONFORMITY vs INDIVIDUALITY:")
    
    # Calculate how much your taste aligns with "popular" choices
    high_popularity_tracks = (tracks_df['popularity'] > 80).mean() * 100
    explicit_content_rate = tracks_df['explicit'].mean() * 100
    
    conformity_score = 0
    if high_popularity_tracks > 60:
        conformity_score += 2
    elif high_popularity_tracks > 40:
        conformity_score += 1
    
    if explicit_content_rate < 10:  # Lower explicit content suggests conformity
        conformity_score += 1
    
    # Check for genre diversity (more diversity = less conformity)
    artist_diversity = len(tracks_df['artist_name'].unique()) / len(tracks_df)
    if artist_diversity < 0.3:  # Low diversity suggests conformity
        conformity_score += 1
    
    if conformity_score >= 3:
        conformity_level = "High Conformity"
        conformity_desc = "You tend to follow mainstream musical norms"
    elif conformity_score >= 2:
        conformity_level = "Moderate Conformity"
        conformity_desc = "You balance social acceptance with personal taste"
    else:
        conformity_level = "High Individuality"
        conformity_desc = "You express strong musical individuality"
    
    print(f"   • High Popularity Tracks: {high_popularity_tracks:.1f}% ({conformity_level})")
    print(f"   • Explicit Content Rate: {explicit_content_rate:.1f}%")
    print(f"   • Psychology: {conformity_desc}")

def analyze_emotional_musical_patterns(tracks_df):
    """Analyze emotional patterns in music choice"""
    print("\n💭 EMOTIONAL MUSICAL PATTERNS")
    print("="*60)
    
    # 1. Mood Regulation Analysis
    print("\n1. MUSIC FOR MOOD REGULATION:")
    
    # Analyze tempo patterns (duration as proxy for energy/tempo)
    avg_duration = tracks_df['duration_minutes'].mean()
    duration_variance = tracks_df['duration_minutes'].var()
    
    # Analyze ranking volatility (how much rankings change)
    rank_changes = []
    for track_artist in tracks_df.groupby(['track_name', 'artist_name']):
        track_data = track_artist[1]
        if len(track_data) > 1:
            rank_changes.append(track_data['rank_position'].std())
    
    avg_rank_volatility = np.mean(rank_changes) if rank_changes else 0
    
    if avg_duration > 4.5:
        mood_type = "Contemplative"
        mood_desc = "You use longer tracks for deep emotional processing"
    elif avg_duration < 3.5:
        mood_type = "Energizing"
        mood_desc = "You prefer shorter, energy-boosting tracks"
    else:
        mood_type = "Balanced"
        mood_desc = "You use music for various emotional needs"
    
    print(f"   • Average Track Duration: {avg_duration:.1f} minutes ({mood_type})")
    print(f"   • Duration Variance: {duration_variance:.1f} (higher = more diverse moods)")
    print(f"   • Emotional Psychology: {mood_desc}")
    
    # 2. Temporal Listening Patterns
    print("\n2. LISTENING PATTERN STABILITY:")
    
    # Analyze how consistent rankings are (stable = emotional regulation)
    if avg_rank_volatility > 10:
        emotional_stability = "Dynamic"
        stability_desc = "Your emotional connection to songs changes frequently"
    elif avg_rank_volatility > 5:
        emotional_stability = "Moderate"
        stability_desc = "You have some emotional consistency with occasional changes"
    else:
        emotional_stability = "Stable"
        stability_desc = "You have strong, stable emotional connections to music"
    
    print(f"   • Ranking Volatility: {avg_rank_volatility:.1f} ({emotional_stability})")
    print(f"   • Psychology: {stability_desc}")
    
    # 3. Complexity Preference (cognitive vs emotional processing)
    print("\n3. COGNITIVE vs EMOTIONAL PROCESSING:")
    
    # Use popularity and age as proxies
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    complexity_score = 0
    if tracks_df['song_age'].mean() > 10:  # Older music often more complex
        complexity_score += 1
    if tracks_df['duration_minutes'].mean() > 4:  # Longer songs often more complex
        complexity_score += 1
    if tracks_df['popularity'].mean() < 75:  # Less popular music often more complex
        complexity_score += 1
    
    if complexity_score >= 2:
        processing_type = "Cognitive"
        processing_desc = "You prefer complex music that engages analytical thinking"
    else:
        processing_type = "Emotional"
        processing_desc = "You prefer music that creates immediate emotional impact"
    
    print(f"   • Complexity Score: {complexity_score}/3 ({processing_type} Processing)")
    print(f"   • Psychology: {processing_desc}")

def generate_comprehensive_profile(tracks_df, artists_df):
    """Generate comprehensive psychological music profile"""
    print("\n🎭 COMPREHENSIVE MUSICAL PSYCHOLOGY PROFILE")
    print("="*70)
    
    # Collect all analysis results
    personality_dims = analyze_musical_personality_profile(tracks_df)
    listening_patterns = analyze_listening_psychology_patterns(tracks_df)
    
    # Generate overall profile
    print("\n🧬 YOUR MUSICAL DNA:")
    
    # Dominant personality trait
    dominant_trait = max(personality_dims.keys(), key=lambda x: personality_dims[x][0])
    print(f"   • Core Musical Personality: {dominant_trait}")
    
    # Key behavioral patterns
    print(f"   • Novelty Seeking: {listening_patterns['novelty_seeking']:.0f}%")
    print(f"   • Taste Stability: {listening_patterns['taste_stability']:.0f}%")
    print(f"   • Temporal Preference: {listening_patterns['temporal_preference']}")
    
    # Calculate overall psychological scores
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    
    openness_score = (
        len(tracks_df['artist_name'].unique()) / len(tracks_df) * 100 +  # Artist diversity
        (100 - tracks_df['popularity'].mean())  # Non-mainstream preference
    ) / 2
    
    conscientiousness_score = listening_patterns['taste_stability']
    
    extraversion_score = tracks_df['popularity'].mean()  # Popular music = social
    
    print(f"\n🧠 BIG FIVE MUSICAL CORRELATIONS:")
    print(f"   • Openness to Experience: {openness_score:.0f}/100")
    print(f"   • Conscientiousness: {conscientiousness_score:.0f}/100") 
    print(f"   • Extraversion: {extraversion_score:.0f}/100")
    
    # Music therapy insights
    print(f"\n🎵 MUSIC THERAPY INSIGHTS:")
    avg_duration = tracks_df['duration_minutes'].mean()
    if avg_duration > 4.5:
        print("   • Your preference for longer tracks suggests you use music for deep emotional processing")
    if listening_patterns['taste_stability'] > 60:
        print("   • Your stable music taste indicates music serves as emotional anchor")
    if openness_score > 70:
        print("   • Your diverse taste suggests music is important for cognitive stimulation")

def main():
    """Main psychological analysis application"""
    print("🧠 SPOTIFY MUSIC PSYCHOLOGY & STATISTICAL INFERENCE")
    print("="*65)
    print("Analyzing the psychology behind your music taste using research-based methods")
    
    # Load data
    tracks_df, artists_df = load_data()
    if tracks_df is None:
        return
    
    while True:
        print(f"\n🔬 PSYCHOLOGY ANALYSIS MENU")
        print("1. Musical Personality Profile (Big Five + Music Dimensions)")
        print("2. Listening Psychology Patterns (Novelty, Stability, Temporal)")
        print("3. Social Musical Behavior (Mainstream vs Independent)")
        print("4. Emotional Musical Patterns (Mood Regulation)")
        print("5. Comprehensive Psychological Profile")
        print("6. Statistical Significance Tests")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            analyze_musical_personality_profile(tracks_df)
            
        elif choice == "2":
            analyze_listening_psychology_patterns(tracks_df)
            
        elif choice == "3":
            analyze_social_musical_behavior(tracks_df, artists_df)
            
        elif choice == "4":
            analyze_emotional_musical_patterns(tracks_df)
            
        elif choice == "5":
            generate_comprehensive_profile(tracks_df, artists_df)
            
        elif choice == "6":
            run_statistical_tests(tracks_df)
            
        elif choice == "7":
            print("Thank you for exploring your musical psychology! 🎵🧠")
            break
            
        else:
            print("Invalid choice. Please try again.")

def run_statistical_tests(tracks_df):
    """Run statistical significance tests on music data"""
    print("\n📊 STATISTICAL SIGNIFICANCE TESTS")
    print("="*60)
    
    # Prepare data
    tracks_df['duration_minutes'] = tracks_df['duration_ms'] / 60000
    tracks_df['release_year'] = pd.to_datetime(tracks_df['release_date'], errors='coerce').dt.year
    tracks_df['song_age'] = datetime.now().year - tracks_df['release_year']
    
    # 1. Test: Do different time periods have significantly different popularity scores?
    print("\n1. POPULARITY DIFFERENCES ACROSS TIME PERIODS:")
    time_periods = tracks_df['time_range'].unique()
    if len(time_periods) > 1:
        period_groups = [tracks_df[tracks_df['time_range'] == period]['popularity'].dropna() 
                        for period in time_periods]
        
        try:
            f_stat, p_value = stats.f_oneway(*period_groups)
            print(f"   • F-statistic: {f_stat:.3f}")
            print(f"   • P-value: {p_value:.6f}")
            
            if p_value < 0.05:
                print("   • Result: SIGNIFICANT difference in popularity across time periods")
                print("   • Interpretation: Your taste in popular vs niche music changes over time")
            else:
                print("   • Result: NO significant difference in popularity across time periods")
                print("   • Interpretation: You maintain consistent mainstream/niche preferences")
        except:
            print("   • Unable to perform test (insufficient data)")
    
    # 2. Test: Correlation between song age and ranking
    print("\n2. CORRELATION: SONG AGE vs PERSONAL RANKING:")
    clean_data = tracks_df.dropna(subset=['song_age', 'rank_position'])
    if len(clean_data) > 10:
        correlation, p_value = stats.pearsonr(clean_data['song_age'], clean_data['rank_position'])
        print(f"   • Correlation coefficient: {correlation:.3f}")
        print(f"   • P-value: {p_value:.6f}")
        
        if p_value < 0.05:
            if correlation > 0:
                print("   • Result: SIGNIFICANT positive correlation")
                print("   • Interpretation: You tend to rank older songs lower (prefer newer music)")
            else:
                print("   • Result: SIGNIFICANT negative correlation")
                print("   • Interpretation: You tend to rank older songs higher (nostalgic preference)")
        else:
            print("   • Result: NO significant correlation")
            print("   • Interpretation: Song age doesn't influence your personal rankings")
    
    # 3. Test: Duration differences between explicit and non-explicit content
    print("\n3. DURATION DIFFERENCE: EXPLICIT vs NON-EXPLICIT CONTENT:")
    explicit_tracks = tracks_df[tracks_df['explicit'] == True]['duration_minutes'].dropna()
    non_explicit_tracks = tracks_df[tracks_df['explicit'] == False]['duration_minutes'].dropna()
    
    if len(explicit_tracks) > 5 and len(non_explicit_tracks) > 5:
        t_stat, p_value = stats.ttest_ind(explicit_tracks, non_explicit_tracks)
        print(f"   • Explicit tracks avg duration: {explicit_tracks.mean():.2f} minutes")
        print(f"   • Non-explicit tracks avg duration: {non_explicit_tracks.mean():.2f} minutes")
        print(f"   • T-statistic: {t_stat:.3f}")
        print(f"   • P-value: {p_value:.6f}")
        
        if p_value < 0.05:
            if explicit_tracks.mean() > non_explicit_tracks.mean():
                print("   • Result: SIGNIFICANT - Explicit tracks are longer")
                print("   • Interpretation: You prefer longer, more complex explicit content")
            else:
                print("   • Result: SIGNIFICANT - Non-explicit tracks are longer")
                print("   • Interpretation: You prefer longer, more complex clean content")
        else:
            print("   • Result: NO significant difference")
            print("   • Interpretation: Content type doesn't affect your duration preferences")
    
    # 4. Test: Ranking consistency analysis
    print("\n4. RANKING CONSISTENCY ANALYSIS:")
    song_rankings = tracks_df.groupby(['track_name', 'artist_name'])['rank_position'].agg(['count', 'std']).reset_index()
    consistent_songs = song_rankings[song_rankings['count'] > 1]
    
    if len(consistent_songs) > 5:
        avg_consistency = consistent_songs['std'].mean()
        consistency_std = consistent_songs['std'].std()
        
        print(f"   • Songs appearing multiple times: {len(consistent_songs)}")
        print(f"   • Average ranking standard deviation: {avg_consistency:.2f}")
        print(f"   • Consistency variation: {consistency_std:.2f}")
        
        if avg_consistency < 5:
            print("   • Result: HIGH ranking consistency")
            print("   • Interpretation: You have very stable preferences for specific songs")
        elif avg_consistency < 10:
            print("   • Result: MODERATE ranking consistency")
            print("   • Interpretation: Your song preferences are somewhat stable")
        else:
            print("   • Result: LOW ranking consistency")
            print("   • Interpretation: Your mood significantly affects song rankings")
    
    print("\n📈 STATISTICAL SUMMARY:")
    print(f"   • Total tracks analyzed: {len(tracks_df)}")
    print(f"   • Unique songs: {len(tracks_df.groupby(['track_name', 'artist_name']))}")
    print(f"   • Time periods covered: {len(tracks_df['time_range'].unique())}")
    print("   • Confidence level: 95% (p < 0.05 considered significant)")

if __name__ == "__main__":
    main()
