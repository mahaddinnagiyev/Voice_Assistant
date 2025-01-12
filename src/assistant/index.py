import os
import time
import pytz
from datetime import datetime, date

# Assistant Speaker
import speech_recognition as sr
import pyttsx3

class Assistant():

    def __init__(self, db, app):
        
        self.db = db
        self.app = app
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'english_us')
        self.running = True


        self.DAY_EXTENSIONS = ["rd", "th", "st", "nd"]
    
    # Speaker
    def speak(self, text):
        
        self.engine.say(text)
        self.engine.runAndWait()

    
    # Listener
    def listen(self):

        r = sr.Recognizer()

        with sr.Microphone() as source:

            audio = r.listen(source)
            said = ""

            try:
                said = r.recognize_google(audio)
            
            except Exception as e:
                print(e)
            
        return said.lower()
    
    
    # Run
    def run(self):

        self.speak("Welcome to the JustDoIT application. Assistant is now active and listening. How can I help you?")

        while self.running:
            
            NOTE_STRS = ["make a note", "remember this", "write this down", "create task", "create new task", "add task", "add new task"]
            WHO_AM_I_STRS = ["who are you", "what is your name", "what's your name"]
            HELP_STRS = ["help", "how it works", "how it work", "how can i use it"]
            REMOVE_TASK_STRS = ["remove task", "delete task", "remove note", "delete note"]

            command = self.listen()
            command_handled = False

            for phrase in NOTE_STRS:

                if phrase in command:
                    self.create_task()
                    command_handled = True
                    break

            for phrase_1 in WHO_AM_I_STRS:

                if phrase_1 in command:
                    self.speak("My name is Jimmy, your personal assistant. I'm here to help you manage your tasks and keep things organized. If there's anything you need, just ask!")
                    command_handled = True
                    break

            for phrase_2 in HELP_STRS:

                if phrase_2 in command:
                    self.speak("I'm here to assist you! You can ask me to create tasks, set deadlines, or even just have a friendly chat. "
                    "Simply tell me what you need, and I'll do my best to help. If you need detailed guidance, feel free to ask!")
                    command_handled = True
                    break

            for phrase_3 in REMOVE_TASK_STRS:

                if phrase_3 in command:
                    self.delete_task()
                    command_handled = True
                    break

            if "hello" in command or "hi" in command:
                self.speak("Hi welcome to the JustDoIT application. How can i help you?")
                command_handled = True

            elif "hey jimmy" in command or "jimmy" in command:
                self.speak("Yes I hear your! How can I assist you today?")
                command_handled = True

            elif "quit" in command or "shut down" in command:
                self.speak("Stopping the assistant.")
                self.close()
                command_handled = True
                
            if not command_handled:
                self.speak("I'm sorry, I don't understand. Can you please rephrase your request?")


    # Stop
    def close(self):
        
        self.running = False
        self.app.quit()

   
    # Create Task
    def create_task(self):

        self.speak("Okay, creating a new task. What is the task name?")
        task_name = self.listen()

        self.speak("What is the task deadline? Please specify in the format 'day month year'.")
        exp_date = self.listen()

        task_date = self.get_date(exp_date)

        if not task_date:
            self.speak("Invalid date provided. Task creation canceled.")
            return
        
        self.add_task_to_database(task_name, task_date)

    
    # Delete Task
    def delete_task(self):

        self.speak("Which task do you want to delete? Please say the task number.")
        task = self.listen()

        word_to_number = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, 
            "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, 
            "eighteen": 18, "nineteen": 19, "twenty": 20, "twenty one": 21,
            "twenty two": 22, "twenty three": 23, "twenty four": 24, "twenty five": 25,
            "twenty six": 26, "twenty seven": 27, "twenty eight": 28, "twenty nine": 29,
            "thirty": 30
        }

        for word, number in word_to_number.items():
            task = task.replace(word, str(number))
        
        try:
            
            words = task.split()
            for word in words:
                if word.isdigit():
                    task_no = int(word)
                    break
            else:
                raise ValueError("No number found in input.")
        except ValueError:
            self.speak("I couldn't understand the task number. Please try again.")
            return

        if task_no <= 0 or task_no > len(self.app.task_treeview.get_children()):
            self.speak(f"Task number {task_no} is invalid. Please provide a valid task number.")
            return

        task_id = self.app.task_treeview.get_children()[task_no - 1]
        task_values = self.app.task_treeview.item(task_id)["values"]
        task_name = task_values[1]

        try:
            cursor = self.db.cursor()
            query = "DELETE FROM tasks WHERE task = %s"
            cursor.execute(query, (task_name,))
            self.db.commit()
            cursor.close()

            self.app.task_treeview.delete(task_id)
            self.speak(f"Task number {task_no} deleted successfully.")

            self.app.load_tasks_from_database()
        except Exception as err:
            self.speak(f"An error occurred while deleting the task: {err}")


    # Get Date Format
    def get_date(self, text):

        MONTHS = [ "january", "february", "march", "april", "may", "june",  "july", "august", "september", "october", "november", "december"]
        
        today = date.today()

        if "today" in text:
            return today
        
        day = -1
        month = -1
        year = -1

        for word in text.split():

            if word in MONTHS:
                month = MONTHS.index(word) + 1

            for ext in self.DAY_EXTENSIONS:
                if word.endswith(ext):
                    try:
                        day = int(word.rstrip("".join(self.DAY_EXTENSIONS)))
                    
                    except Exception as e:
                        print(e)
                        self.speak("Invalid day format. Please try again.")
            
            if word.isdigit() and len(word) == 4:
                year = int(word)

                if year < today.year:
                    self.speak("The year cannot be in the past. Please provide a valid year.")
                    return None

        if month == -1:
            self.speak("Invalid month. Please try again.")
            return None

        if day == -1:
            self.speak("Invalid day. Please try again.")
            return None

        if year == -1:
            year = today.year

        try:
            return date(year, month, day)
        
        except ValueError:
            self.speak("The date is invalid. Please check the day and month.")
            return None

    
    # Add Task to Database
    def add_task_to_database(self, task_name, task_date):

        if not self.db:
            self.speak("Database connection is not available. Unable to add the task.")
            return
        
        try:
            cursor = self.db.cursor()
            query = "INSERT INTO tasks (task, deadline) VALUES (%s, %s)"
            cursor.execute(query, (task_name, task_date))

            self.db.commit()
            cursor.close()

            self.app.load_tasks_from_database()

            self.speak(f"Task added successfully. Task name: {task_name}, Expire date: {task_date}")

        except Exception as e:
            self.speak(f"Failed to add the task. Error: {e}")


