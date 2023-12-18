import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QHeaderView, QFileDialog, \
    QInputDialog, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, QDateTime
import sqlite3

class TabExternal1(QWidget):
    def __init__(self, username, access_level):
        super().__init__()
        self.username = username
        self.access_level = access_level

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Имя файла", "Отправитель", "Время загрузки", "Статус"]
        )
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.upload_button = QPushButton("Загрузить файл")
        self.delete_button = QPushButton("Удалить файл")
        self.download_button = QPushButton("Скачать файл")
        self.change_status_button = QPushButton("Изменить статус")

        button_layout.addStretch()
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.change_status_button)

        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addStretch()

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.table.setShowGrid(False)

        style = "::item { padding-right: 20px }"

        self.table.setStyleSheet(style)

        self.upload_button.setToolTip("Загрузить выбранный файл")
        self.delete_button.setToolTip("Удалить выбранный файл")
        self.download_button.setToolTip("Скачать выбранный файл")
        self.change_status_button.setToolTip("Изменить статус выбранного файла")

        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        self.upload_button.clicked.connect(self.upload_file)
        self.delete_button.clicked.connect(self.delete_file)
        self.download_button.clicked.connect(self.download_file)
        self.change_status_button.clicked.connect(self.change_status)

        self.refresh_table()

    def refresh_table(self):
        self.table.clearContents()
        self.cursor.execute("SELECT name, sender, time, status FROM files")
        files = self.cursor.fetchall()
        self.table.setRowCount(len(files))
        for row, file in enumerate(files):
            for col, data in enumerate(file):
                item = QTableWidgetItem(str(data))
                self.table.setItem(row, col, item)
        for col in range(self.table.columnCount()):
            self.table.resizeColumnToContents(col)

    def upload_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Documents (*.pdf *.docx *.xlsx)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = file_dialog.selectedFiles()
            for file in files:
                filename = os.path.basename(file)
                sender = self.username
                time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                status = "Прием документа"
                self.cursor.execute("INSERT INTO files (name, sender, time, status) VALUES (?, ?, ?, ?)",
                                    (filename, sender, time, status))
            self.connection.commit()
            self.refresh_table()

    def delete_file(self):
        access_level = self.access_level

        if access_level == "Администратор":
            selected_rows = self.table.selectedItems()
            if selected_rows:
                reply = QMessageBox.question(self, "Подтверждение удаления", "Вы уверены, что хотите удалить выбранные файлы?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    for item in selected_rows:
                        row = item.row()
                        file_id = self.table.item(row, 0).text()
                        self.cursor.execute("DELETE FROM files WHERE name = ?", (file_id,))
                    self.connection.commit()
                    self.refresh_table()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Недостаточно прав для удаления файла')

    def download_file(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            file_name = self.table.item(selected_row, 0).text()
            project_folder = os.path.dirname(os.path.dirname(__file__))
            files_folder = os.path.join(project_folder, "Файлы")
            customer_folder = os.path.join(files_folder, self.username)
            for folder in [files_folder, customer_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            file_path = os.path.join(customer_folder, file_name)
            with open(file_path, 'w') as file:
                file.write("Пример содержимого файла")

            QMessageBox.information(self, 'Скачивание файла', f'Файл "{file_name}" был сохранен в папке {self.username}.')
            self.refresh_table()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите файл для скачивания')

    def change_status(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            file_id = self.table.item(selected_row, 0).text()
            current_status = self.table.item(selected_row, 3).text()
            available_statuses = ["Прием документа"]
            selected_status, ok = QInputDialog.getItem(self, "Изменить статус",
                                                       "Выберите новый статус:", available_statuses, 0, False)
            if ok:
                self.cursor.execute("UPDATE files SET status = ? WHERE name = ?", (selected_status, file_id))
                self.connection.commit()
                self.refresh_table()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите файл для изменения статуса')