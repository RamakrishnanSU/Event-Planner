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
        
        /* 1. GLOBAL FONT SETTINGS */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', sans-serif;
        }

        /* 2. REMOVE DEFAULT PADDING */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* 3. CARDS & CONTAINERS */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #1A1C24;
            border-radius: 16px;
            border: 1px solid #2E303E;
            padding: 24px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        /* 4. BUTTONS */
        .stButton > button {
            background-color: #6C63FF;
            color: white !important;
            border-radius: 8px;
            border: none;
            font-weight: 500;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #5a52d5;
            box-shadow: 0px 4px 12px rgba(108, 99, 255, 0.3);
            transform: translateY(-2px);
        }

        /* 5. DATE BADGE */
        .date-badge {
            background-color: #2D2F3E;
            color: #6C63FF !important;
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            font-weight: 700;
            width: 70px;
            border: 1px solid #6C63FF;
        }
        
        /* 6. BANNER */
        .insight-banner {
            background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%);
            border-radius: 16px;
            padding: 30px;
            margin-top: 20px;
            color: white !important;
        }
        
        /* 7. CUSTOM DATAFRAME STYLING (For Attendees & Tasks) */
        /* This fixes the table header visibility */
        div[data-testid="stDataFrame"] {
            background-color: #1A1C24;
            border: 1px solid #2E303E;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* HIDE FOOTER */
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

local_css()
logic = EventLogic()

# --- HELPER: HEADER ---
def page_header(title, subtitle):
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 25px;">
            <div style="background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%); width: 8px; height: 45px; border-radius: 4px; margin-right: 15px;"></div>
            <div>
                <h1 style="margin: 0; font-size: 36px; font-weight: 800; color: white;">Event Pro</h1>
                <p style="margin: 0; color: #A0A0A0; font-size: 16px; font-weight: 500;">{title} &nbsp;|&nbsp; {subtitle}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- HELPER: EVENT CARD ---
def render_event_card(event, unique_idx):
    date_obj = pd.to_datetime(event['date'])
    day = date_obj.day
    month = date_obj.strftime("%b")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.2, 5, 2])
        with c1:
            st.markdown(f"""
                <div class="date-badge">
                    <div style="font-size: 24px; line-height: 24px; color: #6C63FF !important;">{day}</div>
                    <div style="font-size: 12px; text-transform: uppercase; color: #6C63FF !important;">{month}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"<h3 style='color: white; margin: 0 0 5px 0;'>{event['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style='color: white; font-size: 14px;'>
                    📅 {date_obj.year} &nbsp; | &nbsp; ⏰ {event['time']} <br>
                    📍 {event['location']} <br>
                    <span style='color: #A0A0A0; font-size: 13px; font-style: italic;'>{event['description']}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with c3:
            st.write("")
            st.write("")
            if st.button("View Details >", key=f"btn_{event['id']}_{unique_idx}", use_container_width=True):
                st.session_state['view_event_id'] = event['id']
                st.rerun()

# --- INITIALIZE STATE ---
if 'view_event_id' not in st.session_state: st.session_state['view_event_id'] = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>Event Pro</h2>", unsafe_allow_html=True)
    menu = st.radio("", ["Dashboard", "Attendees", "Task Manager", "Analytics"], label_visibility="collapsed")
    st.divider()
    st.info("💡 Pro Tip: Use Analytics to track RSVP trends.")

# --- PAGE 1: DASHBOARD ---
if menu == "Dashboard":
    if st.session_state['view_event_id'] is None:
        c1, c2 = st.columns([6, 1.5])
        with c1: page_header("Dashboard", "All Events")
        with c2:
            st.write("")
            if st.button("➕ Create Event"): st.session_state['show_create'] = not st.session_state.get('show_create', False)

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
                        res = logic.add_event(name, date, time_val, loc, desc)
                        if "Error" in res:
                            st.error(res)
                        else:
                            st.success("Event Saved!")
                            time.sleep(1)
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
        # DETAIL VIEW
        events_df = logic.get_events()
        event_row = events_df[events_df['id'] == st.session_state['view_event_id']]
        
        if not event_row.empty:
            event = event_row.iloc[0]
            page_header("Dashboard", event['name'])
            
            if st.button("← Back"):
                st.session_state['view_event_id'] = None
                st.rerun()
            
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**📅 Date:** {event['date']}")
                c2.markdown(f"**⏰ Time:** {event['time']}")
                c3.markdown(f"**📍 Location:** {event['location']}")
                st.divider()
                st.markdown(f"**Description:** {event['description']}")
                
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
    page_header("Analytics", "Insights")
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        c1, c2 = st.columns(2)
        with c1: st.pyplot(logic.get_rsvp_pie_chart(selected_id))
        with c2: st.pyplot(logic.get_task_status_chart(selected_id))
    else: st.warning("No data.")

# --- PAGE 3: ATTENDEES ---
elif menu == "Attendees":
    page_header("Attendees", "Guest List")
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        attendees = logic.get_attendees(selected_id)
        if not attendees.empty:
            st.dataframe(attendees[['name', 'email', 'rsvp', 'role']], use_container_width=True, hide_index=True)
        else:
            st.info("No guests found.")

        st.write("")
        with st.expander("➕ Add Guest", expanded=True):
            with st.form("add_guest"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Name")
                email = c2.text_input("Email")
                rsvp = st.selectbox("RSVP", ["Confirmed", "Pending"])
                if st.form_submit_button("Add"):
                    logic.add_attendee(selected_id, name, email, rsvp, "Guest", "")
                    st.success("Added")
                    st.rerun()

# --- PAGE 4: TASK MANAGER ---
elif menu == "Task Manager":
    page_header("Tasks", "Tracker")
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        tasks = logic.get_tasks(selected_id)
        if not tasks.empty:
            st.dataframe(tasks[['task_name', 'status', 'priority', 'deadline']], use_container_width=True, hide_index=True)
        else:
            st.info("No tasks found.")

        st.write("")
        with st.expander("➕ Add Task", expanded=True):
            with st.form("add_task"):
                tname = st.text_input("Task")
                tstat = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
                tdue = st.date_input("Due")
                if st.form_submit_button("Add"):
                    logic.add_task(selected_id, tname, tstat, tdue)
                    st.success("Added")
                    st.rerun()
