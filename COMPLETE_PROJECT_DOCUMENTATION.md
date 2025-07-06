# Spotify Musical Identity Analysis Project
## Complete Documentation

**Project Period:** 2020-2025 (6 years)  
**Research Focus:** Musical identity formation during formative years  
**Core Hypothesis:** Reminiscence bump theory and identity-driven music preferences  

---

## 📁 Project Structure

```
Spotify Project/
├── data/                   # Manual CSV data files
├── scripts/               # All analysis scripts
├── visualizations/        # Generated HTML visualizations
├── outputs/              # Database files and processed data
└── documentation/        # Project documentation
```

---

## 🎯 Research Questions

1. **Does music taste change as you grow up?**
   - Hypothesis: No, due to reminiscence bump effect
   - Music preferences formed during ages 10-30 persist throughout life

2. **What drives music preference and genre magnitude?**
   - Identity construction vs. emotional regulation
   - Social influences and personality factors

---

## 📊 Data Sources

### Manual Data (CSV-based)
- **File:** `data/Spotify_data.csv`
- **Content:** Spotify Wrapped data (2020-2025)
- **Structure:** artist_name, rank, year, dimension
- **Usage:** Historical analysis, "Wrapped" style insights

### API Data (SQL-based)
- **Database:** `outputs/listening_trends.db`
- **Content:** Real-time Spotify Web API data
- **Usage:** Current listening patterns, detailed analytics

---

## 🛠️ Scripts Documentation

### 1. **musical_identity_comprehensive_analysis.py**
**Data Source:** CSV (`data/Spotify_data.csv`)  
**Purpose:** Core Wrapped analysis - generates 4 main visualizations  

**What it collects:**
- Artist diversity evolution over 6 years
- Genre/dimension breakdown by year
- Artist persistence (how many years each artist appears)
- Year-by-year artist leaderboards

**Outputs:**
- `artist_diversity_evolution.html`
- `genre_breakdown_evolution.html`
- `artist_leaderboard_by_year.html`
- `artist_persistence_analysis.html`

**Key insights:**
- Musical diversity trends during formative years
- Evidence of reminiscence bump in artist loyalty
- Identity formation through music preference patterns

---

### 2. **create_focused_timeline.py**
**Data Source:** CSV (`data/Spotify_data.csv`)  
**Purpose:** Focused timeline for 5 key artists  

**Focus Artists:**
- Zach Bryan (Peak: 2022, 16.8 score)
- Morgan Wade (Peak: 2023, 6.0 score)
- mike. (Peak: 2022, 13.3 score, present all 6 years)
- Bon Iver (Peak: 2024, 14.7 score)
- Morgan Wallen (Peak: 2021, 18.0 score)

**What it collects:**
- Year-by-year listening scores (songs + rank bonus)
- Artist presence patterns across the 6-year period
- Peak listening years for each artist

**Output:**
- `spotify_wrapped_timeline.html`

**Key insights:**
- Individual artist evolution patterns
- Consistency vs. discovery phases
- Peak listening periods and their significance

---

### 3. **spotify_data_analysis.py**
**Data Source:** API + SQL (`outputs/listening_trends.db`)  
**Purpose:** Current listening pattern analysis  

**What it collects:**
- Recently played tracks (last 50)
- Current top artists and tracks
- Listening frequency patterns
- Audio features (danceability, energy, valence, etc.)

**Database tables created:**
- `tracks` - Track metadata and audio features
- `artists` - Artist information
- `listening_history` - Timestamped listening events

**Key insights:**
- Real-time listening behavior
- Audio feature preferences
- Current vs. historical taste comparison

---

### 4. **spotify_visualizations.py**
**Data Source:** API + SQL (`outputs/listening_trends.db`)  
**Purpose:** Generate current listening visualizations  

**What it collects:**
- Audio feature distributions
- Top artists/tracks rankings
- Listening time patterns
- Genre distributions

**Outputs:**
- Multiple HTML visualizations for current data

---

### 5. **spotify_psychology_insights.py**
**Data Source:** API + SQL (`outputs/listening_trends.db`)  
**Purpose:** Psychological analysis of music preferences  

**What it collects:**
- Audio feature psychology correlations
- Mood regulation patterns
- Preference stability measures
- Personality-music connections

