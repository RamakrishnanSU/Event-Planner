import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import os


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
    def __init__(self, task_file="tasks.csv"):
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
            "Not Started": "\033[91mNot Started\033[0m",
            "In Progress": "\033[93mIn Progress\033[0m",
            "Completed": "\033[92mCompleted\033[0m",
            "Delayed": "\033[95mDelayed\033[0m"
        }
        return status_formats.get(status, status)


class EventAnalyzer:
    def __init__(self, event_file="events.csv", attendee_file="attendees.csv", task_file="tasks.csv"):
        self.data_handler = DataHandler()
        self.event_file = event_file
        self.attendee_file = attendee_file
        self.task_file = task_file

    def load_data(self):
        events_df = self.data_handler.load_from_csv(self.event_file)
        attendees_df = self.data_handler.load_from_csv(self.attendee_file)

        if os.path.exists(self.task_file):
            tasks_df = self.data_handler.load_from_csv(self.task_file)
        else:
            tasks_df = pd.DataFrame(columns=['event_id', 'task_name', 'status', 'deadline'])

        return events_df, attendees_df, tasks_df

    def visualize_rsvp_status(self, event_id=None):
        _, attendees_df, _ = self.load_data()

        if isinstance(attendees_df, str):
            return "No attendee data available for visualization."

        if event_id:
            attendees_df = attendees_df[attendees_df['event_id'] == event_id]
            if attendees_df.empty:
                return f"No attendees found for event ID {event_id}."

        rsvp_counts = attendees_df['rsvp'].value_counts()

        fig, ax = plt.subplots(figsize=(8, 6))
        rsvp_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('RSVP Status Distribution')
        ax.set_ylabel('')

        self._show_plot(fig)
        return "RSVP status visualization displayed."

    def visualize_attendee_categories(self, event_id, category='role'):
        _, attendees_df, _ = self.load_data()

        if isinstance(attendees_df, str):
            return "No attendee data available for visualization."

        attendees_df = attendees_df[attendees_df['event_id'] == event_id]
        if attendees_df.empty:
            return f"No attendees found for event ID {event_id}."

        if category not in attendees_df.columns:
            return f"Category '{category}' not found in attendee data."

        category_counts = attendees_df[category].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        category_counts.plot(kind='bar', ax=ax)
        ax.set_title(f'Attendees by {category.title()}')
        ax.set_xlabel(category.title())
        ax.set_ylabel('Number of Attendees')

        self._show_plot(fig)
        return f"Attendee {category} visualization displayed."

    def visualize_task_status(self, event_id):
        _, _, tasks_df = self.load_data()

        if isinstance(tasks_df, str) or tasks_df.empty:
            return "No task data available for visualization."

        tasks_df = tasks_df[tasks_df['event_id'] == event_id]
        if tasks_df.empty:
            return f"No tasks found for event ID {event_id}."

        status_counts = tasks_df['status'].value_counts()

        fig, ax = plt.subplots(figsize=(8, 6))
        status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_title('Task Status Distribution')
        ax.set_ylabel('')

        self._show_plot(fig)
        return "Task status visualization displayed."

    def analyze_event_timeline(self, event_id):
        events_df, _, tasks_df = self.load_data()

        if isinstance(events_df, str) or isinstance(tasks_df, str):
            return "Required data not available for analysis."

        event = events_df[events_df['id'] == event_id]
        if event.empty:
            return f"Event ID {event_id} not found."

        tasks = tasks_df[tasks_df['event_id'] == event_id]
        if tasks.empty:
            return f"No tasks found for event ID {event_id}."

        tasks['deadline'] = pd.to_datetime(tasks['deadline'])
        event_date = pd.to_datetime(event['date'].values[0])

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axvline(x=event_date, color='r', linestyle='--', label='Event Date')

        for i, task in tasks.iterrows():
            status_color = 'green' if task['status'] == 'Completed' else 'orange' if task['status'] == 'In Progress' else 'red'
            ax.scatter(task['deadline'], i, color=status_color, s=100)
            ax.text(task['deadline'], i, f"  {task['task_name']}", va='center')

        ax.set_title('Event Timeline and Task Deadlines')
        ax.set_xlabel('Date')
        ax.set_yticks([])
        fig.autofmt_xdate()

        self._show_plot(fig)
        return "Event timeline analysis displayed."

    def generate_event_report(self, event_id):
        events_df, attendees_df, tasks_df = self.load_data()

        if isinstance(events_df, str) or isinstance(attendees_df, str) or isinstance(tasks_df, str):
            return "Required data not available for report generation."

        event = events_df[events_df['id'] == event_id]
        if event.empty:
            return f"Event ID {event_id} not found."

        attendees = attendees_df[attendees_df['event_id'] == event_id]
        tasks = tasks_df[tasks_df['event_id'] == event_id]

        report = f"Event Report: {event['name'].values[0]}\n"
        report += f"Date: {event['date'].values[0]} Time: {event['time'].values[0]}\n"
        report += f"Location: {event['location'].values[0]}\n\n"

        total_attendees = len(attendees)
        report += f"Total Attendees: {total_attendees}\n"

        if not attendees.empty:
            rsvp_counts = attendees['rsvp'].value_counts()
            for status, count in rsvp_counts.items():
                report += f"- {status}: {count} ({count / total_attendees * 100:.1f}%)\n"

        report += f"\nTask Status:\n"
        if not tasks.empty:
            task_status = tasks['status'].value_counts()
            total_tasks = len(tasks)
            for status, count in task_status.items():
                report += f"- {status}: {count} ({count / total_tasks * 100:.1f}%)\n"

            report += "\nAreas for Improvement:\n"
            if 'Not Started' in task_status or 'Delayed' in task_status:
                report += "- Some tasks are not started or delayed. Consider better task prioritization.\n"

            if not tasks.empty and 'deadline' in tasks.columns:
                tasks['deadline'] = pd.to_datetime(tasks['deadline'])
                event_date = pd.to_datetime(event['date'].values[0])
                late_tasks = tasks[tasks['deadline'] >= event_date]
                if not late_tasks.empty:
                    report += f"- {len(late_tasks)} tasks are scheduled too close to the event date. Consider earlier planning.\n"
        else:
            report += "- No tasks tracked for this event. Consider adding task tracking for better planning.\n"

        self._show_text_report(report, f"Event Report - {event['name'].values[0]}")
        return "Event report generated."

    def _show_plot(self, fig):
        root = tk.Tk()
        root.title("Event Analysis Visualization")
        root.geometry("800x600")

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        close_button = ttk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=10)

        root.mainloop()

    def _show_text_report(self, report_text, title):
        root = tk.Tk()
        root.title(title)
        root.geometry("700x500")

        text_widget = tk.Text(root, wrap="word", padx=10, pady=10)
        text_widget.insert(tk.END, report_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        close_button = ttk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=10)

        root.mainloop()
