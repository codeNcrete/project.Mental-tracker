# app.py - COMPLETE MENTAL WELLNESS TRACKER (Phase 1)
import streamlit as st
import pandas as pd
import datetime
import calendar
import os

# Initialize session state
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.date.today().isoformat()

# Page configuration
st.set_page_config(
    page_title="Mindful Tracker",
    page_icon="🧠",
    layout="wide"
)

# ========== DATABASE FUNCTIONS ==========
class MoodDatabase:
    def __init__(self):
        self.data_file = 'mood_data.csv'
        self.setup_database()
    
    def setup_database(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.data_file):
            df = pd.DataFrame(columns=[
                'date', 'mood', 'sleep_hours', 'exercise', 
                'diet_quality', 'journal', 'timestamp'
            ])
            df.to_csv(self.data_file, index=False)
    
    def save_mood_entry(self, date, mood, sleep_hours=None, exercise=None, diet_quality=None, journal=""):
        """Save a new mood entry"""
        df = pd.read_csv(self.data_file)
        
        # Check if entry already exists for this date
        existing_index = df[df['date'] == date].index
        
        new_entry = {
            'date': date,
            'mood': mood,
            'sleep_hours': sleep_hours,
            'exercise': exercise,
            'diet_quality': diet_quality,
            'journal': journal,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if not existing_index.empty:
            # Update existing entry
            df.loc[existing_index[0]] = new_entry
        else:
            # Add new entry
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        
        df.to_csv(self.data_file, index=False)
        return True
    
    def get_mood_entry(self, date):
        """Get mood entry for specific date"""
        df = pd.read_csv(self.data_file)
        entry = df[df['date'] == date]
        if not entry.empty:
            return entry.iloc[0].to_dict()
        return None
    
    def get_all_entries(self):
        """Get all mood entries"""
        try:
            df = pd.read_csv(self.data_file)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except:
            return pd.DataFrame()
    
    def get_weekly_average(self, date):
        """Calculate weekly average mood"""
        df = self.get_all_entries()
        if df.empty:
            return None
        
        target_date = pd.to_datetime(date)
        start_date = target_date - datetime.timedelta(days=6)
        
        weekly_data = df[(df['date'] >= start_date) & (df['date'] <= target_date)]
        
        if not weekly_data.empty:
            return weekly_data['mood'].mean()
        return None

# Initialize database
db = MoodDatabase()

# ========== UTILITY FUNCTIONS ==========
def get_mood_emoji(mood_score):
    """Convert mood score to emoji"""
    mood_emojis = {
        1: "😢",  # Very Sad
        2: "😔",  # Sad
        3: "😐",  # Neutral
        4: "😊",  # Happy
        5: "😄"   # Very Happy
    }
    return mood_emojis.get(mood_score, "😐")

def get_mood_color(mood_score):
    """Get color for mood score"""
    mood_colors = {
        1: "#FF6B6B",  # Red
        2: "#FFA726",  # Orange
        3: "#FFD93D",  # Yellow
        4: "#6BCF7F",  # Light Green
        5: "#4ECDC4"   # Dark Green
    }
    return mood_colors.get(mood_score, "#CCCCCC")

def get_mood_suggestion(mood_score):
    """Get suggestion based on mood"""
    suggestions = {
        1: "💙 Be kind to yourself today. Try deep breathing or a short walk. Remember, this feeling will pass.",
        2: "🌱 Small steps matter. Consider talking to a friend or listening to your favorite music.",
        3: "⚖️ Balance is key. Maybe try a new hobby or activity to boost your mood.",
        4: "🌟 Great energy! Share your positivity with others or enjoy your favorite activity.",
        5: "🎉 Amazing! Your positive mindset is shining. Keep spreading the good vibes!"
    }
    return suggestions.get(mood_score, "Take a moment to appreciate today.")

# ========== CALENDAR FUNCTIONS ==========
def display_mood_calendar(selected_date):
    """Display a monthly calendar with mood colors"""
    
    # Get current month and year from selected date
    current_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
    year = current_date.year
    month = current_date.month
    
    # Get mood data
    df = db.get_all_entries()
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.subheader(f"{month_name} {year}")
    
    # Day headers
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")
    
    # Display calendar days
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")  # Empty day
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                entry = None
                
                if not df.empty:
                    date_entries = df[df['date'] == date_str]
                    if not date_entries.empty:
                        entry = date_entries.iloc[0]
                
                display_day(cols[i], day, entry, date_str)

def display_day(col, day, entry, date_str):
    """Display a single day in the calendar"""
    
    if entry is not None and pd.notna(entry['mood']):
        mood_score = int(entry['mood'])
        emoji = get_mood_emoji(mood_score)
        color = get_mood_color(mood_score)
        
        # Create colored box with mood
        col.markdown(
            f"""
            <div style='
                background-color: {color}; 
                border-radius: 10px; 
                padding: 5px; 
                text-align: center;
                color: black;
                margin: 2px;
                min-height: 60px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            '>
                <strong>{day}</strong>
                <div style='font-size: 1.2em;'>{emoji}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # Empty day - no mood logged
        col.markdown(
            f"""
            <div style='
                background-color: #F0F0F0; 
                border-radius: 10px; 
                padding: 5px; 
                text-align: center;
                color: #666;
                margin: 2px;
                min-height: 60px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            '>
                {day}
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Make day clickable using a unique key
    if col.button("📝", key=f"btn_{date_str}", help=f"Log mood for {date_str}"):
        st.session_state.selected_date = date_str
        st.rerun()

# ========== MAIN APP SECTIONS ==========
def show_calendar():
    """Display the mood calendar"""
    st.header("📅 Your Mood Calendar")
    
    # Date navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Month navigation
        current_date = datetime.datetime.strptime(st.session_state.selected_date, "%Y-%m-%d")
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        
        with nav_col1:
            if st.button("⬅️ Prev"):
                prev_month = current_date - datetime.timedelta(days=30)
                st.session_state.selected_date = prev_month.date().isoformat()
                st.rerun()
        
        with nav_col3:
            if st.button("Next ➡️"):
                next_month = current_date + datetime.timedelta(days=30)
                st.session_state.selected_date = next_month.date().isoformat()
                st.rerun()
    
    # Display calendar
    display_mood_calendar(st.session_state.selected_date)
    
    # Selected date info
    st.subheader(f"Selected Date: {st.session_state.selected_date}")
    entry = db.get_mood_entry(st.session_state.selected_date)
    
    if entry and pd.notna(entry['mood']):
        mood_score = int(entry['mood'])
        st.write(f"**Mood:** {get_mood_emoji(mood_score)} ({mood_score}/5)")
        if entry.get('journal') and str(entry['journal']).strip():
            st.write(f"**Journal:** {entry['journal']}")
        
        # Edit button
        if st.button("✏️ Edit This Entry"):
            st.session_state.edit_mode = True
            st.rerun()
    else:
        st.info("No mood logged for this date. Click the log button above to add an entry!")
        
        # Quick log button
        if st.button("📝 Quick Log Mood for Today"):
            st.session_state.edit_mode = True
            st.rerun()

def log_mood():
    """Log mood for selected date"""
    st.header("📊 Log Your Mood")
    
    # Date selector
    selected_date = st.date_input(
        "Select Date",
        datetime.datetime.strptime(st.session_state.selected_date, "%Y-%m-%d").date()
    )
    
    # Update session state
    st.session_state.selected_date = selected_date.isoformat()
    
    # Check for existing entry
    existing_entry = db.get_mood_entry(st.session_state.selected_date)
    
    with st.form("mood_form"):
        st.subheader(f"How are you feeling on {selected_date}?")
        
        # Mood selection with emojis
        mood_options = {
            1: "😢 Very Sad",
            2: "😔 Sad", 
            3: "😐 Neutral",
            4: "😊 Happy",
            5: "😄 Very Happy"
        }
        
        mood_score = st.radio(
            "Select your mood:",
            options=list(mood_options.keys()),
            format_func=lambda x: mood_options[x],
            horizontal=True,
            index=2  # Default to neutral
        )
        
        # Display selected mood preview
        st.write(f"**Selected:** {get_mood_emoji(mood_score)} {mood_options[mood_score].split(' ')[1]}")
        
        # Journal entry
        journal_default = ""
        if existing_entry and pd.notna(existing_entry.get('journal')):
            journal_default = existing_entry['journal']
            
        journal_text = st.text_area(
            "How was your day? (Optional)",
            value=journal_default,
            placeholder="Share your thoughts, feelings, or anything you'd like to remember about today...",
            height=100
        )
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Mood Entry")
        
        if submitted:
            # Save to database
            db.save_mood_entry(
                date=st.session_state.selected_date,
                mood=mood_score,
                journal=journal_text
            )
            
            st.success("✅ Mood saved successfully!")
            st.balloons()
            
            # Show suggestion
            st.info(f"**💡 Suggestion:** {get_mood_suggestion(mood_score)}")

def show_analytics():
    """Show basic analytics"""
    st.header("📈 Your Mood Analytics")
    
    df = db.get_all_entries()
    
    if df.empty:
        st.info("Start logging your mood to see analytics here!")
        return
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_mood = df['mood'].mean()
        st.metric("Average Mood", f"{avg_mood:.1f}/5")
    
    with col2:
        entries_count = len(df)
        st.metric("Total Entries", entries_count)
    
    with col3:
        best_mood = df['mood'].max()
        st.metric("Best Mood", f"{best_mood}/5")
    
    with col4:
        consistency = df['mood'].std()
        st.metric("Consistency", f"{consistency:.2f}")
    
    # Weekly average for current week
    weekly_avg = db.get_weekly_average(st.session_state.selected_date)
    if weekly_avg:
        st.write(f"**This week's average mood:** {weekly_avg:.1f}/5")
    
    # Simple mood trend
    st.subheader("Mood Trend Over Time")
    if not df.empty:
        df_sorted = df.sort_values('date')
        st.line_chart(df_sorted.set_index('date')['mood'])
    
    # Mood distribution
    st.subheader("Mood Distribution")
    mood_counts = df['mood'].value_counts().sort_index()
    st.bar_chart(mood_counts)

# ========== MAIN APP ==========
def main():
    # Sidebar
    st.sidebar.title("🧠 Mindful Tracker")
    st.sidebar.markdown("Track your mood, build better habits")
    
    menu = st.sidebar.radio("Navigation", ["📅 Calendar", "📊 Log Mood", "📈 Analytics"])
    
    # Main content
    st.title("🧠 Mindful Tracker")
    st.markdown("Your personal mental wellness companion")
    
    if menu == "📅 Calendar":
        show_calendar()
    elif menu == "📊 Log Mood":
        log_mood()
    elif menu == "📈 Analytics":
        show_analytics()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip**: Log your mood daily to see patterns and insights!")

if __name__ == "__main__":
    main()