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
        
        /* GLOBAL TEXT & BACKGROUND */
        html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span, div {
            font-family: 'Inter', sans-serif;
            color: #FFFFFF !important;
        }
        .stApp, header[data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #0E1117 !important;
        }
        
        /* CONTAINERS & CARDS */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #1A1C24;
            border-radius: 16px;
            border: 1px solid #2E303E;
            padding: 24px;
        }
        
        /* INPUT FIELDS */
        .stTextInput input, .stDateInput input, .stTimeInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #0E1117 !important; 
            color: white !important;
            border: 1px solid #4F4F4F !important;
            border-radius: 8px;
        }
        
        /* BUTTONS */
        .stButton > button {
            background-color: #6C63FF;
            color: white !important;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #5a52d5;
            box-shadow: 0px 4px 12px rgba(108, 99, 255, 0.3);
            transform: translateY(-2px);
        }

        /* CUSTOM ATTENDEE ROW STYLING */
        .attendee-row {
            background-color: #1A1C24;
            border-bottom: 1px solid #2E303E;
            padding: 15px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .role-badge {
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 12px;
            background-color: #2D2F3E;
            color: #A0A0A0 !important;
            border: 1px solid #4F4F4F;
            text-transform: uppercase;
            font-weight: 700;
        }
        .status-dot {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }
        
        /* FIX POPUPS */
        div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
            background-color: #1A1C24 !important;
            border: 1px solid #2E303E !important;
        }
        
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

local_css()
logic = EventLogic()

# --- HELPER FUNCTIONS ---
def page_header(title, subtitle):
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 25px;">
            <div style="background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%); width: 8px; height: 45px; border-radius: 4px; margin-right: 15px;"></div>
            <div>
                <h1 style="margin: 0; font-size: 32px; font-weight: 800; color: white;">Event Pro</h1>
                <p style="margin: 0; color: #A0A0A0; font-size: 15px; font-weight: 500;">{title} &nbsp;|&nbsp; {subtitle}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_attendee_row(att):
    """Renders a single attendee as a custom HTML row"""
    # Color logic
    color = "#4CAF50" if att['rsvp'] == 'Confirmed' else "#FFA500"
    
    st.markdown(f"""
        <div class="attendee-row">
            <div style="flex: 2;">
                <div style="font-weight: 600; font-size: 16px;">{att['name']}</div>
                <div style="font-size: 13px; color: #8F90A6 !important;">{att['email']}</div>
            </div>
            <div style="flex: 1; text-align: center;">
                <span class="role-badge">{att['role']}</span>
            </div>
            <div style="flex: 1; text-align: right; font-size: 14px; font-weight: 500;">
                <span class="status-dot" style="background-color: {color};"></span>
                <span style="color: {color} !important;">{att['rsvp']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_event_card(event, unique_idx):
    date_obj = pd.to_datetime(event['date'])
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.2, 5, 2])
        with c1:
            st.markdown(f"""
                <div style="background-color:#2D2F3E; color:#6C63FF !important; padding:12px; border-radius:12px; text-align:center; border:1px solid #6C63FF;">
                    <div style="font-size:24px; font-weight:700; color:#6C63FF !important;">{date_obj.day}</div>
                    <div style="font-size:12px; text-transform:uppercase; color:#6C63FF !important;">{date_obj.strftime('%b')}</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"<h3 style='margin:0; color:white !important;'>{event['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#A0A0A0 !important; font-size:14px; margin-top:5px;'>📅 {date_obj.year} &nbsp;|&nbsp; 📍 {event['location']}</div>", unsafe_allow_html=True)
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
            if st.button("➕ New Event"): st.session_state['show_create'] = not st.session_state.get('show_create', False)

        # CREATE EVENT FORM
        if st.session_state.get('show_create', False):
            with st.container(border=True):
                st.subheader("Create New Event")
                with st.form("new_event"):
                    c1, c2 = st.columns(2)
                    name = c1.text_input("Event Name", placeholder="e.g. Summer Gala")
                    loc = c2.text_input("Location", placeholder="e.g. Grand Hall")
                    c3, c4 = st.columns(2)
                    date = c3.date_input("Date")
                    time_val = c4.time_input("Time")
                    desc = st.text_area("Description")
                    
                    st.write("")
                    # Full width save button
                    if st.form_submit_button("💾 Save Event to Cloud", use_container_width=True):
                        res = logic.add_event(name, date, time_val, loc, desc)
                        if "Error" in res:
                            st.error(res)
                        else:
                            st.success("Event Created Successfully!")
                            time.sleep(1)
                            st.session_state['show_create'] = False
                            st.rerun()

        # EVENT LIST
        events_df = logic.get_events()
        if not events_df.empty:
            events_df['date'] = pd.to_datetime(events_df['date'])
            events_df = events_df.sort_values(by='date')
            for idx, (_, event) in enumerate(events_df.iterrows()):
                render_event_card(event, idx)
        else:
            st.info("No events found in database.")

    else:
        # DETAIL VIEW
        events_df = logic.get_events()
        event = events_df[events_df['id'] == st.session_state['view_event_id']].iloc[0]
        page_header("Event Details", event['name'])
        
        if st.button("← Back to Dashboard"):
            st.session_state['view_event_id'] = None
            st.rerun()
            
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**📅 Date:** {event['date']}")
            c2.markdown(f"**⏰ Time:** {event['time']}")
            c3.markdown(f"**📍 Location:** {event['location']}")
            st.divider()
            st.markdown(f"**Description:** {event['description']}")

