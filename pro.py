import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QMessageBox,
    QVBoxLayout, QWidget, QFormLayout, QDialog, QTabWidget, QLineEdit
)
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from twilio.rest import Client
import requests  # To handle API requests for location

class SafetyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("Women's Safety App")
        self.setGeometry(100, 100, 800, 600)

        # Create a main container widget for the whole window
        container = QWidget(self)

        # Set the background image with appropriate scaling
        container.setAutoFillBackground(True)
        palette = QPalette()
        pixmap = QPixmap("C:/Main_pro/background.jpeg.jpg").scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        container.setPalette(palette)

        # Tab widget setup
        self.tabs = QTabWidget(container)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: rgba(255, 255, 255, 0.7);
            }
            QTabBar::tab {
                background-color: rgba(255, 255, 255, 0.7);
                padding: 10px;
            }
        """)
        container.setLayout(QVBoxLayout())
        container.layout().addWidget(self.tabs)

        # Adding Tabs
        self.tabs.addTab(self.create_home_tab(), "Home")
        self.tabs.addTab(self.create_contacts_tab(), "Contacts")
        self.tabs.addTab(self.create_tips_tab(), "Safety Tips")
        self.tabs.addTab(self.create_map_tab(), "Map")

        # Emergency contacts storage
        self.contacts = []

        self.setCentralWidget(container)

    def create_home_tab(self):
        home_tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # Align everything to the center
        home_tab.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")

        welcome_label = QLabel("Welcome to Women's Safety App")
        welcome_label.setFont(QFont("Arial", 20, QFont.Bold))
        welcome_label.setStyleSheet("color: #4CAF50;")
        welcome_label.setAlignment(Qt.AlignCenter)  # Center-align the text

        # Emergency Buzzer Button with red color and increased size
        buzzer_button = QPushButton("Emergency ")
        buzzer_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                border-radius: 75px;
                width: 150px;
                height: 150px;
                text-align: center;
                font-size: 18px;
                border: none;
            }
        """)
        buzzer_button.setFixedSize(150, 150)
        buzzer_button.clicked.connect(self.send_emergency_alert)

        layout.addStretch()
        layout.addWidget(welcome_label, alignment=Qt.AlignCenter)
        layout.addWidget(buzzer_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        home_tab.setLayout(layout)
        return home_tab

    def create_contacts_tab(self):
        contacts_tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        contacts_tab.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")

        register_button = QPushButton("Register Emergency Contacts")
        register_button.setStyleSheet(
            "background-color: #4CAF50; color: black; font-weight: bold; border-radius: 5px;")
        register_button.clicked.connect(self.open_registration_form)

        layout.addWidget(register_button)
        contacts_tab.setLayout(layout)
        return contacts_tab

    def create_tips_tab(self):
        tips_tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        tips_tab.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")

        tips_button = QPushButton("Show Safety Tips")
        tips_button.setStyleSheet(
            "background-color: #9c27b0; color: black; font-weight: bold; padding: 10px; border-radius: 10px;")
        tips_button.clicked.connect(self.show_safety_tips)

        layout.addWidget(tips_button)
        tips_tab.setLayout(layout)
        return tips_tab

    def create_map_tab(self):
        map_tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        map_tab.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")

        self.map_view = QWebEngineView()
        self.map_view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)


        layout.addWidget(self.map_view)
        map_tab.setLayout(layout)

        self.tabs.currentChanged.connect(
            lambda index: self.load_map() if self.tabs.tabText(index) == "Map" else None
        )
        return map_tab

    def load_map(self):
        location = self.get_live_location()
        latitude, longitude = location.split(',')
        google_maps_url = f"https://www.google.com/maps?q={latitude.strip()},{longitude.strip()}&t=k"
        self.map_view.setUrl(QUrl(google_maps_url))

    def open_registration_form(self):
        self.registration_form = RegistrationForm(self)
        self.registration_form.exec_()

    def send_emergency_alert(self):
        if not self.contacts:
            QMessageBox.warning(self, "No Contacts", "Please register emergency contacts first.")
            return

        location = self.get_live_location()
        latitude, longitude = location.split(',')

        google_maps_url = f"https://www.google.com/maps?q={latitude.strip()},{longitude.strip()}&t=k"

        account_sid = 'ACc49f800e0a1609b31babb52fc02a9def'
        auth_token = '817e9f3e98931384c5397e3910a471eb'
        client = Client(account_sid, auth_token)

        for contact in self.contacts:
            try:
                message = client.messages.create(
                    body=f"Emergency Alert: I am in danger! My location is: {google_maps_url}",
                    from_='+12029153004',
                    to=contact['phone']
                )
                print(f"Message sent to {contact['phone']}: {message.sid}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not send message to {contact['phone']}: {str(e)}")

        QMessageBox.information(self, "SOS Alert", "Emergency alert sent to your contacts!")

    def show_safety_tips(self):
        QMessageBox.information(
            self, "Safety Tips", "Stay alert, avoid isolated areas, and keep your phone charged.")

    def get_live_location(self):
        try:
            access_key = 'your_valid_access_key'
            response = requests.get(f"http://api.ipstack.com/check?access_key={access_key}")
            if response.status_code == 200:
                data = response.json()
                latitude = data.get("latitude", "0.0")
                longitude = data.get("longitude", "0.0")
                return f"{latitude}, {longitude}"
            return "0.0, 0.0"
        except requests.exceptions.RequestException as e:
            return "0.0, 0.0"

class RegistrationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register Emergency Contact")
        self.setGeometry(200, 200, 400, 200)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()

        layout.addRow("Name:", self.name_input)
        layout.addRow("Phone:", self.phone_input)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_contact)

        layout.addRow(register_button)
        self.setLayout(layout)

    def register_contact(self):
        name = self.name_input.text()
        phone = self.phone_input.text()

        if not name or not phone:
            QMessageBox.warning(self, "Input Error", "Please fill out all fields.")
            return

        self.parent().contacts.append({'name': name, 'phone': phone})
        QMessageBox.information(self, "Success", f"Registered {name} successfully!")
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SafetyApp()
    window.show()
    sys.exit(app.exec_())
