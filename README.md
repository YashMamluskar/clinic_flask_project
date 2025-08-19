Clinic Management System
A comprehensive web application built with Flask to manage patient records, consultations, and prescriptions in a clinical setting. This system features role-based access control, allowing different user types (Reception, Doctor, Pharmacist) to perform specific tasks within a secure, login-protected environment.

Features
Role-Based User Authentication: Secure login system for different staff roles (Reception, Doctor, Pharmacist).

Patient Registration: Reception staff can register new patients with their essential details.

Patient Database: View and search a complete list of all registered patients.

Consultation Management: Doctors can view patient details, add new consultation notes, and record diagnoses.

Prescription System: Doctors can add multiple medications and dosages to a patient's consultation record.

Pharmacy Queue: Pharmacists have a dedicated view to see all pending prescriptions, grouped by patient.

Dispense Medication: Pharmacists can mark all of a patient's pending medications as "Dispensed" in a single action.

Dashboard: An overview page showing key statistics like total patients, total consultations, and pending prescriptions.

Technologies Used
Backend: Python, Flask

Database: SQLite with Flask-SQLAlchemy and Flask-Migrate for database management.

Authentication: Flask-Login for session management and Flask-Bcrypt for password hashing.

Frontend: Jinja2 Templating (integrated with Flask).

Getting Started
Follow these instructions to get a local copy of the project up and running for development and testing purposes.

Prerequisites
Python 3.x installed on your system.

Git for cloning the repository.

Installation & Setup
Clone the repository:

git clone https://github.com/YashMamluskar/clinic_flask_project.git
cd clinic_flask_project

Create and activate a virtual environment:
This keeps your project dependencies isolated.

On Windows:

python -m venv venv
venv\Scripts\activate

On macOS/Linux:

python3 -m venv venv
source venv/bin/activate

Install the required packages:

pip install -r requirements.txt

Run the application:

flask run

Access the application:
Open your web browser and navigate to http://127.0.0.1:5000.

How to Use the System
Register a User:
To create the first user account (e.g., a doctor or receptionist), navigate to http://127.0.0.1:5000/register_user. Fill in the form to create an account with a specific role.

Log In:
Go to the login page and use the credentials you just created.

Explore:
Once logged in, you can explore the dashboard and perform actions based on the role you assigned to your user. For example, a user with the 'doctor' role will be able to access patient details and add consultations.