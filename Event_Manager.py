import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import os



# Set the working directory explicitly
WORKING_DIR = r"C:\Users\ramak\Desktop\event_planner"

# Ensure the directory exists (optional if you're certain it does)
os.makedirs(WORKING_DIR, exist_ok=True)

class DataHandler:
    def save_to_csv(self, data, filename):
        '''Append or overwrite records in CSV'''
        try:
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            df.to_csv(filename, mode='w', index=False)
            return f'Data saved to {filename}.'
        except Exception as e:
            return f'Error saving data: {e}'

    def load_from_csv(self, filename):
        '''Return pandas DataFrame'''
        try:
            df = pd.read_csv(filename)
            return df if not df.empty else "No data found."
        except Exception as e:
            return f'Error loading data: {e}'


class TaskManager:
    def __init__(self, task_file=os.path.join(WORKING_DIR, "tasks.csv")):

        self.data_handler = DataHandler()
        self.task_file = task_file
        self.tasks = self.load_tasks()

    def load_tasks(self):
        '''Load existing tasks from CSV'''
        df = self.data_handler.load_from_csv(self.task_file)
        return df.to_dict('records') if isinstance(df, pd.DataFrame) else []

    def create_task(self, event_id):
        '''Create a new task for an event'''
        task_name = input("Enter Task Name: ")
        status = input("Enter Status (Not Started/In Progress/Completed/Delayed): ")
        deadline = input("Enter Deadline (YYYY-MM-DD): ")

        task = {
            "event_id": event_id,
            "task_name": task_name,
            "status": status,
            "deadline": deadline
        }

        # Optional additional fields
        assign_to = input("Assign to (optional): ")
        if assign_to:
            task["assigned_to"] = assign_to

        priority = input("Priority (High/Medium/Low) (optional): ")
        if priority:
            task["priority"] = priority

        self.tasks.append(task)
        self.data_handler.save_to_csv(self.tasks, self.task_file)
        print(f'Task "{task_name}" created for Event ID {event_id}.')

    def update_task_status(self):
        '''Update the status of a task'''
        event_id = int(input("Enter Event ID: "))
        self.display_tasks(event_id)

        task_name = input("Enter Task Name to update: ")
        new_status = input("Enter New Status (Not Started/In Progress/Completed/Delayed): ")

        found = False
        for task in self.tasks:
            if task["event_id"] == event_id and task["task_name"] == task_name:
                task["status"] = new_status
                self.data_handler.save_to_csv(self.tasks, self.task_file)
                print(f'Task "{task_name}" updated: {new_status}')
                found = True
                break

        if not found:
            print("Task not found.")

    def display_tasks(self, event_id):
        '''Display all tasks for an event'''
        event_tasks = [t for t in self.tasks if t["event_id"] == event_id]

        if event_tasks:
            print(f"\nTasks for Event ID {event_id}:")
            for i, task in enumerate(event_tasks, 1):
                status_display = self._get_status_display(task["status"])
                print(f'{i}. {task["task_name"]} - {status_display} (Due: {task["deadline"]})')
        else:
            print(f"No tasks found for Event ID {event_id}.")

    def _get_status_display(self, status):
        '''Format status display'''
        status_formats = {
            "Not Started": "\033[91mNot Started\033[0m",  # Red
            "In Progress": "\033[93mIn Progress\033[0m",  # Yellow
            "Completed": "\033[92mCompleted\033[0m",  # Green
            "Delayed": "\033[95mDelayed\033[0m"  # Purple
        }
        return status_formats.get(status, status)