**Key insights:**
- Music as identity expression
- Emotional regulation through music
- Psychological drivers of preference

---

### 6. **spotify_psychology_visualizations.py**
**Data Source:** API + SQL (`outputs/listening_trends.db`)  
**Purpose:** Psychology-focused visualizations  

**What it collects:**
- Big Five personality correlations
- Mood-music relationships
- Audio feature psychology mappings
- Identity formation indicators

---

### 7. **identity_vs_mood_analysis.py**
**Data Source:** API + SQL (`outputs/listening_trends.db`)  
**Purpose:** Test identity vs. mood hypothesis  

**What it collects:**
- Audio feature consistency (identity indicator)
- Temporal listening patterns (mood indicator)
- Artist loyalty vs. exploration balance
- Long-term preference stability

**Key hypothesis testing:**
- Identity construction vs. emotional regulation
- Surface vs. deep motivations for music choice

---

### 8. **historical_data_collector.py**
**Data Source:** API (`outputs/listening_trends.db`)  
**Purpose:** Continuous data collection for longitudinal analysis  

**What it collects:**
- Ongoing listening history
- Track and artist metadata
- Audio feature evolution
- Preference change tracking

---

### 9. **serve_visualizations.py**
**Data Source:** None (utility script)  
**Purpose:** HTTP server for viewing visualizations  

**Function:**
- Serves HTML files on `http://localhost:8080`
- Enables easy browsing of all generated visualizations
- Auto-opens browser for immediate viewing

---

## 📈 Key Research Findings

### Artist Loyalty Patterns
- **mike.** appears in all 6 years (47 total songs) - core identity artist
- **Morgan Wallen** peaks early (2021) then declines - possible phase
- **Zach Bryan** shows recent emergence (2022-2024) - new identity formation

### Musical Diversity Evolution
- Measured by unique artists per year
- Tracks identity crystallization vs. exploration phases
- Higher diversity may indicate continued identity formation

### Genre/Dimension Shifts
- Maps onto identity development stages
- Tracks movement between musical dimensions
- Identifies stable vs. transitional preferences

---

## 🔬 Theoretical Framework

### Reminiscence Bump Theory
- Memories from ages 10-30 are most vivid and persistent
- Music preferences formed during this period remain stable
- Explains why formative-year music persists throughout life

### Identity vs. Mood Functions
- **Surface motivation:** Emotional regulation (what people think)
- **Deep motivation:** Identity construction (actual driver)
- Music serves as non-verbal identity communication

### Musical Identity Formation
- Music as symbolic boundary creation
- Preference patterns reveal identity development
- Artist loyalty indicates core identity elements

---

## 📋 Usage Instructions

### Running the Complete Analysis
```bash
# 1. CSV-based analysis (Wrapped data)
python scripts/musical_identity_comprehensive_analysis.py
python scripts/create_focused_timeline.py

# 2. API-based analysis (current data)
python scripts/spotify_data_analysis.py
python scripts/spotify_visualizations.py
python scripts/spotify_psychology_insights.py
python scripts/identity_vs_mood_analysis.py

# 3. Serve visualizations
python scripts/serve_visualizations.py
```

### Viewing Results
- Start the server: `python scripts/serve_visualizations.py`
- Visit: `http://localhost:8080`
- Browse all generated HTML visualizations

---

## 📚 Research Applications

This project provides empirical data for research on:
- Musical identity formation during emerging adulthood
- Reminiscence bump effects in music preference
- Identity vs. emotional motivations for music listening
- Longitudinal preference stability and change
- Social and psychological factors in music taste development

---

## 🎵 Core Insights Summary

1. **Identity Persistence:** Artists like mike. appearing consistently across all years suggest core identity formation
2. **Preference Evolution:** Different peak years for different artists reveal identity development phases
3. **Musical Diversity:** Changes in artist variety indicate ongoing vs. crystallized identity formation
4. **Genre Stability:** Dimension analysis reveals which musical elements remain stable vs. changeable
5. **Temporal Patterns:** Timeline analysis shows when major preference shifts occur

This comprehensive analysis provides both personal insights and broader research applications for understanding music preference development during formative years.
