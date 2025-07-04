from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QMessageBox


class ClickerGameWindow(QWidget):
    def __init__(self, header:str) -> None:
        super().__init__()
        with open("style.css", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())
            print(stylesheet.read())
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(400, 660)

class AuthorithationWindow(QWidget):
    def __init__(self, header:str) -> None:
        super().__init__()
        with open("style.css", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())
            print(stylesheet.read())
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(300, 250)

class LogInWindow(QWidget):
    def __init__(self, header:str) -> None:
        super().__init__()
        with open("style.css", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())
            print(stylesheet.read())
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(300, 300)

class LeaderBoardWindow(QWidget):
    def __init__(self, header:str) -> None:
        super().__init__()
        with open("style.css", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())
            print(stylesheet.read())
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(300, 300)
class SWindow(QWidget):
    def __init__(self, header:str) -> None:
        super().__init__()
        with open("style.css", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())
            print(stylesheet.read())
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(300, 300)