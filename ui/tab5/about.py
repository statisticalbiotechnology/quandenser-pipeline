from PySide2.QtWebEngineWidgets import QWebEngineView

class about(QWebEngineView):

    def __init__(self):
        super(about,self).__init__(parent = None)
        html_file = open("ui/tab5/about.html")
        self.setHtml(html_file.read())
