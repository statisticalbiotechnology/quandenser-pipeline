import sys
from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QColor
import os
from difflib import SequenceMatcher


class batch_file_viewer(QTextEdit):
    def __init__(self):
        super(batch_file_viewer,self).__init__(parent = None)
        self.textChanged.connect(self.check_text)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.append("/media/storage/timothy/MSfiles/mzML/A1.mzML\ttab")
        self.append("/media/storage/timothy/MSfiles/mzML/A1.mzML")
        self.append("/media/storage/timothy/MSfiles/mzML/A1.mzML blankspace")
        self.append("/notafile/test.txt\tnotafile")

    def check_text(self):
        self.blockSignals(True)
        all_txt = str(self.toPlainText())  # Copy, dont use
        all_txt = all_txt.split('\n')
        self.clear()
        for txt in all_txt:
            self.pick_color(txt)
            self.append(txt)
        self.blockSignals(False)

    def pick_color(self, txt):
        txt = txt.split('\t')
        if len(txt) == 1:
            self.setTextColor(QColor("red"))
        elif len(txt) == 2:
            if not os.path.isfile(txt[0]):
                self.setTextColor(QColor("red"))
            elif len(txt[1]) == 0:
                self.setTextColor(QColor("red"))
            elif txt[0].split('.')[-1] != "mzML":  # If extension != mzML
                self.setTextColor(QColor("blue"))
            else:
                self.setTextColor(QColor("green"))  # Check if path
        else:
            self.setTextColor(QColor("red"))

    def auto_assign(self, txt):
        clean_txt = self.clean_path(txt)
        print(clean_txt)
        all_txt = str(self.toPlainText())  # Copy, dont use
        all_txt = all_txt.split('\n')
        assigned_labels = [i[-1] for i in all_txt if len(i.split('\t'))==2]
        if len(all_txt) == 0:
            self.append(txt + '\t' + 'A')
            return
        for line in all_txt:
            clean_line = self.clean_path(line)
            similarity = SequenceMatcher(None, clean_line, clean_txt).ratio()
            if similarity > 0.8 and len(line.split('\t')) == 2:  # Prevent error if assigned yourself
                label = line.split('\t')[-1]
                self.append(txt + '\t' + label)
                return
        # If we get here, the script has not found a similar match
        char_index = 65
        while True:
            if chr(char_index) in assigned_labels:
                char_index += 1
            else:
                label = chr(char_index)  # Make as chr
                break
        self.append(txt + '\t' + label)

    def clean_path(self, txt):
        txt = txt.split('\t')[0]  # Get path
        txt = txt.split(os.sep)[-1]  # Get filename
        txt = txt.split('.')[0]  # Ignore extension
        txt = ''.join([i for i in txt if 65<=ord(i)<=122])  # Remove all non-letter chars + digits
        return txt
