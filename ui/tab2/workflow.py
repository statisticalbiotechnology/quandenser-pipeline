from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

class workflow(QWebEngineView):

    def __init__(self):
        super(workflow,self).__init__(parent = None)
        self.stderr_backup = None
        self.settings().setAttribute(QWebEngineSettings.ErrorPageEnabled, False)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, False)
        html_file = open("ui/tab2/full.html")
        self.setHtml(html_file.read())


    def nativeEvent(self,event):
        pass
