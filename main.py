import threading # from typing import List, Dict импортируются для указания типов данных
from typing import List, Dict

import uvicorn
from PyQt5.QtGui import QColor
from fastapi import FastAPI, HTTPException, requests
import random
import sys
import time
from PyQt5.QtCore import Qt, QTimer, QDateTime, QDate, QPropertyAnimation, QRect, QObject, pyqtProperty, QEasingCurve

from database import PasswordDatabase, UserDatabase

from basewindow import ClickerGameWindow, AuthorithationWindow, SWindow, LogInWindow
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, \
    QListWidget

app = FastAPI(
    title="My API",
    description="A simple FastAPI application",
    version="1.0.0"
)

user_db = UserDatabase("userdata.db")

@app.get("/")  # HTTP GET method at root path
async def root():
    return {"message": "Hello, World!"}

@app.post("/button-pressed")
async def button_pressed():  #async def can be used by many users at once
    print("Button was pressed!")
    return {"message": "Button press received"}

@app.get("/leaderboard")
async def get_leaderboard() -> List[Dict[str, int]]:
    users = user_db.get_all_users()  # returns list of tuples like [(username, coins), ...]
    # Sort descending by coins
    users_sorted = sorted(users, key=lambda x: x[1], reverse=True)
    # Convert to list of dicts for JSON
    leaderboard = [{"username": u, "coins": c} for u, c in users_sorted]

def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000)

class ColorAnimator(QObject):
    def __init__(self, button):
        super().__init__()
        self._color = QColor('red')
        self.button = button

    def getColor(self):
        return self._color

    def setColor(self, color):
        self._color = color
        self.button.setStyleSheet(f"background-color: {color.name()};")  # .name() returns the color as a hex string like '#RRGGBB' usable in CSS

    color = pyqtProperty(QColor, getColor, setColor)

class authorithation(AuthorithationWindow):
    def __init__(self) -> None:
        super().__init__("Authorithation Window")
        self.db = PasswordDatabase()
        self.user_db = UserDatabase("userdata.db")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.password = ''
        layout.addLayout(self.init_at_layout())

    def init_at_layout(self):
        header_layout = QVBoxLayout()

        self.w_text = QLabel("Welcome, log in or sign in!")

        self.log_in = QPushButton("Log in")
        self.log_in.clicked.connect(self.open_log_in_window)

        self.sign_in = QPushButton("Sign in")
        self.sign_in.clicked.connect(self.open_regestration_window)

        header_layout.addWidget(self.w_text)
        header_layout.addWidget(self.log_in)
        header_layout.addWidget(self.sign_in)

        return header_layout

    def open_regestration_window(self):
        self.second_window = signInWindow("Sign in!", self.db, self.user_db)
        self.second_window.show()
        self.hide()

    def open_log_in_window(self):
        self.second_window = logInWindow("Log in!", self.db, self.user_db)
        self.second_window.show()
        self.hide()

    def open_second_window(self):
        username = self.dict_to_check["username"]
        self.second_window = clickerGame(username)
        self.second_window.show()
        self.hide()

class signInWindow(SWindow):
    def __init__(self, header, db, user_db) -> None:
        super().__init__(header)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.password = ''
        self.db = PasswordDatabase()
        self.user_data_base = user_db
        layout.addLayout(self.init_sw_layout())

    def init_sw_layout(self):
        header_layout = QVBoxLayout()
        self.s_text = QLabel("Create a reliable password!")

        self.username_input_field = QLineEdit()
        self.username_input_field.setPlaceholderText("Type in username")

        self.password_input_field = QLineEdit()
        self.password_input_field.setPlaceholderText("Type in password")

        self.set_password = QPushButton("Register account")
        self.set_password.clicked.connect(self.set_password_def)

        self.go_back = QPushButton("Go back")
        self.go_back.clicked.connect(self.open_main_window)

        header_layout.addWidget(self.s_text)
        header_layout.addWidget(self.username_input_field)
        header_layout.addWidget(self.password_input_field)
        header_layout.addWidget(self.set_password)
        header_layout.addWidget(self.go_back)

        return header_layout

    def open_second_window(self, username, db):
        self.second_window = clickerGame('Clicker', username, db)
        self.second_window.show()
        self.hide()

    def open_main_window(self):
        self.second_window = authorithation()
        self.second_window.show()
        self.hide()

    def set_password_def(self):
        self.password_dict = {
            "username": self.username_input_field.text(),
            "password": self.password_input_field.text()
        }

        username = self.username_input_field.text().strip()
        password = self.password_input_field.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Both fields must be filled in!")
            return  # Stop here if any field is empty

        success = self.db.insert_user(self.password_dict)
        if success:
            self.user_data_base.insert_user(self.password_dict["username"], 1)
            print("Inserted user:", self.password_dict["username"])
            print("Users now:", self.user_data_base.get_all_users())

            QMessageBox.information(self, "Success", "You successfully created an account!")
            self.open_second_window(self.password_dict["username"], self.user_data_base)
        else:
            QMessageBox.warning(self, "Error", "Username already exists.")


