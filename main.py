import sys
from PyQt6.QtWidgets import QApplication
from authorization_window import AuthorizationWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Создание экземпляра приложения PyQt
    auth_window = AuthorizationWindow()  # Создание экземпляра окна авторизации
    auth_window.show()  # Отображение окна авторизации
    sys.exit(app.exec())  # Запуск главного цикла приложения и выход из программы при его завершении