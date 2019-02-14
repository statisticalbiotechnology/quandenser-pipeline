from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl
import os

class about(QWebEngineView):

    def __init__(self):
        super(about,self).__init__(parent = None)
        current_dir = os.getcwd().replace('\\', '/')  # Windows fix
        #html_file = open("ui/tab5/about.html", 'r', encoding='utf-8')
        #self.setHtml(html_file.read())  # THIS WILL NOT LOAD IMAGES
        self.load(QUrl.fromLocalFile(f"{current_dir}/tab5/about.html"))
