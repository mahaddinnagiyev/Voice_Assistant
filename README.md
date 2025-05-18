# JustDoIT To-Do App

## Overview
JustDoIT is a desktop task management application built using **Tkinter** and **CustomTkinter**. The app allows you to easily manage tasks, set deadlines, and create/remove tasks with the help of a voice assistant named **Jimmy**.

### Key Features:
- Add tasks with deadlines.
- Delete tasks.
- Voice assistant ("Jimmy") to assist with creating and removing tasks.
- Simple and intuitive GUI.

---

## Prerequisites
Before running the JustDoIT To-Do app, ensure you have the following installed:

- Python 3.x
- MySQL Server (for database)

---

## Installation

1. **Clone the repository** to your local machine:

    ```bash
    git clone https://github.com/your-username/JustDoIT-App.git
    cd JustDoIT-App
    ```

2. **Set up the environment** by creating and activating a virtual environment:

    ```bash
    python -m venv app-env
    source app-env/bin/activate  # For macOS/Linux
    app-env\Scripts\activate  # For Windows
    ```

3. **Install dependencies** using `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory and add the following configurations:

    ```bash
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=password123
    DB_NAME=to_do_app
    ```

    - Ensure your MySQL database is set up with the name `to_do_app`. Create a table named `tasks` with columns `task` (VARCHAR) and `deadline` (DATE).

---

## Usage

1. **Run the application**:

    ```bash
    python main.py
    ```

2. **Interacting with the app**:
    - Open the app window, and you can use the following voice commands:
        - **"Make a note"**: To add a task.
        - **"Create new task"**: To add a new task with a deadline.
        - **"Delete task"**: To remove a task.
        - **"Who are you?"**: To ask about the assistant's identity.
        - **"Help"**: To get guidance on how the app works.
        - **"Quit" or "Shut down"**: To close the assistant.

---

## Voice Assistant (Jimmy)

Jimmy is a voice assistant integrated into the app to help users with managing tasks. Using **SpeechRecognition** and **pyttsx3**, Jimmy can listen to commands and provide verbal responses.

### Available Commands:
- **Create Task**: "Create a new task" / "Add task" / "Make a note"
- **Delete Task**: "Remove task" / "Delete task"
- **Ask About Jimmy**: "Who are you?" / "What is your name?"
- **Help**: "How does it work?" / "How can I use it?"

---

## Contributing

Feel free to fork the repository, make changes, and submit pull requests if you would like to contribute to the development of JustDoIT To-Do App.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