class EventAnalyzer:
    def __init__(self,
                 event_file=os.path.join(WORKING_DIR, "events.csv"),
                 attendee_file=os.path.join(WORKING_DIR, "attendees.csv"),
                 task_file=os.path.join(WORKING_DIR, "tasks.csv")):

        self.data_handler = DataHandler()
        self.event_file = event_file
        self.attendee_file = attendee_file
        self.task_file = task_file

    def load_data(self):
        """Load all necessary data for analysis"""
        events_df = self.data_handler.load_from_csv(self.event_file)
        attendees_df = self.data_handler.load_from_csv(self.attendee_file)

        # Check if task file exists and load it
        if os.path.exists(self.task_file):
            tasks_df = self.data_handler.load_from_csv(self.task_file)
        else:
            tasks_df = pd.DataFrame(columns=['event_id', 'task_name', 'status', 'deadline'])

        return events_df, attendees_df, tasks_df

    def visualize_rsvp_status(self, event_id=None):
        """Visualize RSVP status distribution for one or all events"""
        _, attendees_df, _ = self.load_data()

        if isinstance(attendees_df, str):  # Error message or no data
            return "No attendee data available for visualization."

        # Filter by event_id if specified
        if event_id:
            attendees_df = attendees_df[attendees_df['event_id'] == event_id]
            if attendees_df.empty:
                return f"No attendees found for event ID {event_id}."

        # Count RSVP statuses
        rsvp_counts = attendees_df['rsvp'].value_counts()

        # Create figure and plot
        fig, ax = plt.subplots(figsize=(8, 6))
        rsvp_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('RSVP Status Distribution')
        ax.set_ylabel('')  # Hide 'None' ylabel

        self._show_plot(fig)
        return "RSVP status visualization displayed."

    def visualize_attendee_categories(self, event_id, category='role'):
        """Visualize attendee distribution by category (role, dietary preference, etc.)"""
        _, attendees_df, _ = self.load_data()

        if isinstance(attendees_df, str):  # Error message or no data
            return "No attendee data available for visualization."

        # Filter by event_id
        attendees_df = attendees_df[attendees_df['event_id'] == event_id]
        if attendees_df.empty:
            return f"No attendees found for event ID {event_id}."

        # Check if category column exists
        if category not in attendees_df.columns:
            return f"Category '{category}' not found in attendee data."

        # Count categories
        category_counts = attendees_df[category].value_counts()

        # Create figure and plot
        fig, ax = plt.subplots(figsize=(10, 6))
        category_counts.plot(kind='bar', ax=ax)
        ax.set_title(f'Attendees by {category.title()}')
        ax.set_xlabel(category.title())
        ax.set_ylabel('Number of Attendees')

        self._show_plot(fig)
        return f"Attendee {category} visualization displayed."

    def visualize_task_status(self, event_id):
        """Visualize task completion status for an event"""
        _, _, tasks_df = self.load_data()

        if isinstance(tasks_df, str) or tasks_df.empty:  # Error message or no data
            return "No task data available for visualization."

        # Filter by event_id
        tasks_df = tasks_df[tasks_df['event_id'] == event_id]
        if tasks_df.empty:
            return f"No tasks found for event ID {event_id}."

        # Count task statuses
        status_counts = tasks_df['status'].value_counts()

        # Create figure and plot
        fig, ax = plt.subplots(figsize=(8, 6))
        status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('Task Status Distribution')
        ax.set_ylabel('')  # Hide 'None' ylabel

        self._show_plot(fig)
        return "Task status visualization displayed."

    def analyze_event_timeline(self, event_id):
        """Analyze event timeline and task deadlines"""
        events_df, _, tasks_df = self.load_data()

        if isinstance(events_df, str) or isinstance(tasks_df, str):
            return "Required data not available for analysis."

        # Filter by event_id
        event = events_df[events_df['id'] == event_id]
        if event.empty:
            return f"Event ID {event_id} not found."

        tasks = tasks_df[tasks_df['event_id'] == event_id]
        if tasks.empty:
            return f"No tasks found for event ID {event_id}."

        # Convert deadlines to datetime
        tasks['deadline'] = pd.to_datetime(tasks['deadline'])
        event_date = pd.to_datetime(event['date'].values[0])

        # Create figure and plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot event date as a vertical line
        ax.axvline(x=event_date, color='r', linestyle='--', label='Event Date')

        # Plot tasks as points
        for i, task in tasks.iterrows():
            status_color = 'green' if task['status'] == 'Completed' else 'orange' if task[
                                                                                         'status'] == 'In Progress' else 'red'
            ax.scatter(task['deadline'], i, color=status_color, s=100)
            ax.text(task['deadline'], i, f"  {task['task_name']}", va='center')

        ax.set_title('Event Timeline and Task Deadlines')
        ax.set_xlabel('Date')
        ax.set_yticks([])  # Hide y-ticks

        # Format x-axis as dates
        fig.autofmt_xdate()

        self._show_plot(fig)
        return "Event timeline analysis displayed."

    def generate_event_report(self, event_id):
        """Generate a comprehensive report for an event"""
        events_df, attendees_df, tasks_df = self.load_data()

        if isinstance(events_df, str) or isinstance(attendees_df, str) or isinstance(tasks_df, str):
            return "Required data not available for report generation."

        # Filter by event_id
        event = events_df[events_df['id'] == event_id]
        if event.empty:
            return f"Event ID {event_id} not found."

        attendees = attendees_df[attendees_df['event_id'] == event_id]
        tasks = tasks_df[tasks_df['event_id'] == event_id]

        # Generate report text
        report = f"Event Report: {event['name'].values[0]}\n"
        report += f"Date: {event['date'].values[0]} Time: {event['time'].values[0]}\n"
        report += f"Location: {event['location'].values[0]}\n\n"

        # Attendee stats
        total_attendees = len(attendees)
        report += f"Total Attendees: {total_attendees}\n"

        if not attendees.empty:
            rsvp_counts = attendees['rsvp'].value_counts()
            for status, count in rsvp_counts.items():
                report += f"- {status}: {count} ({count / total_attendees * 100:.1f}%)\n"

        # Task stats
        report += f"\nTask Status:\n"
        if not tasks.empty:
            task_status = tasks['status'].value_counts()
            total_tasks = len(tasks)
            for status, count in task_status.items():
                report += f"- {status}: {count} ({count / total_tasks * 100:.1f}%)\n"

            # Areas for improvement
            report += "\nAreas for Improvement:\n"
            if 'Not Started' in task_status or 'Delayed' in task_status:
                report += "- Some tasks are not started or delayed. Consider better task prioritization.\n"

            # Check if any tasks are close to or past the event date
            if not tasks.empty and 'deadline' in tasks.columns:
                tasks['deadline'] = pd.to_datetime(tasks['deadline'])
                event_date = pd.to_datetime(event['date'].values[0])
                late_tasks = tasks[tasks['deadline'] >= event_date]
                if not late_tasks.empty:
                    report += f"- {len(late_tasks)} tasks are scheduled too close to the event date. Consider earlier planning.\n"
        else:
            report += "- No tasks tracked for this event. Consider adding task tracking for better planning.\n"

        # Display the report
        self._show_text_report(report, f"Event Report - {event['name'].values[0]}")

        return "Event report generated."

    def _show_plot(self, fig):
        """Display a matplotlib figure in a Tkinter window"""
        root = tk.Tk()
        root.title("Event Analysis Visualization")
        root.geometry("800x600")

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add close button
        close_button = ttk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=10)

        #root.mainloop()

    def _show_text_report(self, report_text, title):
        """Display a text report in a Tkinter window"""
        root = tk.Tk()
        root.title(title)
        root.geometry("700x500")

        # Create text widget
        text_widget = tk.Text(root, wrap="word", padx=10, pady=10)
        text_widget.insert(tk.END, report_text)
        text_widget.config(state="disabled")  # Make it read-only
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Add close button
        close_button = ttk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=10)

        #root.mainloop()


