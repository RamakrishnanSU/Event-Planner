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
        
        /* 1. GLOBAL TEXT & BACKGROUND */
        html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, div {
            font-family: 'Inter', sans-serif;
            color: #FFFFFF !important;
        }
        .stApp, header[data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #0E1117 !important;
        }
        
        /* 2. CARDS */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #1A1C24;
            border-radius: 16px;
            border: 1px solid #2E303E;
            padding: 24px;
        }
        
        /* 3. INPUTS */
        .stTextInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #0E1117 !important; 
            color: white !important;
            border: 1px solid #4F4F4F !important;
            border-radius: 8px;
        }
        
        /* 4. BUTTONS */
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
        }
        .metric-value {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 0px;
        }
        .metric-label {
            font-size: 14px;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* 7. POPUPS */
        div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
            background-color: #1A1C24 !important;
            border: 1px solid #2E303E !important;
        }
        
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

local_css()
logic = EventLogic()

# --- HEADER HELPER ---
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

# --- EVENT CARD HELPER ---
def render_event_card(event, unique_idx):
    date_obj = pd.to_datetime(event['date'])
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.2, 5, 2])
        with c1:
            st.markdown(f"""
                <div class="date-badge">
                    <div style="font-size: 24px; line-height: 24px; color: #6C63FF !important;">{date_obj.day}</div>
                    <div style="font-size: 12px; text-transform: uppercase; color: #6C63FF !important;">{date_obj.strftime('%b')}</div>
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
            
            tab1, tab2 = st.tabs(["👥 Guest List", "✅ Tasks"])
            with tab1:
                att = logic.get_attendees(event['id'])
                if not att.empty:
                    st.dataframe(att[['name', 'email', 'rsvp', 'role']].style.set_properties(**{'background-color': '#1A1C24', 'color': 'white', 'border-color': '#2E303E'}), use_container_width=True, hide_index=True)
                else: st.info("No guests.")
            with tab2:
                tasks = logic.get_tasks(event['id'])
                if not tasks.empty:
                    st.dataframe(tasks[['task_name', 'status', 'deadline']].style.set_properties(**{'background-color': '#1A1C24', 'color': 'white', 'border-color': '#2E303E'}), use_container_width=True, hide_index=True)
                else: st.info("No tasks.")

# --- PAGE 2: ANALYTICS (UPDATED TO MATCH IMAGE) ---
elif menu == "Analytics":
    page_header("Analytics", "Insights")
    events_df = logic.get_events()
    
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        # --- ROW 1: CHARTS ---
        c1, c2 = st.columns(2)
        
        with c1:
            with st.container(border=True):
                st.markdown("### RSVP Distribution")
                fig1 = logic.get_rsvp_pie_chart(selected_id)
                if fig1: st.pyplot(fig1)
                else: st.info("No guests registered.")

        with c2:
            with st.container(border=True):
                st.markdown("### Task Progress")
                fig2 = logic.get_task_status_chart(selected_id)
                if fig2: st.pyplot(fig2)
                else: st.info("No tasks created.")

        # --- ROW 2: QUICK INSIGHTS BANNER ---
        attendees = logic.get_attendees(selected_id)
        tasks = logic.get_tasks(selected_id)
        
        total_guests = len(attendees)
        confirmed = len(attendees[attendees['rsvp'] == 'Confirmed']) if not attendees.empty else 0
        pending_tasks = len(tasks[tasks['status'] != 'Completed']) if not tasks.empty else 0
        completed_tasks = len(tasks[tasks['status'] == 'Completed']) if not tasks.empty else 0
        
        st.markdown(f"""
            <div class="insight-banner">
                <h2 style="color: white; margin-bottom: 25px;">Quick Insights for {event_names[selected_id]}</h2>
                <div style="display: flex; justify-content: space-between; text-align: left;">
                    <div><div class="metric-label">Total Guests</div><div class="metric-value">{total_guests}</div></div>
                    <div><div class="metric-label">Confirmed</div><div class="metric-value">{confirmed}</div></div>
                    <div><div class="metric-label">Pending Tasks</div><div class="metric-value">{pending_tasks}</div></div>
                    <div><div class="metric-label">Completed</div><div class="metric-value">{completed_tasks}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("No events found. Please create an event first.")

# --- PAGE 3: ATTENDEES ---
elif menu == "Attendees":
    page_header("Attendees", "Guest List")
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        att = logic.get_attendees(selected_id)
        if not att.empty:
            st.dataframe(att[['name', 'email', 'rsvp', 'role']].style.set_properties(**{'background-color': '#1A1C24', 'color': 'white', 'border-color': '#2E303E'}), use_container_width=True, hide_index=True)
        else: st.info("No guests.")
        
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

# --- PAGE 4: TASKS ---
elif menu == "Task Manager":
    page_header("Tasks", "Tracker")
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        tasks = logic.get_tasks(selected_id)
        if not tasks.empty:
            st.dataframe(tasks[['task_name', 'status', 'deadline']].style.set_properties(**{'background-color': '#1A1C24', 'color': 'white', 'border-color': '#2E303E'}), use_container_width=True, hide_index=True)
        else: st.info("No tasks.")
        
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
