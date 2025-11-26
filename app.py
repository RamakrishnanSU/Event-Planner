import streamlit as st
import pandas as pd
from logic import EventLogic
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Event Pro", page_icon="📅", layout="wide")

# --- THEME MANAGEMENT ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def set_css():
    # === DARK MODE CSS (Your existing perfect dark mode) ===
    dark_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, div {
            font-family: 'Inter', sans-serif;
            color: #FFFFFF !important;
        }
        .stApp, header[data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #0E1117 !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #1A1C24;
            border-radius: 16px;
            border: 1px solid #2E303E;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
        }
        .stTextInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #0E1117 !important; 
            color: white !important;
            border: 1px solid #4F4F4F !important;
        }
        .date-badge {
            background-color: #2D2F3E;
            color: #6C63FF !important;
            border: 1px solid #6C63FF;
        }
        div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
            background-color: #1A1C24 !important;
            border: 1px solid #2E303E !important;
        }
        /* Table Styling Dark */
        div[data-testid="stDataFrame"] { background-color: #1A1C24; }
        </style>
    """

    # === LIGHT MODE CSS (Fixed for Contrast) ===
    light_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* Force Dark Text on Light Background */
        html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, div {
            font-family: 'Inter', sans-serif;
            color: #111827 !important; /* Very Dark Grey (Almost Black) */
        }
        
        /* Off-White Background for the Page (Makes cards pop) */
        .stApp, header[data-testid="stHeader"] {
            background-color: #F3F4F6 !important; 
        }
        
        /* Keep Sidebar Dark (Like EventHorizon) */
        [data-testid="stSidebar"] {
            background-color: #0E1117 !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label {
            color: #FFFFFF !important; /* Force Sidebar text white */
        }
        
        /* Pure White Cards with Shadow */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #FFFFFF;
            border-radius: 16px;
            border: 1px solid #E5E7EB;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        /* Inputs (White background, Dark Text) */
        .stTextInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #FFFFFF !important; 
            color: #111827 !important;
            border: 1px solid #D1D5DB !important;
        }
        
        /* Date Badge (Light Purple) */
        .date-badge {
            background-color: #F5F3FF;
            color: #6C63FF !important;
            border: 1px solid #6C63FF;
        }
        
        /* Popups (Light) */
        div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
        }
        li[role="option"] {
            color: #111827 !important;
            background-color: #FFFFFF !important;
        }
        li[role="option"]:hover {
            background-color: #F3F4F6 !important;
        }
        </style>
    """

    # === SHARED CSS (Buttons, Banner) ===
    shared_css = """
        <style>
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
        .insight-banner {
            background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%);
            border-radius: 16px;
            padding: 30px;
            margin-top: 20px;
            color: white !important;
        }
        /* Banner text must always be white regardless of theme */
        .insight-banner div, .insight-banner h2, .insight-banner span {
            color: white !important;
        }
        .date-badge {
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            font-weight: 700;
            width: 70px;
        }
        footer {visibility: hidden;}
        </style>
    """

    if st.session_state.theme == 'dark':
        st.markdown(dark_css + shared_css, unsafe_allow_html=True)
    else:
        st.markdown(light_css + shared_css, unsafe_allow_html=True)

set_css()
logic = EventLogic()

# --- HELPER FUNCTIONS ---
def page_header(title, subtitle):
    # Title color is handled by CSS (White in dark mode, Black in light mode)
    # We add a gradient bar for style
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 25px;">
            <div style="background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%); width: 8px; height: 45px; border-radius: 4px; margin-right: 15px;"></div>
            <div>
                <h1 style="margin: 0; font-size: 36px; font-weight: 800;">Event Pro</h1>
                <p style="margin: 0; opacity: 0.7; font-size: 16px; font-weight: 500;">{title} &nbsp;|&nbsp; {subtitle}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- INITIALIZE STATE ---
if 'view_event_id' not in st.session_state: st.session_state['view_event_id'] = None

# --- SIDEBAR ---
with st.sidebar:
    # Sidebar header is always white because of CSS rule
    st.markdown("<h2 style='color: white;'>Event Pro</h2>", unsafe_allow_html=True)
    menu = st.radio("", ["Dashboard", "Attendees", "Task Manager", "Analytics"], label_visibility="collapsed")
    
    st.divider()
    
    # Theme Switcher
    st.markdown("### 🎨 Appearance")
    mode = st.toggle("Light Mode", value=(st.session_state.theme == 'light'))
    if mode and st.session_state.theme != 'light':
        st.session_state.theme = 'light'
        st.rerun()
    elif not mode and st.session_state.theme != 'dark':
        st.session_state.theme = 'dark'
        st.rerun()

# --- EVENT CARD RENDERER ---
def render_event_card(event, unique_idx):
    date_obj = pd.to_datetime(event['date'])
    day = date_obj.day
    month = date_obj.strftime("%b")
    
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.2, 5, 2, 0.5])
        
        with c1:
            st.markdown(f"""
                <div class="date-badge">
                    <div style="font-size: 24px; line-height: 24px;">{day}</div>
                    <div style="font-size: 12px; text-transform: uppercase;">{month}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"<h3 style='margin: 0 0 5px 0;'>{event['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style='opacity: 0.8; font-size: 14px;'>
                    📅 {date_obj.year} &nbsp; | &nbsp; ⏰ {event['time']} <br>
                    📍 {event['location']} <br>
                    <span style='font-size: 13px; font-style: italic;'>{event['description']}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with c3:
            st.write("")
            st.write("")
            if st.button("View Details >", key=f"btn_{event['id']}_{unique_idx}", use_container_width=True):
                st.session_state['view_event_id'] = event['id']
                st.rerun()
        
        with c4:
            st.write("")
            st.write("")
            # Delete Button
            if st.button("🗑️", key=f"del_{event['id']}_{unique_idx}", help="Delete"):
                logic.delete_event(event['id'])
                st.toast("Deleted successfully!")
                time.sleep(1)
                st.rerun()

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
            
            # Logic for table styling based on theme
            is_dark = st.session_state.theme == 'dark'
            table_bg = '#1A1C24' if is_dark else '#FFFFFF'
            table_color = 'white' if is_dark else '#111827'
            
            with tab_attendees:
                attendees = logic.get_attendees(event['id'])
                if not attendees.empty:
                    styled_df = attendees[['name', 'email', 'rsvp', 'role']].style.set_properties(**{
                        'background-color': table_bg,
                        'color': table_color,
                        'border-color': '#2E303E'
                    })
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No guests registered yet.")
                    
            with tab_tasks:
                tasks = logic.get_tasks(event['id'])
                if not tasks.empty:
                    styled_tasks = tasks[['task_name', 'status', 'priority', 'deadline']].style.set_properties(**{
                        'background-color': table_bg,
                        'color': table_color,
                        'border-color': '#2E303E'
                    })
                    st.dataframe(styled_tasks, use_container_width=True, hide_index=True)
                else:
                    st.info("No tasks assigned.")
        else:
            st.warning("Event deleted.")
            if st.button("Go Back"):
                st.session_state['view_event_id'] = None
                st.rerun()

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
        
        is_dark = st.session_state.theme == 'dark'
        table_bg = '#1A1C24' if is_dark else '#FFFFFF'
        table_color = 'white' if is_dark else '#111827'

        if not attendees.empty:
            styled_df = attendees[['name', 'email', 'rsvp', 'role']].style.set_properties(**{
                'background-color': table_bg,
                'color': table_color,
                'border-color': '#2E303E'
            })
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
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
        
        is_dark = st.session_state.theme == 'dark'
        table_bg = '#1A1C24' if is_dark else '#FFFFFF'
        table_color = 'white' if is_dark else '#111827'

        if not tasks.empty:
            styled_tasks = tasks[['task_name', 'status', 'priority', 'deadline']].style.set_properties(**{
                'background-color': table_bg,
                'color': table_color,
                'border-color': '#2E303E'
            })
            st.dataframe(styled_tasks, use_container_width=True, hide_index=True)
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
