from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl
import os

class about(QWebEngineView):

    def __init__(self):
        super(about,self).__init__(parent = None)
        html_file = open("ui/tab5/about.html", 'r', encoding='utf-8')
        #self.setHtml(html_file.read())
