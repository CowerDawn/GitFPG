import sys
import os
import requests
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QTextBrowser, QComboBox, QToolBar
)
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QUrl, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt5.QtWebEngineWidgets import QWebEngineView
from git import Repo
import tkinter as tk
from tkinter import simpledialog


class GitFPG(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitFPG")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.layout.addWidget(self.main_widget)

        self.browser_widget = QWidget()
        self.browser_layout = QVBoxLayout(self.browser_widget)
        self.browser = QWebEngineView()
        self.browser_toolbar = QToolBar()
        self.back_button = QPushButton("← Back to GitFPG")
        self.back_button.setFont(QFont("Arial", 12))
        self.back_button.clicked.connect(self.show_main_interface)
        self.browser_toolbar.addWidget(self.back_button)
        self.browser_layout.addWidget(self.browser_toolbar)
        self.browser_layout.addWidget(self.browser)
        self.browser_widget.hide()
        self.layout.addWidget(self.browser_widget)

        self.header_layout = QHBoxLayout()
        self.header_label = QLabel("GitFPG")
        self.header_label.setFont(QFont("Arial", 20))
        self.header_layout.addWidget(self.header_label)

        self.theme_label = QLabel("Theme:")
        self.theme_label.setFont(QFont("Arial", 14))
        self.header_layout.addWidget(self.theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setFont(QFont("Arial", 14))
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        self.header_layout.addWidget(self.theme_combo)

        self.main_layout.addLayout(self.header_layout)

        self.repo_layout = QHBoxLayout()
        self.repo_label = QLabel("Enter Repository Name:")
        self.repo_label.setFont(QFont("Arial", 14))
        self.repo_layout.addWidget(self.repo_label)

        self.repo_input = QLineEdit()
        self.repo_input.setFont(QFont("Arial", 14))
        self.repo_input.setPlaceholderText("repository-name")
        self.repo_input.returnPressed.connect(self.search_repository)
        self.repo_layout.addWidget(self.repo_input)

        self.main_layout.addLayout(self.repo_layout)

        self.search_button = QPushButton("Search Repository")
        self.search_button.setFont(QFont("Arial", 14))
        self.search_button.clicked.connect(self.search_repository)
        self.main_layout.addWidget(self.search_button)

        self.repo_list = QListWidget()
        self.repo_list.setFont(QFont("Arial", 14))
        self.repo_list.itemClicked.connect(self.show_repo_info)
        self.repo_list.itemDoubleClicked.connect(self.open_repo_url)
        self.main_layout.addWidget(self.repo_list)

        self.repo_info_label = QLabel("Repository Info:")
        self.repo_info_label.setFont(QFont("Arial", 14))
        self.main_layout.addWidget(self.repo_info_label)

        self.repo_info_browser = QTextBrowser()
        self.repo_info_browser.setFont(QFont("Arial", 12))
        self.main_layout.addWidget(self.repo_info_browser)

        self.download_button = QPushButton("Download Selected Repository")
        self.download_button.setFont(QFont("Arial", 14))
        self.download_button.clicked.connect(self.download_repository)
        self.main_layout.addWidget(self.download_button)

        self.program_list = QListWidget()
        self.program_list.setFont(QFont("Arial", 14))
        self.main_layout.addWidget(self.program_list)

        self.load_programs()
        self.change_theme()

        self.animations = []

    def load_programs(self):
        self.program_list.clear()
        programs_dir = os.path.expanduser("~/fpg")
        if not os.path.exists(programs_dir):
            os.makedirs(programs_dir)
        for program in os.listdir(programs_dir):
            item = QListWidgetItem(program)
            self.program_list.addItem(item)

    def search_repository(self):
        repo_name = self.repo_input.text().strip()
        if not repo_name:
            QMessageBox.warning(self, "Error", "Please enter a repository name.")
            return

        try:
            url = f"https://api.github.com/search/repositories?q={repo_name}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            self.repo_list.clear()
            if data["total_count"] == 0:
                QMessageBox.information(self, "Info", "No repositories found.")
                return

            for repo in data["items"]:
                item = QListWidgetItem(f"{repo['full_name']} (Stars: {repo['stargazers_count']})")
                item.repo_data = repo
                self.repo_list.addItem(item)

            self.animate_widget(self.repo_list, QSize(0, 0), self.repo_list.size())

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to search repositories: {e}")

    def show_repo_info(self, item):
        repo_data = item.repo_data
        info = f"""
        Name: {repo_data['full_name']}
        Description: {repo_data['description']}
        Stars: {repo_data['stargazers_count']}
        Forks: {repo_data['forks_count']}
        URL: {repo_data['html_url']}
        """
        self.repo_info_browser.setText(info)

        self.animate_widget(self.repo_info_browser, QSize(0, 0), self.repo_info_browser.size())

    def open_repo_url(self, item):
        repo_data = item.repo_data
        url = repo_data["html_url"]
        self.browser.setUrl(QUrl(url))
        self.show_browser_interface()

    def show_browser_interface(self):
        self.main_widget.hide()
        self.browser_widget.show()

    def show_main_interface(self):
        self.browser_widget.hide()
        self.main_widget.show()

    def download_repository(self):
        selected_item = self.repo_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a repository to download.")
            return

        repo_data = selected_item.repo_data
        repo_name = repo_data["full_name"].split("/")[-1]
        repo_url = repo_data["clone_url"]

        programs_dir = os.path.expanduser("~/fpg")
        if not os.path.exists(programs_dir):
            os.makedirs(programs_dir)

        repo_path = os.path.join(programs_dir, repo_name)

        if os.path.exists(repo_path):
            QMessageBox.warning(self, "Error", f"Repository '{repo_name}' is already installed.")
            return

        try:
            Repo.clone_from(repo_url, repo_path)
            QMessageBox.information(self, "Success", f"Repository '{repo_name}' has been downloaded to {repo_path}.")
            self.load_programs()
            self.build_repository(repo_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download repository: {e}")

    def build_repository(self, repo_path):
        try:
            if os.path.exists(os.path.join(repo_path, "Makefile")):
                self.run_sudo_command(["make"], repo_path)
                self.run_sudo_command(["make", "install"], repo_path)
            elif os.path.exists(os.path.join(repo_path, "build")):
                self.run_command(["chmod", "+x", "build"], repo_path)
                self.run_command(["./build"], repo_path)
            elif os.path.exists(os.path.join(repo_path, "build.sh")):
                self.run_command(["chmod", "+x", "build.sh"], repo_path)
                self.run_command(["./build.sh"], repo_path)
            else:
                QMessageBox.warning(self, "Warning", "No known build system detected.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to build repository: {e}")

    def run_command(self, command, cwd):
        try:
            result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
            QMessageBox.information(self, "Success", f"Command executed successfully:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Command failed:\n{e.stderr}")

    def run_sudo_command(self, command, cwd):
        try:
            password = self.get_password()
            if not password:
                return

            command = ["sudo", "-S"] + command
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=password + "\n")

            if process.returncode == 0:
                QMessageBox.information(self, "Success", f"Command executed successfully:\n{stdout}")
            else:
                QMessageBox.critical(self, "Error", f"Command failed:\n{stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute command: {e}")

    def get_password(self):
        root = tk.Tk()
        root.withdraw()
        password = simpledialog.askstring("Password", "Enter your password:", show="*")
        return password

    def change_theme(self):
        theme = self.theme_combo.currentText()
        if theme == "Dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #2E3440; color: #D8DEE9; }
                QLabel { color: #D8DEE9; }
                QPushButton { background-color: #5E81AC; color: #D8DEE9; border-radius: 5px; padding: 5px; }
                QPushButton:hover { background-color: #81A1C1; }
                QLineEdit { background-color: #4C566A; color: #D8DEE9; border-radius: 5px; padding: 5px; }
                QListWidget { background-color: #4C566A; color: #D8DEE9; border-radius: 5px; padding: 5px; }
                QTextBrowser { background-color: #4C566A; color: #D8DEE9; border-radius: 5px; padding: 5px; }
                QComboBox { background-color: #5E81AC; color: #D8DEE9; border-radius: 5px; padding: 5px; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #FFFFFF; color: #000000; }
                QLabel { color: #000000; }
                QPushButton { background-color: #4CAF50; color: #FFFFFF; border-radius: 5px; padding: 5px; }
                QPushButton:hover { background-color: #81C784; }
                QLineEdit { background-color: #F1F1F1; color: #000000; border-radius: 5px; padding: 5px; }
                QListWidget { background-color: #F1F1F1; color: #000000; border-radius: 5px; padding: 5px; }
                QTextBrowser { background-color: #F1F1F1; color: #000000; border-radius: 5px; padding: 5px; }
                QComboBox { background-color: #4CAF50; color: #FFFFFF; border-radius: 5px; padding: 5px; }
            """)

    def animate_widget(self, widget, start_size, end_size):
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        animation.setStartValue(start_size)
        animation.setEndValue(end_size)
        animation.start()
        self.animations.append(animation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitFPG()
    window.show()
    sys.exit(app.exec_())
