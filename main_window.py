#!usr/bin/env python

""" App's main GUI window. """

import sys

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget,
                             QVBoxLayout, QApplication,
                             QLabel, QPushButton, QFormLayout,
                             QMessageBox)
from helper_modules import helper_functions

from api_communicator import WorkerThread

MSG_BOX_FONT = QFont('Italics', 13)
BUTTONS_FONT = QFont('Times', 13)
SHEET_JSON_FILE = 'g_sheet_info.json'

json_file_content = helper_functions.json_file_loader(file_name=SHEET_JSON_FILE)


class MixWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MixWindow, self).__init__(parent)
        self.setWindowTitle(json_file_content.get('window_title', 'MIX'))
        self.resize(300, 110)
        self.central_wid = QWidget()
        self.win_layout = QVBoxLayout()

        self.central_wid.setLayout(self.win_layout)
        self.setCentralWidget(self.central_wid)

        self._add_wids()
        self._create_btns_connection()

    def _create_btns_connection(self):
        self.close_win_btn.clicked.connect(self._close_btn_responder)
        self.generate_man_btn.clicked.connect(self._threadManager)

    def _threadManager(self):
        """ Manages the WorkerThread used in this algorithm.
        This thread is used when user clicks on Generare Manuale button. """

        self._label_thread = QThread()
        self._worker_thread = WorkerThread()
        # Move the worker thread to a separate thread
        self._worker_thread.moveToThread(self._label_thread)

        # Connect thread to the method that communicates with Google sheets
        self._label_thread.started.connect(self._worker_thread.api_communicator)

        # Update app's states
        self._worker_thread.progress.connect(self._updateAppStateWhileBusy)
        self._worker_thread.finished.connect(self._updateAppStateWhileDone)
        self._worker_thread.unfinished.connect(self._updateAppStateWhileDone)
        self._worker_thread.finished.connect(self._communicateSuccess)
        self._worker_thread.unfinished.connect(self._communicateFailure)

        # Clean up after the operation is completed
        self._worker_thread.finished.connect(self._label_thread.quit)
        self._worker_thread.unfinished.connect(self._label_thread.quit)
        self._worker_thread.finished.connect(self._label_thread.deleteLater)
        self._worker_thread.unfinished.connect(self._label_thread.deleteLater)

        # Run the thread
        self._label_thread.start()

    def _communicateFailure(self):
        """ Communicates to user if the generation of manual operation failed. """
        helper_functions.output_communicator(
            msg_box_font=MSG_BOX_FONT,
            window_title=json_file_content.get('window_title', 'MIX'),
            output_type=False,
            button_pressed=self.generate_man_btn.text(),
        )

    def _communicateSuccess(self):
        """ Communicates to user the successful generation of manual. """
        helper_functions.output_communicator(msg_box_font=MSG_BOX_FONT,
                                             window_title=json_file_content.get('window_title', 'MIX'),
                                             output_type=True,
                                             button_pressed=self.generate_man_btn.text())

    def _updateAppStateWhileDone(self):
        """ Updates the app's GUI state after it's done generating manual. """
        self.generate_man_btn.setEnabled(True)
        self.close_win_btn.setEnabled(True)

    def _updateAppStateWhileBusy(self):
        """ Updates the app's GUI state while it is busy blocking some buttons. """
        self.generate_man_btn.setEnabled(False)
        self.close_win_btn.setEnabled(False)

    def _close_btn_responder(self):
        user_choice = helper_functions.ask_before_close(
            msg_box_font=MSG_BOX_FONT,
            window_tile=json_file_content.get('window_title', 'MIX'),
        )
        if user_choice == QMessageBox.Yes:
            self.close()
        else:
            pass

    def _add_wids(self):
        """ Adds the necessary widgets and layouts. """
        user_name = helper_functions.get_user_name()
        self.greetings = QLabel(f'<h1> Ciao {user_name}')
        self.win_layout.addWidget(self.greetings)

        # Buttons
        self.generate_man_btn = QPushButton('Generare Manuale')
        self.generate_man_btn.setFont(BUTTONS_FONT)
        self.generate_man_btn.setStyleSheet('color: blue')

        self.close_win_btn = QPushButton('Chiudi')
        self.close_win_btn.setStyleSheet('color: red')
        self.close_win_btn.setFont(BUTTONS_FONT)

        btns_list = [self.generate_man_btn, self.close_win_btn]
        self.form_layout = QFormLayout()

        for button_index, button_name in enumerate(btns_list):
            btn_label = f'{button_index + 1}.'
            self.form_layout.addRow(btn_label, button_name)
        self.win_layout.addLayout(self.form_layout)


def main():
    app = QApplication(sys.argv)
    window = MixWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    pass
