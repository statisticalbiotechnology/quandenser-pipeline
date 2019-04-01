from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QPushButton
from PySide2.QtCore import QUrl
import os

class about(QWebEngineView):

    def __init__(self):
        super(about,self).__init__(parent = None)
        self.current_dir = os.getcwd().replace('\\', '/')  # Windows fix
        #html_file = open("ui/tab5/about.html", 'r', encoding='utf-8')
        #self.setHtml(html_file.read())  # THIS WILL NOT LOAD IMAGES
        self.urlChanged.connect(self.check_url)
        self.return_button = QPushButton()
        self.return_button.setText('BACK TO ABOUT PAGE')
        self.return_button.clicked.connect(self.return_to_about)
        self.return_button.setStyleSheet('QPushButton {color: #00ff96;}')
        self.load(QUrl.fromLocalFile(f"{self.current_dir}/tab5/about.html"))

    def check_url(self, url):
        if "tab5/about.html" in str(url):
            pass
        else:
            parent_layout = self.parentWidget().layout()
            parent_layout.addWidget(self.return_button)

    def return_to_about(self):
        self.load(QUrl.fromLocalFile(f"{self.current_dir}/tab5/about.html"))
        self.return_button.setParent(None)
