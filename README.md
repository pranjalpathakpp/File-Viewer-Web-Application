# File Management Web Application

This is a file management web application built with Flask. It allows users to log in/signup, upload, view, dark mode, log out, and manage their files. The application provides features like login, signup, dashboard, recent files, synced files, a trash bin, logout, dark mode, and a very interactive sidebar.

## Installation

1. Install the required libraries:

 The required libraries are:

   - Flask: A micro web framework for building web applications in Python.
   - Flask-WTF: An extension that integrates Flask with WTForms, which provides convenient form handling and validation.
   - Flask-Login: An extension that provides user session management, including login, logout, and user authentication.
   - Flask-SQLAlchemy: An extension that integrates SQLAlchemy, a SQL toolkit, and Object-Relational Mapping (ORM) library, with Flask.
   - Werkzeug: A comprehensive WSGI (Web Server Gateway Interface) utility library for Python.
   - SQLite: A lightweight, serverless database engine used as the backend database for this application.

 2. Set up the database:

   - Initialize the database:

   - Create the initial migration:

   - Apply the migration:

 3. Run the application:

4. Open your web browser and navigate to `http://localhost:5000` to access the application.

## Usage

The application provides the following features:

- **Login/signup Page**: The login and signup page ensures safety measures and has users safely signup and login on to our application. 

- **Dashboard**: The dashboard shows all the files uploaded by the user that haven't been deleted. You can upload files by clicking the "Upload Your Files" button.

- **Recents**: The recent page displays the most recently uploaded files.

- **Synced**: The synced page displays all the synced files that haven't been deleted.

- **Trash**: The trash page displays all the deleted files. You can permanently delete all the files in the trash by clicking the "Delete All" button.

- **LogOut**: The logout button provides safe log-out from the dashboard and redirects to the login page.

- **Darkmode**: Darkmode provides users to work in light mode as well as a dark mode as their preferences.

## Contributing

Contributions are welcome! Feel free to submit a pull request if you have any suggestions or improvements for this project.

To run the application in an editor, you must install the required libraries mentioned above using the command `pip install -r requirements.txt` command.

Let me know if you need any further assistance!
