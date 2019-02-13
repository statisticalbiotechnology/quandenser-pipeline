from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

class workflow(QWebEngineView):

    def __init__(self):
        super(workflow,self).__init__(parent = None)
        self.page = page()
        self.setPage(self.page)
        self.page.load_page()  # Must be in this order
        self.setZoomFactor(1)  # Title size

class page(QWebEnginePage):

    def __init__(self):
        super(page,self).__init__(parent = None)

    def load_page(self):
        html_file = open("ui/tab2/flowchart.html", encoding='utf-8')
        self.setHtml(html_file.read())

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if not "a parser-blocking" in message and level == 2:  # Filter script injection erros
            print(level, message, lineNumber, sourceId)