class logInWindow(LogInWindow):
    def __init__(self, header, db, user_db) -> None:
        super().__init__(header)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.password = ''
        self.db = PasswordDatabase()
        self.user_data_base = user_db
        layout.addLayout(self.init_sw_layout())

    def init_sw_layout(self):
        header_layout = QVBoxLayout()
        self.s_text = QLabel("Enter your account data")

        self.username_input_field = QLineEdit()
        self.username_input_field.setPlaceholderText("Type in username")

        self.password_input_field = QLineEdit()
        self.password_input_field.setPlaceholderText("Type in password")

        self.proceed = QPushButton("Proceed")
        self.proceed.clicked.connect(self.check_for_correct_data)

        self.go_back = QPushButton("Go back")
        self.go_back.clicked.connect(self.open_main_window)

        header_layout.addWidget(self.s_text)
        header_layout.addWidget(self.username_input_field)
        header_layout.addWidget(self.password_input_field)
        header_layout.addWidget(self.proceed)
        header_layout.addWidget(self.go_back)

        return header_layout

    def open_second_window(self, username, db):
        self.second_window = clickerGame('Clicker', username, db)
        self.second_window.show()
        self.hide()

    def check_for_correct_data(self):
        self.dict_to_check = {
            "username": self.username_input_field.text(),
            "password": self.password_input_field.text()
        }

        is_user_exists = self.db.get_user_by_credentials(self.dict_to_check["username"], self.dict_to_check["password"])
        if is_user_exists:
            QMessageBox.information(self, "Success", "You logged in successfully!")
            self.open_second_window(self.dict_to_check["username"], self.user_data_base)
        else:
            QMessageBox.warning(self, "Error", "Username or password is incorrect.")

    def open_main_window(self):
        self.second_window = authorithation()
        self.second_window.show()
        self.hide()

class LeaderboardWindow(QWidget):
    def __init__(self, user_db: UserDatabase):
        super().__init__()
        self.setWindowTitle("Leaderboard")
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.leaderboard_list = QListWidget()
        layout.addWidget(QLabel("Top Users by Coins:"))
        layout.addWidget(self.leaderboard_list)

        self.load_leaderboard(user_db)

    def load_leaderboard(self, user_db: UserDatabase):
        users = user_db.get_all_users()
        users_sorted = sorted(users, key=lambda x: x[1], reverse=True)  # sort by coin_amount
        for username, coins in users_sorted:
            self.leaderboard_list.addItem(f"{username}: {coins} coins")

