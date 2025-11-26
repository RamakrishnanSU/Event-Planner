import pandas as pd
import matplotlib.pyplot as plt
from data_handler import DataHandler

class EventLogic:
    def __init__(self):
        self.handler = DataHandler()
        # Worksheet Names
        self.sheet_events = "events"
        self.sheet_tasks = "tasks"
        self.sheet_attendees = "attendees"

    # ================= EVENTS =================
    def get_events(self):
        df = self.handler.load_data(self.sheet_events)
        required_cols = ['id', 'name', 'date', 'time', 'location', 'description']
        
        if df.empty:
            return pd.DataFrame(columns=required_cols)
        
        # Ensure all columns exist
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        
        # Clean ID
        if 'id' in df.columns:
             df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
             
        return df

    def add_event(self, name, date, time, location, description):
        events_df = self.get_events()
        events = events_df.to_dict('records')
        
        new_id = 1 if not events else max([int(e['id']) for e in events]) + 1
        
        new_event = {
            "id": new_id,
            "name": name,
            "date": str(date),
            "time": str(time),
            "location": location,
            "description": description
        }
        events.append(new_event)
        return self.handler.save_data(events, self.sheet_events)

    # --- DELETE EVENT ---
    def delete_event(self, event_id):
        # 1. Delete the event itself
        res = self.handler.delete_data(self.sheet_events, "id", event_id)
        # 2. Delete associated data
        self.handler.delete_data(self.sheet_attendees, "event_id", event_id)
        self.handler.delete_data(self.sheet_tasks, "event_id", event_id)
        return res

    # ================= ATTENDEES =================
    def get_attendees(self, event_id=None):
        df = self.handler.load_data(self.sheet_attendees)
        cols = ['event_id', 'name', 'email', 'rsvp', 'role', 'dietary']
        if df.empty: return pd.DataFrame(columns=cols)
        
        # Clean ID
        if 'event_id' in df.columns:
             df['event_id'] = pd.to_numeric(df['event_id'], errors='coerce').fillna(0).astype(int)
        
        if event_id:
            return df[df['event_id'] == int(event_id)]
        return df

    def add_attendee(self, event_id, name, email, rsvp, role, dietary):
        df = self.handler.load_data(self.sheet_attendees)
        attendees = df.to_dict('records') if not df.empty else []
        
        new_att = {
            "event_id": int(event_id),
            "name": name,
            "email": email,
            "rsvp": rsvp,
            "role": role,
            "dietary": dietary
        }
        attendees.append(new_att)
        return self.handler.save_data(attendees, self.sheet_attendees)

    # ================= TASKS =================
    def get_tasks(self, event_id=None):
        df = self.handler.load_data(self.sheet_tasks)
        cols = ['event_id', 'task_name', 'status', 'deadline', 'priority']
        if df.empty: return pd.DataFrame(columns=cols)
        
        if 'event_id' in df.columns:
             df['event_id'] = pd.to_numeric(df['event_id'], errors='coerce').fillna(0).astype(int)

        if event_id:
            return df[df['event_id'] == int(event_id)]
        return df

    def add_task(self, event_id, task_name, status, deadline, priority="Medium"):
        df = self.handler.load_data(self.sheet_tasks)
        tasks = df.to_dict('records') if not df.empty else []
        
        new_task = {
            "event_id": int(event_id),
            "task_name": task_name,
            "status": status,
            "deadline": str(deadline),
            "priority": priority
        }
        tasks.append(new_task)
        return self.handler.save_data(tasks, self.sheet_tasks)

    def update_task_status(self, event_id, task_name, new_status):
        df = self.handler.load_data(self.sheet_tasks)
        if df.empty: return "No tasks found."
        
        if 'event_id' in df.columns:
            df['event_id'] = pd.to_numeric(df['event_id'], errors='coerce').fillna(0).astype(int)
        
        updated = False
        for index, row in df.iterrows():
            if row['event_id'] == int(event_id) and row['task_name'] == task_name:
                df.at[index, 'status'] = new_status
                updated = True
        
        if updated:
            return self.handler.save_data(df, self.sheet_tasks)
        return "Task not found."

    # ================= ANALYTICS (DONUT & STYLED BAR) =================
    def get_rsvp_pie_chart(self, event_id):
        attendees = self.get_attendees(event_id)
        if attendees.empty: return None
        
        rsvp_counts = attendees['rsvp'].value_counts()
        
        # Transparent Background
        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Custom Colors (Green, Orange, Red)
        colors = ['#00C853', '#FFAB00', '#D50000']
        
        # DONUT CHART LOGIC
        wedges, texts, autotexts = ax.pie(
            rsvp_counts, 
            labels=rsvp_counts.index, 
            autopct='%1.1f%%', 
            colors=colors[:len(rsvp_counts)],
            wedgeprops=dict(width=0.4, edgecolor='none'), # width=0.4 makes it a ring
            textprops={'color': "white", 'fontsize': 10}
        )
        
        # Style the percentage text
        plt.setp(autotexts, size=10, weight="bold", color="white")
        plt.setp(texts, color="white")
        
        return fig

    def get_task_status_chart(self, event_id):
        tasks = self.get_tasks(event_id)
        if tasks.empty: return None

        status_counts = tasks['status'].value_counts()
        
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Bar Chart
        bars = ax.bar(status_counts.index, status_counts.values, color='#6C63FF', width=0.5)
        
        # Minimal Styling (Remove borders)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.tick_params(colors='white')
        
        # Add numbers on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', color='white')
        
        return fig

