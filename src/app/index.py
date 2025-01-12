# Tkinter
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# Utils
import threading
from decouple import config
from datetime import datetime

# Assistant
from ..assistant.index import Assistant

# Database
import mysql.connector


class App(ctk.CTk):

    def __init__(self):

        super().__init__()


        # Title and Icon
        self.title("JustDoIT To-Do App")
        self.iconbitmap("src/app/images/todo-icon-7.ico")

  
        # Theme
        ctk.set_appearance_mode("light")

 
        # Window Size and Position
        width, height = 1000, 600
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        middle_x = int((self.screen_width / 2) - (width / 2))
        middle_y = int((self.screen_height / 2) - (height / 2))

        self.geometry(f"{width}x{height}+{middle_x}+{middle_y}")
        self.resizable(False, False)


        # Connect to Database
        self.db = self.connect_to_database()


        # Voice Assistant
        self.assistant = Assistant(self.db, self)


        # Start the assistant in a separate thread
        self.assistant_thread = threading.Thread(target=self.assistant.run, daemon=True)
        self.assistant_thread.start()


        # Initialize UI Elements
        self.create_widgets()

 
    # Connect to Database
    def connect_to_database(self):
        
        try:
            db = mysql.connector.connect(
                host=config("DB_HOST"),
                user=config("DB_USER"),
                password=config("DB_PASSWORD"),
                database=config("DB_NAME")
            )
            return db
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.show_message(f"Database Connection Error: {err}")
            return None

 
    # Widgets
    def create_widgets(self):

        # Main Content Frame
        content_frame = ctk.CTkFrame(self, corner_radius=10)
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Task Input
        self.task_entry = ctk.CTkEntry(content_frame, placeholder_text="Enter a new task...")
        self.task_entry.pack(pady=10, padx=10, fill=tk.X)

        # Deadline Input
        self.deadline_entry = ctk.CTkEntry(content_frame, placeholder_text="Enter deadline (YYYY-MM-DD)...")
        self.deadline_entry.pack(pady=10, padx=10, fill=tk.X)

        button_frame = ctk.CTkFrame(content_frame, corner_radius=10)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        add_task_button = ctk.CTkButton(
            button_frame, text="Add Task", command=self.add_task_to_database
        )
        add_task_button.pack(pady=5, padx=10, side=tk.LEFT)

        self.delete_task_button = ctk.CTkButton(
            button_frame, text="Delete Task", fg_color="red", hover="red", cursor="hand2", state="disabled", command=self.delete_task_from_database
        )
        self.delete_task_button.pack(pady=5, padx=10, side=tk.RIGHT)

        # Task List (Treeview)
        self.task_treeview = ttk.Treeview(content_frame, columns=("№", "Task", "Deadline"), show="headings")
        self.task_treeview.heading("№", text="№")
        self.task_treeview.heading("Task", text="Task")
        self.task_treeview.heading("Deadline", text="Deadline")

        self.task_treeview.column("№", width=2)
        self.task_treeview.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Configure style for bold text
        self.task_treeview.tag_configure("bold", font=("Arial", 12, "bold"))
    
        # Load Tasks from Database
        self.load_tasks_from_database()

        self.task_treeview.bind("<<TreeviewSelect>>", self.enable_delete_button)

 
    # Enable Delete Button
    def enable_delete_button(self, event):

        selected_item = self.task_treeview.selection()

        if selected_item:
            self.delete_task_button.configure(state="normal")
        else:
            self.delete_task_button.configure(state="disabled")


    # Add task
    def add_task_to_database(self):
        task = self.task_entry.get().strip()
        deadline = self.deadline_entry.get().strip()

        # Validate inputs
        if not task or not deadline:
            self.show_message("Please enter both task and deadline.")
            return

        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()

        except ValueError:
            self.show_message("Invalid date format. Use YYYY-MM-DD.")
            return

        try:
            cursor = self.db.cursor()
            query = "INSERT INTO tasks (task, deadline) VALUES (%s, %s)"
            cursor.execute(query, (task, deadline_date))
            self.db.commit()
            cursor.close()

            self.task_treeview.insert("", tk.END, values=(task, deadline))

            # Clear input fields
            self.task_entry.delete(0, tk.END)
            self.deadline_entry.delete(0, tk.END)

            self.load_tasks_from_database()

            self.show_message("Task added successfully.")

        except mysql.connector.Error as err:
            self.show_message(f"Database Error: {err}")


    # Get all tasks
    def load_tasks_from_database(self):
        
        if not self.db:
            return

        try:
            cursor = self.db.cursor()
            query = "SELECT task, deadline FROM tasks ORDER BY deadline ASC"
            cursor.execute(query)
            tasks = cursor.fetchall()
            cursor.close()

            for item in self.task_treeview.get_children():
                self.task_treeview.delete(item)

            for index, (task, deadline) in enumerate(tasks, start=1):
                self.task_treeview.insert("", tk.END, values=(index, task, deadline), tags=("bold",))

        except mysql.connector.Error as err:
            self.show_message(f"Error Loading Tasks: {err}")


    # Delete Task
    def delete_task_from_database(self):

        selected_item = self.task_treeview.selection()[0]
        task = self.task_treeview.item(selected_item)["values"][1]

        try:
            cursor = self.db.cursor()
            query = "DELETE FROM tasks WHERE task = %s"
            cursor.execute(query, (task,))
            self.db.commit()
            cursor.close()

            self.task_treeview.delete(selected_item)

            self.show_message("Task deleted successfully.")

            self.load_tasks_from_database()

        except mysql.connector.Error as err:
            self.show_message(f"Database Error: {err}")


    # Show messages in a popup
    def show_message(self, message):
        
        popup = tk.Toplevel(self)
        popup.title("Message")

        width, height = 400, 150
        popup.geometry(f"{width}x{height}+{self.screen_width//2 - width//2}+{self.screen_height//2 - height//2}")

        msg_label = ctk.CTkLabel(popup, text=message, font=("Arial", 12))
        msg_label.pack(pady=20)

        ok_button = ctk.CTkButton(popup, text="OK", command=popup.destroy)
        ok_button.pack()


