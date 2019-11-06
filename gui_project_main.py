import sys
import os
import subprocess

from gui_project import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QTreeWidgetItemIterator, QFileDialog, QCheckBox, QMessageBox
from PyQt5 import QtCore, QtWidgets, QtGui
from subprocess import Popen, PIPE


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Gui Python Project')
        self.ui.select_test_button.clicked.connect(self.select_test)
        self.ui.run_test_button.clicked.connect(self.run_checked_files)
        self.ui.logs_button.clicked.connect(self.log_output)
        self.ui.stop_button.clicked.connect(self.stop_run)
        self.ui.clear_logs_button.clicked.connect(self.clear_logs)
        self.ui.treeWidget_select_test.itemClicked.connect(self.check_status)
        self.ui.select_all_button.clicked.connect(self.select_all_checkbox)
        self.ui.deselect_all_button.clicked.connect(self.deselect_all_checkbox)
        self.ui.action_Run.triggered.connect(self.run_checked_files)
        self.ui.action_Stop.triggered.connect(self.stop_run)
        self.ui.actionSelect_test.triggered.connect(self.select_test)
        self.ui.actionShow_logs.triggered.connect(self.log_output)
        self.ui.actionClear_logs.triggered.connect(self.clear_logs)
        self.ui.deselect_all_button.setEnabled(False)
        self.ui.stop_button.setEnabled(False)
        self.ui.select_all_button.setEnabled(False)
        self.run_subprocess = ""  # the Popen
        self.list_files = []      # list of test that were checked
        self.tree_files = []      # list of all files in the tree
        self.kill = []            # list of all process id's of tests that chosen to run
        self.setWindowIcon(QtGui.QIcon("icon_for_app.png"))

    # select test with 'select test' button: open the dialog box and choose a folder, input the chosen in the treeView
    def select_test(self):
        self.folder_name = QFileDialog.getExistingDirectory(self, "Select Folder", "C:\CODE\BOOTCAMP")
        print(self.folder_name)
        for file in os.listdir(self.folder_name):
            if file.endswith(".js") or file.endswith(".py"):
                item = QTreeWidgetItem(self.ui.treeWidget_select_test, [file])
                item.setCheckState(0, QtCore.Qt.Unchecked)
                self.ui.select_all_button.setEnabled(True)
                self.tree_files.append(file)
        # print(self.tree_files)        #print all files in the widget tree

    # check the status of the checkbox buttons
    def check_status(self):
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget_select_test)
        item = iterator.value()
        while iterator.value():
            if item.checkState(0):
                self.ui.select_all_button.setEnabled(False)
                self.ui.deselect_all_button.setEnabled(True)
            iterator += 1

    # press run button: iterate over the selected filed in the chosen folder and run the checked tests
    def run_checked_files(self):
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget_select_test)
        while iterator.value():
            item = iterator.value()
            if item.checkState(0):
                self.list_files.append(item.text(0))
            iterator += 1
        # print(self.list_files)  # print the list of the files that has checked boxes
        self.check_status()
        self.open_popen()
        self.ui.stop_button.setEnabled(True)
        self.ui.run_test_button.setEnabled(False)
        self.ui.treeWidget_select_test.setEnabled(False)
        self.ui.select_test_button.setEnabled(False)
        self.ui.select_all_button.setEnabled(False)
        self.ui.deselect_all_button.setEnabled(False)

    def open_popen(self):
        a = ''
        for i in range(0, len(self.list_files)):
            if i != 0:
                a += f" && node {self.folder_name}/{self.list_files[i]}"
            else:
                a += f"node {self.folder_name}/{self.list_files[i]}"
        self.run_subprocess = Popen(a, stdout=PIPE, stderr=PIPE, shell=True)
        self.kill.append({"id": self.run_subprocess.pid})
        # print(self.run_subprocess.pid)         # print the id of the process

    # stop the test run
    def stop_run(self):
        self.ui.run_test_button.setEnabled(True)
        self.ui.treeWidget_select_test.setEnabled(True)
        self.ui.select_test_button.setEnabled(True)
        try:
            message_question = "Are you sure you want to stop? \n If you click 'OK' it will abort all tasks."
            if_ok = QMessageBox.question(self, 'Are you sure?', message_question, QMessageBox.Ok, QMessageBox.Cancel)
            # if_ok(QMessageBox.defaultButton(QMessageBox.Cancel))
            if if_ok == QMessageBox.Ok:
                for process in self.kill:
                    subprocess.Popen("taskkill /F /T /PID %i" % self.run_subprocess.pid, shell=True)
                    self.ui.textEdit.setText('Stopped running tests')
                    print('stopped running tests')
                    self.ui.stop_button.setEnabled(False)
            else:
                self.ui.treeWidget_select_test.setEnabled(False)
                self.ui.run_test_button.setEnabled(False)
                self.ui.select_test_button.setEnabled(False)
                self.check_status()
        except:
            print("Couldn't stop the process")

    # select all checkboxes
    def select_all_checkbox(self):
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget_select_test)
        while iterator.value():
            item = iterator.value()
            item.setCheckState(0, QtCore.Qt.Checked)
            iterator += 1
            self.ui.select_all_button.setEnabled(False)
            self.ui.deselect_all_button.setEnabled(True)

    # deselect all processes
    def deselect_all_checkbox(self):
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget_select_test)
        while iterator.value():
            item = iterator.value()
            item.setCheckState(0, QtCore.Qt.Unchecked)
            iterator += 1
            self.ui.select_all_button.setEnabled(True)
            self.ui.deselect_all_button.setEnabled(False)
            if item.setCheckState(2, QtCore.Qt.Checked):
                self.ui.select_all_button.setEnabled(False)

    # press on logs button: input all logs of the tests running in the textEdit box
    def log_output(self):
        log_file = open(f"{self.folder_name}/log/log.log")
        read_log = log_file.read()
        # print(read_log)   # print all the logs
        self.ui.textEdit.setText(read_log)

    # clear the log screen
    def clear_logs(self):
        self.ui.textEdit.setText("")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