# --- PAGE 2: ATTENDEES (Custom UI) ---
elif menu == "Attendees":
    page_header("Attendees", "Guest List Management")
    
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        # Display Custom List
        attendees_df = logic.get_attendees(selected_id)
        
        with st.container(border=True):
            if not attendees_df.empty:
                st.markdown(f"### Guest List ({len(attendees_df)})")
                # Loop through and render custom rows
                for _, att in attendees_df.iterrows():
                    render_attendee_row(att)
            else:
                st.info("No guests registered yet.")

        # Add Guest Section
        st.write("")
        with st.expander("➕ Add New Guest", expanded=True):
            with st.form("add_guest_form"):
                c1, c2 = st.columns(2)
                name = c1.text_input("Guest Name")
                email = c2.text_input("Email Address")
                c3, c4 = st.columns(2)
                role = c3.selectbox("Role", ["Guest", "VIP", "Speaker", "Staff"])
                rsvp = c4.selectbox("RSVP Status", ["Confirmed", "Pending", "Declined"])
                
                if st.form_submit_button("Add Guest", use_container_width=True):
                    res = logic.add_attendee(selected_id, name, email, rsvp, role, "")
                    if "Error" in res:
                        st.error(res)
                    else:
                        st.success("Guest Added!")
                        time.sleep(0.5)
                        st.rerun()

# --- PAGE 3: TASKS ---
elif menu == "Task Manager":
    page_header("Tasks", "Project Tracker")
    
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        # Task List
        tasks_df = logic.get_tasks(selected_id)
        if not tasks_df.empty:
            st.dataframe(
                tasks_df[['task_name', 'status', 'priority', 'deadline']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No tasks yet.")

        # Add Task Form
        st.write("")
        with st.container(border=True):
            st.subheader("Create New Task")
            with st.form("add_task_form"):
                tname = st.text_input("Task Name")
                c1, c2, c3 = st.columns(3)
                tstat = c1.selectbox("Status", ["Not Started", "In Progress", "Completed"])
                tprio = c2.selectbox("Priority", ["Low", "Medium", "High"])
                tdue = c3.date_input("Deadline")
                
                if st.form_submit_button("Add Task", use_container_width=True):
                    logic.add_task(selected_id, tname, tstat, tdue, tprio)
                    st.success("Task Added!")
                    time.sleep(0.5)
                    st.rerun()

# --- PAGE 4: ANALYTICS ---
elif menu == "Analytics":
    page_header("Analytics", "Insights")
    events_df = logic.get_events()
    if not events_df.empty:
        event_names = dict(zip(events_df['id'], events_df['name']))
        selected_id = st.selectbox("Select Event", event_names.keys(), format_func=lambda x: event_names[x])
        
        c1, c2 = st.columns(2)
        with c1: 
            st.caption("RSVP Distribution")
            st.pyplot(logic.get_rsvp_pie_chart(selected_id))
        with c2: 
            st.caption("Task Status")
            st.pyplot(logic.get_task_status_chart(selected_id))
    else: 
        st.warning("No data.")
