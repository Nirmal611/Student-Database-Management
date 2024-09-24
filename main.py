import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, \
    QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QToolBar, QStatusBar, QComboBox, \
    QMessageBox
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Management System')
        self.setMinimumSize(400,300)
        file_menu_item = self.menuBar().addMenu('&File')
        help_menu_item = self.menuBar().addMenu('&Help')
        edit_menu_item = self.menuBar().addMenu('&Edit')

        about = QAction('About',self)
        help_menu_item.addAction(about)
        about.triggered.connect(self.show_about)

        add_student = QAction(QIcon('icons/add.png'),'Add Student',self)
        add_student.triggered.connect(self.insert)
        file_menu_item.addAction(add_student)

        search_student = QAction(QIcon('icons/search.png'),'Search',self)
        search_student.triggered.connect(self.search)
        edit_menu_item.addAction(search_student)

        ##Create a toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        toolbar.addAction(add_student)
        toolbar.addAction(search_student)
        self.addToolBar(toolbar)

        ##Create a Status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('Id','Name','Course','Phone'))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        self.load_data()
        self.table.cellClicked.connect(self.cell_clicked)

    def show_about(self):
        ab = AboutDialogBox()
        ab.exec()

    def load_data(self):
        connection = sqlite3.connect("example.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_num , row_data in enumerate(result):
            self.table.insertRow(row_num)
            for column_num , data in enumerate(row_data):
                self.table.setItem(row_num, column_num, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = AddStudentDialog()
        dialog.exec()

    def search(self):
        search = SearchStudentDialog()
        search.exec()

    def cell_clicked(self):
        children = self.findChildren(QPushButton)
        for child in children:
            self.statusbar.removeWidget(child)

        edit_button = QPushButton('Edit Record')
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton('Delete Record')
        delete_button.clicked.connect(self.delete)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def edit(self):
        edit = StatusBarEdit()
        edit.exec()

    def delete(self):
        delete = StatusBarDelete()
        delete.exec()


class AboutDialogBox(QMessageBox):
    def __init__(self):
        super().__init__()
        message = "This simple app was created to maintain student details , feel free to edit to hold different information and use it !"
        self.setWindowTitle('About')
        self.setText(message)


class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Add Student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        self.student_course = QComboBox()
        self.student_course.addItems(['Biology','Computer Science','Commerce'])
        self.student_phone = QLineEdit()
        self.student_phone.setPlaceholderText('Phone Number')
        add_student_button = QPushButton('Add Student')
        add_student_button.clicked.connect(self.insert_student)

        layout.addWidget(self.student_name)
        layout.addWidget(self.student_course)
        layout.addWidget(self.student_phone)
        layout.addWidget(add_student_button)
        self.setLayout(layout)

    def insert_student(self):
        name,course,phone = (self.student_name.text(),self.student_course.currentText(),self.student_phone.text())
        print(self.student_course.currentText())
        connection = sqlite3.connect("example.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM students")
        result = cursor.fetchall()
        result = list(result)
        y = []
        for x in result:
            y.append(int(x[0]))
        new_id = 0
        for i in range(1, max(y) + 1):
            if i not in y:
                new_id = i
                break

        print(new_id)
        cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?)",(new_id,name,course,phone))
        connection.commit()
        connection.close()

        #Refresh the table
        student.load_data()


class SearchStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setWindowTitle('Search')
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText('Enter a name to Search')
        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_student_name)
        layout.addWidget(self.search_name)
        layout.addWidget(search_button)
        self.setLayout(layout)

    def search_student_name(self):
        name = self.search_name.text()
        connection = sqlite3.connect('example.db')
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?",(name,))
        rows = list(result)
        print(rows)
        items = student.table.findItems(name,Qt.MatchFlag.MatchFixedString)
        for item in items :
            student.table.item(item.row(),1).setSelected(True)

        cursor.close()
        connection.close()


class StatusBarEdit(QDialog):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        index = student.table.currentRow()
        self.student_id = student.table.item(index, 0).text()
        old_name = student.table.item(index,1).text()
        old_phone = student.table.item(index,3).text()

        self.new_name = QLineEdit(old_name)
        self.new_name.setPlaceholderText('name')

        self.new_course = QComboBox()
        self.new_course.addItems(['Biology', 'Computer Science', 'Commerce'])

        self.new_phone = QLineEdit(old_phone)
        self.new_phone.setPlaceholderText('phone')

        edit_button = QPushButton('Update')
        edit_button.clicked.connect(self.update_student)

        layout.addWidget(self.new_name)
        layout.addWidget(self.new_course)
        layout.addWidget(self.new_phone)
        layout.addWidget(edit_button)
        self.setLayout(layout)

    def update_student(self):
        print(self.new_name.text(), self.new_course.currentText(), self.new_phone.text(), self.student_id)
        connection = sqlite3.connect('example.db')
        cursor = connection.cursor()
        result = cursor.execute("UPDATE students SET name = ?, course = ?, phone = ? WHERE id = ?",(self.new_name.text(),self.new_course.currentText(),self.new_phone.text(),self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        student.load_data()


class StatusBarDelete(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        warning_label = QLabel('Do You want to delete this students Record ?')
        yes_button = QPushButton('Yes')
        no_button = QPushButton('No')
        no_button.clicked.connect(self.close)
        yes_button.clicked.connect(self.delete_record)
        layout.addWidget(warning_label)
        layout.addWidget(yes_button)
        layout.addWidget(no_button)
        self.setLayout(layout)

    def delete_record(self):
        index = student.table.currentRow()
        student_id = student.table.item(index, 0).text()
        connection = sqlite3.connect('example.db')
        cursor = connection.cursor()
        result = cursor.execute("DELETE FROM students WHERE id = ?",(student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        student.load_data()
        self.close()
        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle('Success')
        confirmation_message.setText('The selected record was deleted successfylly!')
        confirmation_message.exec()


app = QApplication(sys.argv)
student = MainWindow()
student.show()
sys.exit(app.exec())