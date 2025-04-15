import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import json
import os
from PIL import Image
import io
import base64

# Configure Streamlit page
st.set_page_config(page_title="Social Media Content Planner", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .platform-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metrics-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .post-card {
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        margin-bottom: 0.5rem;
        background-color: white;
    }
    .tag {
        background-color: #e1f5fe;
        color: #0277bd;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-right: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def load_data():
    """Load saved posts or return empty dataframe if none exists"""
    try:
        if os.path.exists("social_media_posts.json"):
            with open("social_media_posts.json", "r") as f:
                data = json.load(f)
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    
    # Default empty dataframe
    return pd.DataFrame({
        "title": [],
        "content": [],
        "platform": [],
        "scheduled_date": [],
        "scheduled_time": [],
        "status": [],
        "image": [],
        "likes": [],
        "comments": [],
        "shares": [],
        "reach": []
    })

def save_data(df):
    """Save dataframe to JSON file"""
    try:
        with open("social_media_posts.json", "w") as f:
            json.dump(df.to_dict(orient="records"), f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def get_platform_icon(platform):
    """Return the appropriate emoji icon for a platform"""
    icons = {
        "Facebook": "📘",
        "Instagram": "📸",
        "Twitter": "🐦",
        "LinkedIn": "🔗",
        "TikTok": "📱",
        "Pinterest": "📌"
    }
    return icons.get(platform, "📱")

def encode_image(image_file):
    """Encode uploaded image file to base64 string for storage"""
    if image_file is not None:
        bytes_data = image_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

def decode_image(base64_string):
    """Decode base64 string to image for display"""
    if base64_string:
        img_data = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(img_data))
    return None

# Initialize session state variables
if "posts_df" not in st.session_state:
    st.session_state.posts_df = load_data()
if "current_view" not in st.session_state:
    st.session_state.current_view = "Calendar"
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()
if "expanded_post" not in st.session_state:
    st.session_state.expanded_post = None

# Generate demo data if the dataframe is empty
if len(st.session_state.posts_df) == 0:
    # Create some demo data
    demo_dates = [
        datetime.now().date() + timedelta(days=i) 
        for i in range(-5, 15)
    ]
    
    demo_platforms = ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok"]
    demo_statuses = ["Published", "Scheduled", "Draft", "Published", "Scheduled"]
    
    demo_data = []
    for i in range(20):
        platform = demo_platforms[i % len(demo_platforms)]
        status = demo_statuses[i % len(demo_statuses)]
        likes = 0
        comments = 0
        shares = 0
        reach = 0
        
        # Add some performance metrics for published posts
        if status == "Published":
            likes = int(100 + 50 * (i % 7))
            comments = int(10 + 5 * (i % 5))
            shares = int(5 + 3 * (i % 4))
            reach = int(500 + 100 * (i % 10))
        
        demo_data.append({
            "title": f"Demo Post {i+1}",
            "content": f"This is example content for {platform} post #{i+1}. #demo #socialmedia",
            "platform": platform,
            "scheduled_date": demo_dates[i % len(demo_dates)].strftime("%Y-%m-%d"),
            "scheduled_time": f"{8 + (i % 8)}:00",
            "status": status,
            "image": None,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "reach": reach
        })
    
    st.session_state.posts_df = pd.DataFrame(demo_data)
    save_data(st.session_state.posts_df)

# Main layout
st.markdown('<h1 class="main-header">📊 Social Media Content Planner</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    view_options = ["Calendar", "Create Post", "Analytics", "Settings"]
    selected_view = st.radio("Choose View", view_options, index=view_options.index(st.session_state.current_view))
    
    if selected_view != st.session_state.current_view:
        st.session_state.current_view = selected_view
        st.rerun()
    
    st.markdown("---")
    
    # Quick filters
    st.markdown("## 🔍 Quick Filters")
    platform_filter = st.multiselect(
        "Platform",
        options=["All"] + sorted(st.session_state.posts_df["platform"].unique().tolist()),
        default="All"
    )
    status_filter = st.multiselect(
        "Status",
        options=["All"] + sorted(st.session_state.posts_df["status"].unique().tolist()),
        default="All"
    )
    
    # Apply filters to the dataframe
    filtered_df = st.session_state.posts_df.copy()
    if platform_filter and "All" not in platform_filter:
        filtered_df = filtered_df[filtered_df["platform"].isin(platform_filter)]
    if status_filter and "All" not in status_filter:
        filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]

# Calendar View
if st.session_state.current_view == "Calendar":
    # Get current month and year
    current_date = datetime.now().date()
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = current_date.month
    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = current_date.year
    
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        if st.button("⬅️ Previous Month"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()
    
    with col2:
        month_name = calendar.month_name[st.session_state.calendar_month]
        st.markdown(f"## {month_name} {st.session_state.calendar_year}")
    
    with col3:
        if st.button("Next Month ➡️"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()
    
    # Create calendar
    cal = calendar.monthcalendar(st.session_state.calendar_year, st.session_state.calendar_month)
    
    # Create columns for each day of the week
    cols = st.columns(7)
    for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        cols[i].markdown(f"<div style='text-align: center; font-weight: bold;'>{day_name}</div>", unsafe_allow_html=True)
    
    # Create a dataframe with just the current month's posts
    month_start = f"{st.session_state.calendar_year}-{st.session_state.calendar_month:02d}-01"
    month_end = (datetime.strptime(month_start, "%Y-%m-%d") + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    month_end = month_end.strftime("%Y-%m-%d")
    
    month_posts = filtered_df[
        (filtered_df["scheduled_date"] >= month_start) & 
        (filtered_df["scheduled_date"] <= month_end)
    ]
    
    # Create calendar grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                # Empty cell for days not in this month
                cols[i].markdown("<div style='height: 100px; background-color: #f5f5f5; border-radius: 5px;'></div>", unsafe_allow_html=True)
            else:
                date_str = f"{st.session_state.calendar_year}-{st.session_state.calendar_month:02d}-{day:02d}"
                is_current_date = date_str == current_date.strftime("%Y-%m-%d")
                is_selected_date = date_str == st.session_state.selected_date.strftime("%Y-%m-%d")
                
                # Style for the date cell
                bg_color = "#e3f2fd" if is_selected_date else "#ffffff"
                border = "2px solid #1976d2" if is_current_date else "1px solid #e0e0e0"
                
                # Get posts for this day
                day_posts = month_posts[month_posts["scheduled_date"] == date_str]
                day_post_count = len(day_posts)
                
                # Create platform indicators
                platform_indicators = ""
                for platform in day_posts["platform"].unique():
                    platform_indicators += f"<span class='platform-icon'>{get_platform_icon(platform)}</span>"
                
                # Display date cell with post count and platform indicators
                cell_content = f"""
                <div style='
                    height: 100px; 
                    background-color: {bg_color}; 
                    border: {border}; 
                    border-radius: 5px; 
                    padding: 5px; 
                    position: relative; 
                    overflow: hidden;'
                    onclick=''
                >
                    <div style='font-weight: bold;'>{day}</div>
                    <div style='margin-top: 5px;'>
                        {platform_indicators}
                    </div>
                    <div style='position: absolute; bottom: 5px; right: 5px; font-size: 0.8rem;'>
                        {day_post_count} post{'' if day_post_count == 1 else 's'}
                    </div>
                </div>
                """
                
                if cols[i].markdown(cell_content, unsafe_allow_html=True):
                    # Set the selected date when a cell is clicked
                    st.session_state.selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    st.rerun()
    
    # Display posts for the selected date
    st.markdown(f"## Posts for {st.session_state.selected_date.strftime('%B %d, %Y')}")
    
    selected_date_str = st.session_state.selected_date.strftime("%Y-%m-%d")
    selected_date_posts = filtered_df[filtered_df["scheduled_date"] == selected_date_str]
    
    if len(selected_date_posts) == 0:
        st.info("No posts scheduled for this date.")
    else:
        for idx, post in selected_date_posts.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class='post-card'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                            <div>
                                <span class='platform-icon'>{get_platform_icon(post['platform'])}</span>
                                <strong>{post['platform']}</strong> • 
                                <span class='tag'>{post['status']}</span> • 
                                {post['scheduled_time']}
                            </div>
                        </div>
                        <div><strong>{post['title']}</strong></div>
                        <div style='margin-top: 0.5rem;'>{post['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col2:
                    st.button("Edit", key=f"edit_{idx}", help="Edit this post")
                    st.button("Delete", key=f"delete_{idx}", help="Delete this post")

# Create Post View
elif st.session_state.current_view == "Create Post":
    st.markdown("## 📝 Create New Post")
    
    with st.form("new_post_form"):
        post_title = st.text_input("Post Title", placeholder="Enter a title for your post")
        post_content = st.text_area("Content", placeholder="Write your post content here...")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            post_platform = st.selectbox(
                "Platform",
                options=["Facebook", "Instagram", "Twitter", "LinkedIn", "TikTok", "Pinterest"]
            )
        
        with col2:
            post_date = st.date_input("Scheduled Date", value=datetime.now().date())
        
        with col3:
            post_time = st.time_input("Scheduled Time", value=datetime.now().time())
        
        post_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        
        post_status = st.selectbox(
            "Status",
            options=["Draft", "Scheduled", "Published"]
        )
        
        submit_button = st.form_submit_button("Save Post")
        
        if submit_button:
            if not post_title:
                st.error("Please enter a post title")
            elif not post_content:
                st.error("Please enter post content")
            else:
                # Encode image if provided
                encoded_image = encode_image(post_image) if post_image else None
                
                # Create new post
                new_post = {
                    "title": post_title,
                    "content": post_content,
                    "platform": post_platform,
                    "scheduled_date": post_date.strftime("%Y-%m-%d"),
                    "scheduled_time": post_time.strftime("%H:%M"),
                    "status": post_status,
                    "image": encoded_image,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "reach": 0
                }
                
                # Add to dataframe
                st.session_state.posts_df = pd.concat([
                    st.session_state.posts_df, 
                    pd.DataFrame([new_post])
                ], ignore_index=True)
                
                # Save data
                if save_data(st.session_state.posts_df):
                    st.success("Post saved successfully!")
                    # Clear form (this requires a rerun)
                    st.session_state.clear_form = True
                    st.rerun()

# Analytics View
elif st.session_state.current_view == "Analytics":
    st.markdown("## 📊 Performance Analytics")
    
    # Only analyze published posts
    published_posts = filtered_df[filtered_df["status"] == "Published"].copy()
    
    if len(published_posts) == 0:
        st.info("No published posts to analyze yet.")
    else:
        # Convert scheduled_date to datetime
        published_posts["date"] = pd.to_datetime(published_posts["scheduled_date"])
        
        # Overall metrics
        total_posts = len(published_posts)
        total_engagement = published_posts["likes"].sum() + published_posts["comments"].sum() + published_posts["shares"].sum()
        total_reach = published_posts["reach"].sum()
        avg_engagement_per_post = total_engagement / total_posts if total_posts > 0 else 0
        
        # Display overall metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class='metrics-card'>
                <div style='font-size: 0.9rem; color: #757575;'>Total Posts</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: #1976d2;'>{}</div>
            </div>
            """.format(total_posts), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='metrics-card'>
                <div style='font-size: 0.9rem; color: #757575;'>Total Engagement</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: #1976d2;'>{}</div>
            </div>
            """.format(total_engagement), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='metrics-card'>
                <div style='font-size: 0.9rem; color: #757575;'>Total Reach</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: #1976d2;'>{}</div>
            </div>
            """.format(total_reach), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class='metrics-card'>
                <div style='font-size: 0.9rem; color: #757575;'>Avg. Engagement/Post</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: #1976d2;'>{:.1f}</div>
            </div>
            """.format(avg_engagement_per_post), unsafe_allow_html=True)
        
        st.markdown("### Engagement by Platform")
        
        # Aggregate data by platform
        platform_data = published_posts.groupby("platform").agg({
            "likes": "sum",
            "comments": "sum",
            "shares": "sum",
            "reach": "sum"
        }).reset_index()
        
        # Calculate engagement rate
        platform_data["engagement_rate"] = (
            (platform_data["likes"] + platform_data["comments"] + platform_data["shares"]) / 
            platform_data["reach"] * 100
        )
        
        # Create stacked bar chart for engagement by platform
        fig = px.bar(
            platform_data,
            x="platform",
            y=["likes", "comments", "shares"],
            labels={"value": "Count", "platform": "Platform", "variable": "Metric"},
            title="Engagement by Platform",
            color_discrete_sequence=["#1976d2", "#ff7043", "#66bb6a"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Engagement rate by platform
        fig_rate = px.bar(
            platform_data,
            x="platform",
            y="engagement_rate",
            labels={"engagement_rate": "Engagement Rate (%)", "platform": "Platform"},
            title="Engagement Rate by Platform",
            color="platform",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        st.plotly_chart(fig_rate, use_container_width=True)
        
        # Performance over time
        st.markdown("### Performance Over Time")
        
        # Aggregate data by date
        time_data = published_posts.groupby("date").agg({
            "likes": "sum",
            "comments": "sum",
            "shares": "sum",
            "reach": "sum"
        }).reset_index()
        
        # Create line chart for performance over time
        fig_time = px.line(
            time_data,
            x="date",
            y=["likes", "comments", "shares", "reach"],
            labels={"value": "Count", "date": "Date", "variable": "Metric"},
            title="Performance Metrics Over Time",
            color_discrete_sequence=["#1976d2", "#ff7043", "#66bb6a", "#9c27b0"]
        )
        
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Best performing posts
        st.markdown("### Top Performing Posts")
        
        # Add total engagement column
        published_posts["total_engagement"] = published_posts["likes"] + published_posts["comments"] + published_posts["shares"]
        
        # Sort by total engagement
        top_posts = published_posts.sort_values("total_engagement", ascending=False).head(5)
        
        for idx, post in top_posts.iterrows():
            with st.container():
                st.markdown(f"""
                <div class='post-card' style='border-left: 4px solid #66bb6a;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <div>
                            <span class='platform-icon'>{get_platform_icon(post['platform'])}</span>
                            <strong>{post['platform']}</strong> • 
                            {post['scheduled_date']}
                        </div>
                        <div>
                            <span class='tag' style='background-color: #e8f5e9; color: #2e7d32;'>
                                {post['total_engagement']} Engagements
                            </span>
                        </div>
                    </div>
                    <div><strong>{post['title']}</strong></div>
                    <div style='margin-top: 0.5rem;'>{post['content']}</div>
                    <div style='display: flex; margin-top: 0.5rem;'>
                        <div style='margin-right: 1rem;'>❤️ {post['likes']}</div>
                        <div style='margin-right: 1rem;'>💬 {post['comments']}</div>
                        <div>🔄 {post['shares']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Settings View
elif st.session_state.current_view == "Settings":
    st.markdown("## ⚙️ Settings")
    
    with st.expander("Export Data", expanded=True):
        st.write("Export your post data to CSV or JSON format.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to CSV"):
                # Save dataframe to CSV for download
                csv = st.session_state.posts_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="social_media_posts.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Export to JSON"):
                # Save dataframe to JSON for download
                json_str = st.session_state.posts_df.to_json(orient="records", indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="social_media_posts.json",
                    mime="application/json"
                )
    
    with st.expander("Import Data"):
        st.write("Import posts from a CSV or JSON file.")
        
        uploaded_file = st.file_uploader("Upload file", type=["csv", "json"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    imported_df = pd.read_csv(uploaded_file)
                    st.success(f"Successfully imported {len(imported_df)} posts from CSV.")
                else:
                    imported_df = pd.read_json(uploaded_file)
                    st.success(f"Successfully imported {len(imported_df)} posts from JSON.")
                
                if st.button("Replace Current Data with Imported Data"):
                    st.session_state.posts_df = imported_df
                    save_data(st.session_state.posts_df)
                    st.success("Data replaced successfully!")
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error importing data: {e}")
    
    with st.expander("Reset Application"):
        st.write("⚠️ Warning: This will delete all your posts and reset the application.")
        
        if st.button("Reset All Data", help="This will delete all your posts"):
            st.session_state.posts_df = pd.DataFrame({
                "title": [],
                "content": [],
                "platform": [],
                "scheduled_date": [],
                "scheduled_time": [],
                "status": [],
                "image": [],
                "likes": [],
                "comments": [],
                "shares": [],
                "reach": []
            })
            save_data(st.session_state.posts_df)
            st.success("Application reset successfully!")
            st.rerun()
