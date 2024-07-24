Facial Recognition Attendance System

Description
This project is an attendance management system that utilizes facial recognition for employee verification and attendance marking. The system is built using Django for the backend and OpenCV for facial recognition.

Features
- **User Registration**: Register users with profile pictures.
- **Model Training**: Train the facial recognition model with the captured images.
- **Real-time Scanning**: Scan faces using the webcam to verify identity and mark attendance.
- **Attendance Dashboard**: View attendance records and reports.

Technologies Used
- **Backend**: Django
- **Facial Recognition**: OpenCV
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default)

Usage
Registering Users
Go to the registration page.
Fill in the form with the required details and capture a profile picture.
Submit the form to register the user.
Training the Model
After registering users, go to the admin panel.
Click on the "Train Model" button to train the facial recognition model with the registered user images.
Scanning and Marking Attendance
Click on the "Scan" button on the homepage.
Allow access to the webcam.
The system will scan faces in real-time and mark attendance for recognized users.

1_ Create and activate a virtual environment
2_ Install the dependencies : pip install -r requirements.txt
3_ Apply the migrations: python manage.py migrate
4_ Create a superuser (to access the admin interface): python manage.py createsuperuser
5_ Run the development server: python manage.py runserver
6_ Access the application: Open a web browser and go to http://127.0.0.1:8000/

