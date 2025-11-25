import streamlit as st
import pandas as pd
from logic import EventLogic
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Event Pro", page_icon="📅", layout="wide")

# --- CUSTOM CSS ---

def local_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* 1. GLOBAL TEXT COLOR FIX */
        html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, div {
            font-family: 'Inter', sans-serif;
            color: #FFFFFF !important; /* Force White Everywhere */
        }
        
        /* 2. FORCE DARK BACKGROUND */
        .stApp {
            background-color: #0E1117;
        }
        
        /* 3. HEADER BAR */
        header[data-testid="stHeader"] {
            background-color: #0E1117;
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: #0E1117;
            border-right: 1px solid #2E303E;
        }

        /* --- CARDS --- */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #1A1C24;
            border-radius: 16px;
            border: 1px solid #2E303E;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
            padding: 24px;
        }
        
        /* --- METRICS --- */
        div[data-testid="stMetric"] {
            background-color: #262730 !important;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #2E303E;
        }
        div[data-testid="stMetricLabel"] > label { color: #A0A0A0 !important; }
        div[data-testid="stMetricValue"] { color: #FFFFFF !important; }

        /* --- BUTTONS --- */
        .stButton > button {
            background-color: #6C63FF;
            color: white !important;
            border-radius: 8px;
            border: none;
            font-weight: 500;
        }
        .stButton > button:hover {
            background-color: #5a52d5;
        }

        /* --- DATE BADGE --- */
        .date-badge {
            background-color: #2D2F3E;
            color: #6C63FF !important; /* Keep badge purple */
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            font-weight: 700;
            width: 70px;
            border: 1px solid #6C63FF;
        }
        .date-day { font-size: 24px; line-height: 24px; color: #6C63FF !important; }
        .date-month { font-size: 12px; text-transform: uppercase; color: #6C63FF !important; }

        /* --- BANNER --- */
        .insight-banner {
            background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%);
            border-radius: 16px;
            padding: 30px;
            color: white !important;
            margin-top: 20px;
        }
        
        /* --- INPUTS --- */
        .stTextInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #0E1117; 
            color: white !important;
            border-radius: 8px;
            border: 1px solid #4F4F4F;
        }
        
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

# --- HELPER: UNIFIED HEADER FUNCTION ---
def page_header(title, subtitle):
    """Displays the consistent Event Pro header on every page"""
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 25px;">
            <div style="background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%); width: 8px; height: 45px; border-radius: 4px; margin-right: 15px;"></div>
            <div>
                <h1 style="margin: 0; font-size: 36px; font-weight: 800; color: white;">Event Pro</h1>
                <p style="margin: 0; color: #A0A0A0; font-size: 16px; font-weight: 500;">{title} &nbsp;|&nbsp; {subtitle}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'view_event_id' not in st.session_state:
    st.session_state['view_event_id'] = None

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 30px;'>
            <div style='background: #6C63FF; width: 30px; height: 30px; border-radius: 8px;'></div>
            <h2 style='margin:0; font-size: 20px; font-weight: 700;'>Event Pro</h2>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio("", ["Dashboard", "Attendees", "Task Manager", "Analytics"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("""
        <div style='background-color: #1E2130; padding: 15px; border-radius: 12px; color: #8F90A6; font-size: 13px;'>
            <strong style='color: white;'>Pro Tip</strong><br>
            Use Analytics to track RSVP trends.
        </div>
    """, unsafe_allow_html=True)

# --- HELPER: RENDER CARD ---

def render_event_card(event, unique_idx):
    date_obj = pd.to_datetime(event['date'])
    day = date_obj.day
    month = date_obj.strftime("%b")
    
    with st.container(border=True):
        col_badge, col_info, col_btn = st.columns([1.2, 5, 2])
        
        with col_badge:
            st.markdown(f"""
                <div class="date-badge">
                    <div class="date-day">{day}</div>
                    <div class="date-month">{month}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_info:
            # 1. Force Title to White
            st.markdown(f"<h3 style='color: white; margin: 0 0 5px 0;'>{event['name']}</h3>", unsafe_allow_html=True)
            
            # 2. Force Details to White (Changed from #A0A0A0)
            st.markdown(f"""
                <div style='color: white; font-size: 14px;'>
                    📅 {date_obj.year} &nbsp; | &nbsp; ⏰ {event['time']} <br>
                    📍 {event['location']} <br>
                    <span style='color: #E0E0E0; font-size: 13px; font-style: italic;'>{event['description']}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with col_btn:
            st.write("")
            st.write("")
            if st.button("View Details >", key=f"btn_{event['id']}_{unique_idx}", use_container_width=True):
                st.session_state['view_event_id'] = event['id']
                st.rerun()

# --- PAGE 1: DASHBOARD ---
if menu == "Dashboard":
    if st.session_state['view_event_id'] is None:
        # === LIST VIEW ===
        col_header, col_add = st.columns([6, 1.5])
        
        with col_header:
            # 1. NEW HEADER
            page_header("Dashboard", "All Events")
        
        with col_add:
            st.write("") 
            if st.button("➕ Create Event"):
                st.session_state['show_create'] = not st.session_state.get('show_create', False)

        if st.session_state.get('show_create', False):
            with st.container(border=True):
                st.subheader("Create New Event")
                with st.form("new_event"):
                    c1, c2 = st.columns(2)
                    name = c1.text_input("Event Name")
                    loc = c2.text_input("Location")
                    c3, c4 = st.columns(2)
                    date = c3.date_input("Date")
                    time_val = c4.time_input("Time")
                    desc = st.text_area("Description")
                    if st.form_submit_button("Save Event", use_container_width=True):
                        logic.add_event(name, date, time_val, loc, desc)
                        st.session_state['show_create'] = False
                        st.rerun()

        events_df = logic.get_events()
        if not events_df.empty:
            events_df['date'] = pd.to_datetime(events_df['date'])
            events_df = events_df.sort_values(by='date')
            for idx, (_, event) in enumerate(events_df.iterrows()):
                render_event_card(event, idx)
        else:
            st.info("No events found.")

    else:
        # === DETAIL VIEW ===
        events_df = logic.get_events()
        event = events_df[events_df['id'] == st.session_state['view_event_id']].iloc[0]
        
        # 1. NEW HEADER
        page_header("Dashboard", event['name'])
        
        if st.button("← Back to Dashboard"):
            st.session_state['view_event_id'] = None
            st.rerun()
        
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**📅 Date:** {event['date']}")
            c2.markdown(f"**⏰ Time:** {event['time']}")
            c3.markdown(f"**📍 Location:** {event['location']}")
            st.divider()
            st.markdown(f"**📝 Description:**\n{event['description']}")
            
        tab_attendees, tab_tasks = st.tabs(["👥 Guest List", "✅ Tasks"])
        
        with tab_attendees:
            attendees = logic.get_attendees(event['id'])
            if not attendees.empty:
                st.dataframe(attendees[['name', 'email', 'rsvp', 'role']], use_container_width=True, hide_index=True)
            else:
                st.info("No guests registered yet.")
                
        with tab_tasks:
            tasks = logic.get_tasks(event['id'])
            if not tasks.empty:
                st.dataframe(tasks[['task_name', 'status', 'priority', 'deadline']], use_container_width=True, hide_index=True)
            else:
                st.info("No tasks assigned.")

# --- PAGE 2: ANALYTICS ---
elif menu == "Analytics":
    # 1. NEW HEADER
    page_header("Analytics", "Insights & Reports")
    
    events_df = logic.get_events()
    if events_df.empty:
        st.warning("No data to analyze.")
    else:
        event_names = dict(zip(events_df['id'], events_df['name']))
        col_empty, col_sel = st.columns([3, 1])
        with col_sel:
            selected_id = st.selectbox("Select Event", options=event_names.keys(), format_func=lambda x: event_names[x], label_visibility="collapsed")

        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.subheader("RSVP Distribution")
                fig_rsvp = logic.get_rsvp_pie_chart(selected_id)
                if fig_rsvp: st.pyplot(fig_rsvp)
                else: st.info("No data")

        with c2:
            with st.container(border=True):
                st.subheader("Task Progress")
                fig_task = logic.get_task_status_chart(selected_id)
                if fig_task: st.pyplot(fig_task)
                else: st.info("No data")

        attendees = logic.get_attendees(selected_id)
        tasks = logic.get_tasks(selected_id)
        total_guests = len(attendees)
        confirmed = len(attendees[attendees['rsvp'] == 'Confirmed']) if not attendees.empty else 0
        pending_tasks = len(tasks[tasks['status'] != 'Completed']) if not tasks.empty else 0
        completed_tasks = len(tasks[tasks['status'] == 'Completed']) if not tasks.empty else 0

        st.markdown(f"""
            <div class="insight-banner">
                <h3 style="color: white; margin-bottom: 20px;">Quick Insights for {event_names[selected_id]}</h3>
                <div style="display: flex; justify-content: space-between;">
                    <div><div class="insight-label">Total Guests</div><div class="insight-metric">{total_guests}</div></div>
                    <div><div class="insight-label">Confirmed</div><div class="insight-metric">{confirmed}</div></div>
                    <div><div class="insight-label">Pending Tasks</div><div class="insight-metric">{pending_tasks}</div></div>
                    <div><div class="insight-label">Completed</div><div class="insight-metric">{completed_tasks}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- PAGE 3: ATTENDEES ---
elif menu == "Attendees":
    # 1. NEW HEADER
    page_header("Attendees", "Guest Management")
    
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", options=event_names.keys(), format_func=lambda x: event_names[x])
        
        tab_list, tab_add = st.tabs(["Guest List", "Add Guest"])
        
        with tab_list:
            attendees = logic.get_attendees(selected_id)
            if not attendees.empty:
                st.dataframe(attendees[['name', 'email', 'rsvp', 'role']], use_container_width=True, hide_index=True)
            else:
                st.info("No attendees yet.")
        
        with tab_add:
            with st.container(border=True):
                c1, c2 = st.columns(2)
                name = c1.text_input("Name")
                email = c2.text_input("Email")
                c3, c4 = st.columns(2)
                role = c3.selectbox("Role", ["Guest", "VIP", "Speaker"])
                rsvp = c4.selectbox("RSVP", ["Confirmed", "Pending", "Declined"])
                if st.button("Add Attendee", use_container_width=True):
                    logic.add_attendee(selected_id, name, email, rsvp, role, "")
                    st.success("Added!")
                    st.rerun()

# --- PAGE 4: TASK MANAGER ---
elif menu == "Task Manager":
    # 1. NEW HEADER
    page_header("Tasks", "Project Tracking")
    
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Project", options=event_names.keys(), format_func=lambda x: event_names[x])
        
        c_add, c_view = st.columns([1, 2])
        
        with c_add:
            with st.container(border=True):
                st.subheader("New Task")
                t_name = st.text_input("Task Name")
                t_stat = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Delayed"])
                t_due = st.date_input("Due Date")
                if st.button("Add Task", use_container_width=True):
                    logic.add_task(selected_id, t_name, t_stat, t_due)
                    st.rerun()
                    
        with c_view:
            tasks = logic.get_tasks(selected_id)
            if not tasks.empty:
                for _, t in tasks.iterrows():
                    with st.container(border=True):
                        tc1, tc2 = st.columns([3, 1])
                        tc1.markdown(f"**{t['task_name']}**")
                        status_color = "#4CAF50" if t['status'] == "Completed" else "#FF9800" if t['status'] == "In Progress" else "#F44336"
                        tc1.caption(f"Due: {t['deadline']}")
                        tc2.markdown(f"<div style='color:{status_color}; font-weight:bold; text-align:right'>{t['status']}</div>", unsafe_allow_html=True)
                        if t['status'] != "Completed":
                            if tc2.button("Done", key=f"done_{t['task_name']}"):
                                logic.update_task_status(selected_id, t['task_name'], "Completed")
                                st.rerun()
            else:

                st.info("No active tasks.")