class clickerGame(ClickerGameWindow):# 'has no attribute' = does not exists in this class
    def __init__(self, header, username: str, user_db) -> None:
        super().__init__(header + " of " + username)
        layout = QVBoxLayout()
        self.user_data_base = user_db
        print("Using DB file:", self.user_data_base.dbname)

        self.username_of_game = username

        self.user_data_base.insert_user(self.username_of_game, 1)

        self.user_data_base.count_rows()
        print("Users after insert:", self.user_data_base.get_all_users())

        self.coin_amount = self.user_data_base.get_money_for_user(self.username_of_game)
        print(f"Loaded money for {self.username_of_game}: {self.coin_amount}")

        self.user_data_base.update_money(self.username_of_game, self.coin_amount)
        print("Users after update:", self.user_data_base.get_all_users())

        self.db = PasswordDatabase()
        self.setLayout(layout)
        self.c_p_c_upgrade_cost = 50
        self.l_r_amount = 0
        self.l_r_upgrade_cost = 250
        self.a_p_c_upgrade_cost = 100
        self.am_p_c_upgrade_cost = 500
        self.click_cooldown = 1
        self.coin_per_click = 1
        self.coin_per_auto = 1
        self.doAutoCoinAddition = True
        self.auto_coin_timer = QTimer(self)
        self.auto_coin_timer.timeout.connect(self.add_auto_coins)
        self.auto_click_cooldown = 5000
        self.auto_coin_timer.start(self.auto_click_cooldown)

        layout.addLayout(self.init_main_layout())

        self.color_animator = ColorAnimator(self.open_leaderboard_button)
        self.anim = QPropertyAnimation(self.color_animator, b"color")
        self.anim.setDuration(2000)
        self.anim.setLoopCount(-1)  # Loop forever
        self.anim.setKeyValueAt(0, QColor('blue'))
        self.anim.setKeyValueAt(0.5, QColor('green'))
        self.anim.setKeyValueAt(1, QColor('blue'))
        self.anim.setEasingCurve(QEasingCurve.Linear)  # Linear easing keeps the speed constant during the animation
        self.anim.start()
        self.last_claimed_date = None

    def init_main_layout(self):
        header_layout = QVBoxLayout()

        self.try_claim_daily_bonus_button = QPushButton(
            f"    Claim daily bonus!    ")
        self.try_claim_daily_bonus_button.setObjectName("tryClaimButton")
        self.try_claim_daily_bonus_button.clicked.connect(self.check_daily_bonus)

        self.auto_click_amount_upgrade_button = QPushButton(
            f"Click to buy auto click amount upgrade! Cost: {self.am_p_c_upgrade_cost}", self)
        self.auto_click_amount_upgrade_button.setObjectName("AMupgradeButton")
        self.auto_click_amount_upgrade_button.clicked.connect(self.am_p_c_upgrade)

        self.auto_click_upgrade_button = QPushButton(
            f"Click to buy auto click upgrade! Cost: {self.a_p_c_upgrade_cost}", self)
        self.auto_click_upgrade_button.setObjectName("AupgradeButton")
        self.auto_click_upgrade_button.clicked.connect(self.a_p_c_upgrade)

        self.lucky_roll_upgrade_button = QPushButton(f"Click to buy lucky roll upgrade! Cost: {self.l_r_upgrade_cost}", self)
        self.lucky_roll_upgrade_button.setObjectName("lupgradeButton")
        self.lucky_roll_upgrade_button.clicked.connect(self.l_r_upgrade)

        self.coins_per_click_upgrade_button = QPushButton(f"Click to buy coins per click upgrade! Cost: {self.c_p_c_upgrade_cost}", self)
        self.coins_per_click_upgrade_button.setObjectName("cupgradeButton")
        self.coins_per_click_upgrade_button.clicked.connect(self.c_p_c_upgrade)

        self.coin_count_display = QLineEdit(self)
        self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
        self.coin_count_display.setReadOnly(True)

        self.click_button = QPushButton("Click!", self)
        self.click_button.setObjectName("clickButton")
        self.click_button.clicked.connect(self.add_coins)

        self.open_leaderboard_button = QPushButton("View Leaderboard")
        self.open_leaderboard_button.setObjectName("open_leaderbord_Button")
        self.open_leaderboard_button.clicked.connect(self.show_leaderboard)

        header_layout.addWidget(self.try_claim_daily_bonus_button)
        header_layout.addWidget(self.auto_click_amount_upgrade_button)
        header_layout.addWidget(self.auto_click_upgrade_button)
        header_layout.addWidget(self.lucky_roll_upgrade_button)
        header_layout.addWidget(self.coins_per_click_upgrade_button)
        header_layout.addWidget(self.coin_count_display)
        header_layout.addWidget(self.click_button)
        header_layout.addWidget(self.open_leaderboard_button)

        return header_layout

    def add_moneyamount_column(self):
        self.user_data_base.add_user_and_money_column()

    def show_leaderboard(self):
        self.leaderboard_window = LeaderboardWindow(self.user_data_base)
        self.leaderboard_window.show()

    def add_coins(self):
        self.coin_amount += self.coin_per_click
        print(self.coin_amount)
        luckyRollProbability = random.random()
        if luckyRollProbability <= 0.05:
            self.coin_amount += self.coin_amount * self.l_r_amount
        self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
        self.update_user_score()
        self.user_data_base.update_money(self.username_of_game, self.coin_amount)

    def update_user_score(self):
        self.user_data_base.update_money(self.username_of_game, self.coin_amount)

    def sync_from_password_db(self, password_db: PasswordDatabase):
        # Get all usernames from PasswordDatabase
        users = password_db.get_users()  # Returns list of (id, username, password)
        for _, username, _ in users:  # unpacking id, username, password; ignoring id and password
            self.user_data_base.insert_user(username)
        print("Current users in UserDatabase:", self.user_data_base.get_all_users())

    def check_daily_bonus(self):
        today = QDate.currentDate()

        try:
            with open("dailyBonusDate.txt", "r") as file:
                last_date_str = file.read().strip()
                if last_date_str:
                    self.last_claimed_date = QDate.fromString(last_date_str, "yyyy-MM-dd")
                else:
                    self.last_claimed_date = None
        except FileNotFoundError:
            self.last_claimed_date = None

        if self.last_claimed_date == today:
            QMessageBox.information(self, "Daily Bonus", "You already claimed your bonus today!")
            return

        self.coin_amount += 1000
        self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
        QMessageBox.information(self, "Daily Bonus", "You received 1000 coins!")

        with open("dailyBonusDate.txt", "w") as file:
            file.write(today.toString("yyyy-MM-dd"))

        self.last_claimed_date = today

    def on_button_click(self):
        try:
            response = requests.post("http://127.0.0.1:8000/button-pressed")
            data = response.json()
            QMessageBox.information(self, "Response", data.get("message", "No message"))
        except Exception as e:
            QMessageBox.warning(self, "Error", str())

    def add_auto_coins(self):
        self.coin_amount += self.coin_per_auto
        print(self.coin_amount)
        self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
        self.update_user_score()
        self.sync_from_password_db(self.db)
        self.user_data_base.update_money(self.username_of_game, self.coin_amount)

    def c_p_c_upgrade(self):
        if self.coin_amount >= self.c_p_c_upgrade_cost:
            self.coin_per_click += 1
            self.coin_amount -= self.c_p_c_upgrade_cost
            self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
            self.c_p_c_upgrade_cost += int(self.c_p_c_upgrade_cost * 0.5)
            self.coins_per_click_upgrade_button.setText(f"Click to buy coins per click upgrade! Cost: {self.c_p_c_upgrade_cost}")
        else:
            QMessageBox.warning(
                self,
                "Not enough coins",
                "You don't have enough coins to buy this upgrade."
            )

    def a_p_c_upgrade(self):
        if self.coin_amount >= self.a_p_c_upgrade_cost:
            self.auto_click_cooldown -= 200
            self.auto_coin_timer.start(self.auto_click_cooldown)
            self.coin_amount -= self.a_p_c_upgrade_cost
            self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
            self.a_p_c_upgrade_cost += int(self.a_p_c_upgrade_cost * 0.5)
            self.auto_click_upgrade_button.setText(f"Click to buy auto click upgrade! Cost: {self.a_p_c_upgrade_cost}")
            if self.auto_click_cooldown <= 10:
                self.auto_click_cooldown = 10
                self.auto_click_upgrade_button.setText(
                    f"You bought max auto click upgrades!")
                self.auto_click_upgrade_button.setEnabled(False)
        else:
            QMessageBox.warning(
                self,
                "Not enough coins",
                "You don't have enough coins to buy this upgrade."
            )

    def am_p_c_upgrade(self):
        if self.coin_amount >= self.am_p_c_upgrade_cost:
            self.coin_per_auto += 1
            self.coin_amount -= self.am_p_c_upgrade_cost
            self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
            self.am_p_c_upgrade_cost += int(self.am_p_c_upgrade_cost * 0.5)
            self.auto_click_amount_upgrade_button.setText(f"Click to buy coins per click upgrade! Cost: {self.am_p_c_upgrade_cost}")
        else:
            QMessageBox.warning(
                self,
                "Not enough coins",
                "You don't have enough coins to buy this upgrade."
            )

    def l_r_upgrade(self):
        if self.coin_amount >= self.l_r_upgrade_cost:
            self.l_r_amount += 1
            self.coin_amount -= self.l_r_upgrade_cost
            self.coin_count_display.setText(f"Coins you have: {self.coin_amount}")
            self.l_r_upgrade_cost += int(self.l_r_upgrade_cost * 2)
            self.lucky_roll_upgrade_button.setText(f"Click to buy lucky roll upgrade! Cost: {self.l_r_upgrade_cost}")
        else:
            QMessageBox.warning(
                self,
                "Not enough coins",
                "You don't have enough coins to buy this upgrade."
            )

if __name__ == "__main__":
    api_thread = threading.Thread(target=run_fastapi, daemon=True) #threading creates a new separate thread of execution allowing us to run a function concurrently with the main program
    api_thread.start()

    app = QApplication(sys.argv)

    db = PasswordDatabase()
    window = authorithation()
    window.db = db
    window.show()

    exit_code = app.exec_()
    db.close()
    sys.exit(exit_code)