import sys
from PySide2.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QMenu, QAction
from PySide2.QtGui import QColor, QKeySequence, QClipboard
from PySide2 import QtCore
import os
from difflib import SequenceMatcher

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser

class batch_file_viewer(QTableWidget):
    def __init__(self, nf_settings_path):
        super(batch_file_viewer,self).__init__(parent = None)
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(nf_settings_path)
        self.setRowCount(20)
        self.setColumnCount(2)
        # Fill all places so there are no "None" types in the table
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item = QTableWidgetItem()
                item.setText('')
                self.setItem(row, column, item)

        self.original_background = item.background()

        self.cellChanged.connect(self.check_cell)  # Needs to be after "filling for loop" above
        self.header = self.horizontalHeader()
        self.header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.setHorizontalHeaderLabels(["MS files", "Label"])

        self.header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header.customContextMenuRequested.connect( self.right_click_menu )

    def right_click_menu(self, point):
        column = self.header.logicalIndexAt(point.x())
        # show menu about the column if column 1
        if column == 1:
            menu = QMenu(self)
            menu.addAction('Auto label', self.auto_label)
            menu.popup(self.header.mapToGlobal(point))

    def keyPressEvent(self, event):
        """Add functionallity to keyboard"""
        if event.key() == 16777223:
            for item in self.selectedItems():
                item.setText('')
        elif event.key() == 16777221 or event.key() == 16777220:  # *.221 is right enter
            if len(self.selectedIndexes()) == 0:  # Quick check if anything is selected
                pass
            else:
                index = self.selectedIndexes()[0]  # Take last
                self.setCurrentCell(index.row() + 1, index.column())
        super().keyPressEvent(event)  # Propagate to built in methods

    def check_cell(self, row, column):
        """Triggered when cell is changed"""
        self.blockSignals(True)
        self.pick_color(row, column)
        self.blockSignals(False)

    def pick_color(self, row, column):
        """Triggered by check_cell"""
        msfile = self.item(row, 0)
        label = self.item(row, 1)
        if label is None or msfile is None:  # NOTE: item == None will give NotImplementedError. Must use "is"
            return  # This might remove some weird errors in the future

        # Ms file
        if not os.path.isfile(msfile.text()):
            msfile.setForeground(QColor('red'))
        elif msfile.text().split('.')[-1] == "mzML":
            msfile.setForeground(QColor(0,255,150))
        elif msfile.text().split('.')[-1] != "mzML":
            msfile.setForeground(QColor(30,150,255))

        workflow = self.nf_settings_parser.get('params.workflow')
        if msfile.text() == '':
            label.setBackground(self.original_background)
            label.setForeground(QColor('white'))
        elif label.text() == '' and os.path.isfile(msfile.text()) and workflow == "Full":
            label.setBackground(QColor('red'))
        elif os.path.isfile(msfile.text()) and label.text() != '':
            label.setBackground(self.original_background)
            label.setForeground(QColor(0,255,150))
        else:
            label.setBackground(self.original_background)
            label.setForeground(QColor('white'))

    def update(self):
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                self.pick_color(row, column)

    def auto_assign(self, file):
        """Triggered when using file chooser button"""
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item.text() == '':
                self.item(row, 0).setText(file)
                return

        # If we get here, add more rows
        self.blockSignals(True)
        item = QTableWidgetItem()
        item.setText(file)
        self.setRowCount(self.rowCount() + 1)
        self.setItem(row + 1, 0, item)    # Note: new rowcount here
        label = QTableWidgetItem()
        label.setText('')
        self.setItem(row + 1, 1, label)
        self.pick_color(row + 1, 0)
        self.pick_color(row + 1, 1)
        self.blockSignals(False)

    def auto_label(self):
        all_labels = []
        # Get current labels, we want unique
        for row in range(self.rowCount()):
            label = self.item(row, 1).text()
            all_labels.append(label)

        # Assign labels
        current_label = [65]
        for row in range(self.rowCount()):
            label = self.item(row, 1).text()
            file = self.item(row, 0).text()
            if label == '' and file != '':
                while True:
                    added_label = ''.join([chr(i) for i in current_label])
                    if added_label in all_labels:
                        current_label[-1] += 1
                        if current_label[-1] >= 122:  # aka "z"
                            current_label.append(65)  # aka "A"
                    else:
                        break
                self.item(row, 1).setText(added_label)
                current_label[-1] += 1
                if current_label[-1] >= 122:  # aka "z"
                    current_label.append(65)  # aka "A"
