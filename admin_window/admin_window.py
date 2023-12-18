from PyQt6.QtWidgets import QMainWindow, QTabWidget, QPushButton
import sqlite3
from admin_window.tab_admin1 import TabAdmin1
from admin_window.tab_admin2 import TabAdmin2
from datetime import datetime

class AdminWindow(QMainWindow):
    def __init__(self, username, access_level, auth_window):
        super().__init__()

        self.setWindowTitle(f'Привет, {username}')
        self.setGeometry(0, 0, 800, 600)

        self.tab_widget = QTabWidget(self)

        # Создаем пустые вкладки
        self.tab1 = TabAdmin1(username, access_level)
        self.tab2 = TabAdmin2(username)

        self.tab_widget.addTab(self.tab1, 'Документы')
        self.tab_widget.addTab(self.tab2, 'История')

        self.setCentralWidget(self.tab_widget)

        self.statusBar()
        self.closeEvent = self.closeEvent

        # Создаем кнопки
        self.change_user_button = QPushButton('Сменить пользователя')
        self.exit_button = QPushButton('Выйти')

        # Добавляем обработчик события для кнопки "Выйти"
        self.exit_button.clicked.connect(self.close_application)
        self.change_user_button.clicked.connect(self.change_user)

        # Сохраняем ссылку на окно авторизации
        self.auth_window = auth_window

        # Добавляем кнопки в нижнюю часть окна
        self.statusBar().addPermanentWidget(self.change_user_button)
        self.statusBar().addPermanentWidget(self.exit_button)

        # Подключение к базе данных
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        # Добавление записи о входе в историю
        self.add_action(username, "Вход в программу")

    # Функция добавления записи о выходе в историю
    def closeEvent(self, event):
        # Добавление записи о выходе в историю
        username = self.tab2.username
        self.add_action(username, "Выход из программы")
        event.accept()

    # Функция выхода из программы
    def close_application(self):
        self.close()

    # Функция смены пользователя
    def change_user(self):
        self.close()
        self.auth_window.refresh_user_combo()
        self.auth_window.show()

    # Функция добавления события об авторизации
    def add_action(self, username, action):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO actions (action, user, time) VALUES (?, ?, ?)"
        self.cursor.execute(query, (action, username, current_time))
        self.connection.commit()