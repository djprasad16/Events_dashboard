import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Page config
st.set_page_config(page_title="Event Summary", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("events.csv", parse_dates=["event_date"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

facility = st.sidebar.multiselect(
    "Facility",
    options=df["facility"].unique(),
    default=df["facility"].unique()
)

event_types = [
    "Bathroomentry", "Bathroomexit",
    "Bedentry", "Bedexit",
    "Fall", "Longstay", "Entry", "Exit"
]

# Updated the default date range to dynamically show the latest month based on available data.
latest_month_start = df["event_date"].max().replace(day=1)
latest_month_end = df["event_date"].max()

# Date range selector in sidebar with separate start and end dates on same line
st.sidebar.subheader("Date Range")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start",
        value=latest_month_start,
        key="start_date"
    )
with col2:
    end_date = st.date_input(
        "End",
        value=latest_month_end,
        key="end_date"
    )

# Integrated the event type selection into the sidebar
with st.sidebar:
    st.subheader("Event Type")
    selected_event = option_menu(
        None,  # Removed the heading
        options=event_types,
        default_index=event_types.index("Fall"),
        menu_icon=None,  # Disabled menu icons
        orientation="vertical",  # Changed orientation to vertical for sidebar
        styles={
            "container": {"padding": "0px", "background-color": "#f9f9f9"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#eee", "padding": "5px 10px"},
            "nav-link-selected": {"background-color": "#02ab21", "color": "white", "padding": "5px 10px"},
            "icon": {"display": "none"}  # Removed icons explicitly
        }
    )

# Map the selected event type to its lowercase equivalent for DataFrame operations.
selected_event_column = selected_event.lower()

st.title("Event Summary")

# Apply filters
filtered_df = df[
    (df["facility"].isin(facility)) &
    (df["event_date"] >= pd.to_datetime(start_date)) &
    (df["event_date"] <= pd.to_datetime(end_date))
]

# KPI
total_events = filtered_df[selected_event_column].sum()

col1, col2 = st.columns(2)
col1.metric("Overall Event Count", f"{int(total_events):,}")
col2.metric("Days Selected", filtered_df["event_date"].nunique())

# Timeline chart
timeline_df = (
    filtered_df
    .groupby("event_date")[selected_event_column]
    .sum()
    .reset_index()
)

# Ensure `selected_event_column` is treated as a list to avoid Series-related errors.
timeline_df["total"] = timeline_df[[selected_event_column]].sum(axis=1)

fig = px.line(
    timeline_df,
    x="event_date",
    y="total",
    markers=True,
    title="Timeline"
)

# Adjusted the y-axis tick values to show integers only.
fig.update_layout(
    yaxis=dict(
        tickmode="linear",
        tick0=1,
        dtick=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# Optional: Detailed table
with st.expander("View Daily Event Details"):
    st.dataframe(filtered_df.sort_values("event_date"))