class EventManager:
    def __init__(self,
                 event_file=os.path.join(WORKING_DIR, "events.csv"),
                 attendee_file=os.path.join(WORKING_DIR, "attendees.csv")):

        self.data_handler = DataHandler()
        self.event_file = event_file
        self.attendee_file = attendee_file
        self.events = self.load_events()
        self.attendees = self.load_attendees()
        self.task_manager = TaskManager()
        self.event_analyzer = EventAnalyzer()

    def load_events(self):
        '''Load existing events from CSV'''
        df = self.data_handler.load_from_csv(self.event_file)
        return df.to_dict('records') if isinstance(df, pd.DataFrame) else []

    def load_attendees(self):
        '''Load existing attendees from CSV'''
        df = self.data_handler.load_from_csv(self.attendee_file)
        return df.to_dict('records') if isinstance(df, pd.DataFrame) else []

    def create_event(self):
        '''Get event details from user and create event'''
        name = input("Enter Event Name: ")
        date = input("Enter Event Date (YYYY-MM-DD): ")
        time = input("Enter Event Time (HH:MM AM/PM): ")
        location = input("Enter Event Location: ")
        description = input("Enter Event Description: ")

        event_id = len(self.events) + 1
        event = {
            "id": event_id,
            "name": name,
            "date": date,
            "time": time,
            "location": location,
            "description": description
        }
        self.events.append(event)
        self.data_handler.save_to_csv(self.events, self.event_file)
        print(f'Event "{name}" created successfully!')

    def add_attendee(self):
        '''Get attendee details from user and add to event'''
        event_id = int(input("Enter Event ID: "))
        name = input("Enter Attendee Name: ")
        email = input("Enter Attendee Email: ")
        rsvp = input("Enter RSVP Status (Pending/Confirmed/Declined): ")

        # Additional attendee information for analysis
        role = input("Enter Professional Role (optional): ")
        dietary = input("Enter Dietary Preferences (optional): ")

        attendee = {
            "event_id": event_id,
            "name": name,
            "email": email,
            "rsvp": rsvp
        }

        # Add optional fields if provided
        if role:
            attendee["role"] = role
        if dietary:
            attendee["dietary"] = dietary

        self.attendees.append(attendee)
        self.data_handler.save_to_csv(self.attendees, self.attendee_file)
        print(f'Attendee "{name}" added to Event {event_id}.')

    def update_rsvp(self):
        '''Update RSVP status for an attendee'''
        email = input("Enter Attendee Email: ")
        new_rsvp = input("Enter New RSVP Status (Pending/Confirmed/Declined): ")

        found = False
        for attendee in self.attendees:
            if attendee["email"] == email:
                attendee["rsvp"] = new_rsvp
                self.data_handler.save_to_csv(self.attendees, self.attendee_file)
                print(f'RSVP updated for {email}: {new_rsvp}')
                found = True
                break
        if not found:
            print("Attendee not found.")

    def display_events(self):
        '''Display all events'''
        if not self.events:
            print("No events found.")
            return

        print("\nAll Events:")
        for event in self.events:
            print(
                f'ID: {event["id"]}, Name: {event["name"]}, Date: {event["date"]}, Time: {event["time"]}, Location: {event["location"]}')

    def display_attendees(self):
        '''List attendees for an event'''
        event_id = int(input("Enter Event ID: "))
        attendees = [a for a in self.attendees if a["event_id"] == event_id]
        if attendees:
            for att in attendees:
                print(f'Name: {att["name"]}, Email: {att["email"]}, RSVP: {att["rsvp"]}')
                # Display additional fields if they exist
                if "role" in att:
                    print(f'  Role: {att["role"]}')
                if "dietary" in att:
                    print(f'  Dietary: {att["dietary"]}')
        else:
            print("No attendees found for this event.")

    # ======= Task Management Functions =======
    def manage_tasks(self):
        '''Task management menu'''
        while True:
            print("\nTask Management")
            print("1. Create New Task")
            print("2. Update Task Status")
            print("3. Display Tasks")
            print("4. Return to Main Menu")

            choice = input("Choose an option: ")

            if choice == "1":
                event_id = int(input("Enter Event ID: "))
                self.task_manager.create_task(event_id)
            elif choice == "2":
                self.task_manager.update_task_status()
            elif choice == "3":
                event_id = int(input("Enter Event ID: "))
                self.task_manager.display_tasks(event_id)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")

    # ======= Data Visualization and Analysis Functions =======
    def visualize_data(self):
        '''Data visualization menu'''
        while True:
            print("\nData Visualization and Analysis")
            print("1. RSVP Status Distribution")
            print("2. Attendee Category Analysis")
            print("3. Task Status Visualization")
            print("4. Event Timeline Analysis")
            print("5. Generate Event Report")
            print("6. Return to Main Menu")

            choice = input("Choose an option: ")

            if choice == "1":
                event_id = input("Enter Event ID (or leave blank for all events): ")
                if event_id:
                    result = self.event_analyzer.visualize_rsvp_status(int(event_id))
                else:
                    result = self.event_analyzer.visualize_rsvp_status()
                print(result)
            elif choice == "2":
                event_id = int(input("Enter Event ID: "))
                category = input("Enter Category (role/dietary): ")
                result = self.event_analyzer.visualize_attendee_categories(event_id, category)
                print(result)
            elif choice == "3":
                event_id = int(input("Enter Event ID: "))
                result = self.event_analyzer.visualize_task_status(event_id)
                print(result)
            elif choice == "4":
                event_id = int(input("Enter Event ID: "))
                result = self.event_analyzer.analyze_event_timeline(event_id)
                print(result)
            elif choice == "5":
                event_id = int(input("Enter Event ID: "))
                result = self.event_analyzer.generate_event_report(event_id)
                print(result)
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")


# Main Application
def main():
    """Main function to run the Event Planner application"""
    print("Welcome to Event Planner!")
    print("-------------------------")

    manager = EventManager()

    while True:
        print("\nEvent Planner - Main Menu")
        print("1. Create Event")
        print("2. Add Attendee")
        print("3. Update RSVP")
        print("4. Display Events")
        print("5. Display Attendees")
        print("6. Task Management")
        print("7. Data Visualization & Analysis")
        print("8. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            manager.create_event()
        elif choice == "2":
            manager.add_attendee()
        elif choice == "3":
            manager.update_rsvp()
        elif choice == "4":
            manager.display_events()
        elif choice == "5":
            manager.display_attendees()
        elif choice == "6":
            manager.manage_tasks()
        elif choice == "7":
            manager.visualize_data()
        elif choice == "8":
            print("Thank you for using Event Planner! Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()