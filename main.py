import os
import sqlite3
import random
import sys
from getpass import getuser

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QFileDialog


class GetCookiesForHostApp(QWidget):
    def __init__(self):
        super().__init__()
        name_user = getuser()
        path_to_sqlite = ""

        dir_path = f'/home/{name_user}/snap/firefox/common/.mozilla/firefox'
        x = os.listdir(dir_path)
        for y in x:
            if os.path.exists(f'{dir_path}/{y}/cookies.sqlite'):
                path_to_sqlite = y
            else:
                continue
        self.local_storage_path = f"/home/{name_user}/snap/firefox/common/.mozilla/firefox/{path_to_sqlite}/cookies.sqlite"
        self.target_host = None
        self.extension = None
        _signal = pyqtSignal(int)

        vbox = QVBoxLayout()

        # Создаем кнопку Download
        self.download_button = QPushButton('Get cookie', self)
        self.download_button.clicked.connect(self.get_session_data)
        vbox.addWidget(self.download_button)

        # Создаем кнопку Put
        self.get_button = QPushButton('Put cookie', self)
        self.get_button.clicked.connect(self.insert_data_from_file)
        vbox.addWidget(self.get_button)

        # Настраиваем layout для главного окна
        self.setLayout(vbox)

        # Настройки главного окна
        self.setWindowTitle('Get cookie')
        self.setGeometry(100, 100, 300, 200)
        self.show()

    def save_session_data(self, session_data):
        # Создание списка строк для сохранения в файл
        lines = [f"{' '.join(map(str, values))}" for id, values in session_data.items()]

        # Выбор места сохранения файла
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if save_path:
            with open(save_path, "w") as file:
                file.write("\n".join(lines))

            # Форматирование вывода в текстовом файле
            with open(save_path, "r") as file:
                lines = file.readlines()

            formatted_lines = []
            for line in lines:
                formatted_lines.append(line.strip())

            with open(save_path, "w") as file:
                file.write("\n".join(formatted_lines))

            QMessageBox.information(self, 'Good', f'Cookie downloaded')

    def get_session_data(self):

        session_data = self.fetch_session_data(self.target_host)
        if not session_data:
            QMessageBox.critical(self, 'Error', f'No cookie for host')
            return
        self.save_session_data(session_data)

    def fetch_session_data(self, host):
        session_data = {}
        # Открытие файла локального хранилища
        with sqlite3.connect(self.local_storage_path) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM moz_cookies")

            rows = cursor.fetchall()
            for row in rows:
                session_data[row[0]] = row

        return session_data

    def insert_data_from_file(self):
        count = 0
        error = ""
        # Выбор файла с данными о куках
        file_path, filetype = QFileDialog.getOpenFileName(self,
                                                         "Выбрать файл",
                                                         ".",
                                                         "All Files(*);;Text Files(*.txt);;JPEG Files(*.jpeg);;\
                                                         PNG Files(*.png);;GIF File(*.gif)")

        if file_path:
            with open(file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split(" ")
                    data[0] = random.randint(1000000, 9999999)

                    # Вставка данных в таблицу
                    count, error = self.insert_cookie_data(data, count, error)

                if count != 0:
                    QMessageBox.information(self, 'Good', f'Cookie put in mozilla')
                else:
                    QMessageBox.critical(self, 'Error', f'Error: {error}')

    def insert_cookie_data(self, data, count, error):

        with sqlite3.connect(self.local_storage_path) as connection:
            try:
                sql = '''REPLACE INTO moz_cookies(id, originAttributes, name, value, host, path, expiry, lastAccessed, creationTime, isSecure, isHttpOnly, inBrowserElement, sameSite, rawSameSite, schemeMap, isPartitionedAttributeSet) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                cursor = connection.cursor()
                cursor.execute(sql, data)
                connection.commit()
                count = 1
            except Exception as e:
                error = e
        return count, error


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GetCookiesForHostApp()
    sys.exit(app.exec())