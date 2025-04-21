import screeninfo
import os
import requests

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction
from src.Ui_MainWindow import Ui_MainWindow
from Windows.CriticalWindow import CriticalWindow
from Windows.SuccessWindow import SuccessWindow
from Windows.AboutWindow import AboutWindow

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        size = screeninfo.get_monitors()[0]
        WIDTH, HEIGHT = 800, 600
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setGeometry(int(size.width / 2 - (WIDTH / 2)), int(size.height / 2 - (HEIGHT / 2)), WIDTH, HEIGHT)
        self.setFixedSize(WIDTH, HEIGHT)
        self.source_file = ""
        self.destination_file = ""
        self.url = "http://46.30.47.219:7878/demarshalize"
        self.fail = False
        
        self.ui.selectFile_btn.clicked.connect(self.open_file)
        self.ui.decompile_btn.clicked.connect(self.decompile)
        self.about_action = QAction("О программе", self)
        self.about_action.triggered.connect(self.show_about)
        self.ui.menuBar.addAction(self.about_action)

    def show_about(self):
        about_text = """
        <center>
        <h3>PYC-Decompiler</h3>
        <p>Версия: 1.0</p>
        <p>Программа для декомпиляции Python .pyc файлов</p>
        <p><a href="https://github.com/Qurclinc">Автор</a></p>
        <p>© 2025 Все права защищены</p>
        </center>
        """
        title = "О программе"
        AboutWindow(title, about_text).exec()


    def send_file(self):
        try:
            with open(self.source_file, "rb") as pyc:
                files = {"file": (self.source_file, pyc, "application/octet-stream")}
                response = requests.post(self.url, files=files)
                return response
        except Exception as ex:
            self.fail = True
            return "abort"
    
    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Python Compiled Files (*.pyc)")
        if filepath:
            self.source_file = os.path.abspath(filepath)
            # self.ui.textspace_edit.setPlainText("\n".join(line.strip() for line in f.readlines()))
            self.ui.filename_label.setText(f"Current file: {os.path.basename(self.source_file)}")

    def get_destination(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Choose file", "Output/output.py", "Python Files (*.py)")
        if filepath:
            self.destination_file = os.path.abspath(f"{filepath}") 

    def decompile(self):
        strings = ""
        if (not(self.source_file)):
            CriticalWindow("Decompilation error", "Select input file first!").exec()
        else:
            self.get_destination()
            response = self.send_file()
            if self.fail:
                CriticalWindow("Decompilation error", "Could not decompile your file!").exec()
                self.fail = False
                return
            if response.status_code == 200:
                with open(self.destination_file, "wb") as f:
                    f.write(response.content)
                    self.ui.filename_label.setText(f"Current file: {os.path.basename(self.destination_file)}")
                    SuccessWindow("Succes", "File decompiled successfully!").exec()
                with open(self.destination_file, "r") as f:
                    strings = ''.join(line for line in f.readlines()[4:])
                    self.ui.textspace_edit.setPlainText(strings)
                with open(self.destination_file, "w") as f:
                    f.writelines(strings)
            else:
                CriticalWindow("Decompilation error", "Could not decompile your file!").exec()
                return


