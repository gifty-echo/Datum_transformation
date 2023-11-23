import csv
import sys
import os
import geopandas as gp
import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, \
    QPushButton, QComboBox, QLabel, QFileDialog, QMessageBox, QApplication
from shapely.geometry import Point

COLUMN_WIDTH = 150
if not os.path.exists("data"):
    os.mkdir("./data")

class InstructionScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.icon = QIcon("Maps_icon-icons.com_76888.ico")
        self.setWindowIcon(self.icon)
        # set window properties
        self.setWindowTitle("Manual")
        self.setStyleSheet("""
            background-color: #1f1f1f;
            color: #FFFFFF;
            font-size: 16px;
        """)

        # create layout
        layout = QVBoxLayout()

        # add title label
        title_label = QLabel("Welcome to Coordinate Converter")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # add instructions
        instruction_label = QLabel("Please follow the instructions below:")
        layout.addWidget(instruction_label)

        # add numbered instructions
        instruction_1_label = QLabel(

            "1. Depending on what coordinate system(Projected or Geographic) you're working on, \n"
            "     X is for Longitude or Easting"
            " and Y is Latitude or Northing")
        instruction_2_label = QLabel("2. X on the Left column, Y on the Right.")
        instruction_4_label = QLabel(
            "4. You can import the CSV file that contains coordinates or enter the coordinates in the table.\n"
            "    You can view and edit from the tables")
        instruction_3_label = QLabel("3. Including column headers in the CSV files is not necessary.")
        layout.addWidget(instruction_1_label)
        layout.addWidget(instruction_2_label)
        layout.addWidget(instruction_3_label)
        layout.addWidget(instruction_4_label)

        # add button to close instruction screen
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("""
            background-color: #FFFFFF;
            color: #1f1f1f;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
            padding: 5px 10px;
            margin-top: 20px;
        """)
        ok_button.clicked.connect(self.close)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        # set layout
        self.setGeometry(250, 250, 150, 150)

        self.setLayout(layout)


class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self._filepath = None
        self.column_names = None
        self.dst_filepath = "data/transformed.csv"
        self.data_to_be_transformed = "data/data_to_be_transformed.csv"
        self.gdf_transformed = None

        self.initUI()

    def initUI(self):
        # Set dark theme stylesheet
        self.setStyleSheet("background-color: #1f1f1f; color: #d9d9d9;")
        self.icon = QIcon("Maps_icon-icons.com_76888.ico")
        self.setWindowIcon(self.icon)
        # Create left table
        self.left_table = QTableWidget()
        self.left_table.setColumnCount(3)
        self.left_table.setHorizontalHeaderLabels(["X", "Y", "L"])
        self.left_table.setColumnWidth(0, 10000)
        # Add some empty cells
        self.left_table.setRowCount(100)
        for i in range(100):
            for j in range(3):
                self.left_table.setItem(i, j, QTableWidgetItem(""))
        self.left_table.resizeColumnsToContents()

        # Create right table
        self.right_table = QTableWidget()
        self.right_table.setColumnCount(3)
        self.right_table.setHorizontalHeaderLabels(["X", "Y", "L"])
        # Add some empty cells
        self.right_table.setRowCount(100)
        for i in range(100):
            for j in range(3):
                self.right_table.setItem(i, j, QTableWidgetItem(""))
        self.right_table.resizeColumnsToContents()

        # Set default column width to 100 pixels

        for i in range(self.left_table.columnCount()):
            self.left_table.setColumnWidth(i, COLUMN_WIDTH)

        for i in range(self.right_table.columnCount()):
            self.right_table.setColumnWidth(i, COLUMN_WIDTH)
        # Create import, clear, and transform buttons for left table
        left_import_button = QPushButton("Import")
        left_clear_button = QPushButton("Clear")
        transform_button = QPushButton("Transform")
        transform_button.clicked.connect(self.transform_to)
        left_import_button.clicked.connect(lambda: self.importCsvFile(self.left_table))
        left_clear_button.clicked.connect(self.left_table.clear)

        # Create export and clear buttons for right table
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.destination_path)
        right_clear_button = QPushButton("Clear")
        right_clear_button.clicked.connect(self.right_table.clear)

        # Create combobox and label for left table
        left_label = QLabel("EPSG:")
        self.left_combobox = QComboBox()
        self.left_combobox.addItem("32630")
        # self.left_combobox.addIztem("32630: WGS 84/UTM ZONE 30N")
        self.left_combobox.addItem("4326")
        # self.left_combobox.addItem("4326: WGS 84")
        self.left_combobox.addItem("2136")
        # self.left_combobox.addItem("2136: Ghana National Grid")

        # Create combobox and label for right table
        right_label = QLabel("EPSG:")
        self.right_combobox = QComboBox()
        # self.right_combobox.addItem("32630: WGS 84/UTM ZONE 30N")
        self.right_combobox.addItem("32630")
        # self.right_combobox.addItem("4326: WGS 84")
        self.right_combobox.addItem("4326")
        # self.right_combobox.addItem("2136: Ghana National Grid")
        self.right_combobox.addItem("2136")

        # Create arrow button
        arrow_button = QPushButton("➡")
        arrow_button.setFlat(True)
        arrow_button.setFixedWidth(20)

        # Create layouts
        left_layout = QVBoxLayout()
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.left_combobox)
        left_layout.addWidget(self.left_table)
        left_layout.addWidget(left_import_button)
        left_layout.addWidget(left_clear_button)
        left_layout.addWidget(transform_button)

        right_layout = QVBoxLayout()
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.right_combobox)
        right_layout.addWidget(self.right_table)
        right_layout.addWidget(export_button)
        right_layout.addWidget(right_clear_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addWidget(arrow_button)
        main_layout.addLayout(right_layout)

        self.column_names = []
        for i in range(self.left_table.columnCount()):
            self.column_names.append(self.left_table.horizontalHeaderItem(i).text())
        # Set the main layout of the window
        self.setLayout(main_layout)

        # Set the window properties
        self.setWindowTitle("Coordinate Converter")
        self.setGeometry(100, 100, 1000, 650)
        self.show()

    def clearTable(self, table):
        # Loop through all the cells in the table and set their text to an empty string
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                table.setItem(i, j, QTableWidgetItem(""))

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, value):
        self._filepath = value

    @staticmethod
    def crs_from(crs_from):
        return crs_from.currentText()

    @staticmethod
    def crs_to(crs_to):
        return crs_to.currentText()

    def destination_path(self):
        # create a custom stylesheet for the save dialog
        if self.is_table_empty(self.right_table):
            return
        save_dialog_stylesheet = """
        QLabel {
            color: white;
        }
        QPushButton {
            background-color: #1c1c1c;
            color: white;
            border-radius: 5px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #383838;
        }
        """

        # create a file dialog and set the stylesheet
        save_dialog = QFileDialog()
        save_dialog.setStyleSheet(save_dialog_stylesheet)

        # set the dialog options and open the dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontResolveSymlinks

        filepath, _ = save_dialog.getSaveFileName(None, "Save file", "", "CSV Files (*.csv)", options=options)

        if filepath:
            # do something with the file_name
            print(f"Selected file: {filepath}")
            self.export_transformed_coordinates(filepath)

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("File saved successfully!")
            msgBox.setWindowTitle("File saved")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()

    @staticmethod
    def is_table_empty(table):
        """
        Check if all cells in the given table are empty.
        Returns True if the table is empty, False otherwise.
        """
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None and item.text():
                    return False
        return True

    def export_transformed_coordinates(self, dst_filepath):
        x, y = self.gdf_transformed.geometry.x, self.gdf_transformed.geometry.y  # Grab the x and y cols
        data = {"X": x, "Y": y}
        x_y_data_frame = gp.GeoDataFrame(data=data)
        x_y_data_frame.to_csv(dst_filepath, index=False, header=False)

    def loadData(self, table, file_path):
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row_data in csv_reader:
                row = table.rowCount()
                table.insertRow(row)
                for column, data in enumerate(row_data):
                    item = QTableWidgetItem(data)
                    table.setItem(row, column, item)

            # Resize columns to fit contents
        # table.resizeColumnsToContents()

    def exportTableToCsv(self, tableWidget, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            self.right_table.clearContents()
            self.right_table.setRowCount(0)

            for row in range(tableWidget.rowCount()):
                row_data = []
                for column in range(tableWidget.columnCount() - 1):
                    item = tableWidget.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                writer.writerow(row_data)

    def importCsvFile(self, table):
        # Open file dialog and get selected file path
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV file", "", "CSV files (*.csv)")
        if file_path:
            # Clear table before loading new data
            table.clearContents()
            table.setRowCount(0)
            # Read data from CSV file and load into table
            self.loadData(self.left_table, file_path)

    def transform_to(self):
        if self.is_table_empty(self.left_table):
            return
        self.exportTableToCsv(self.left_table, self.data_to_be_transformed)
        try:
            df = gp.read_file(filename=self.data_to_be_transformed)

            geometry = [Point(xy) for xy in zip(df.iloc[:, 0], df.iloc[:, 1]) if
                        xy and isinstance(xy[0], str) and xy[0] and xy[1]]
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid Coordinates Entered")
        else:

            crs = f'epsg:{self.crs_from(self.left_combobox)}'
            print(crs)

            # Replace empty strings with NaN
            df.replace('', pd.NA, inplace=True)

            # Drop rows with NaN values
            df.dropna(inplace=True)

            gdf = gp.GeoDataFrame(df, crs=crs, geometry=geometry)

            print(self.crs_from(self.left_combobox), self.crs_to(self.right_combobox))
            if self.crs_from(self.left_combobox) == self.crs_to(self.right_combobox):
                QMessageBox.critical(self, "Error",
                                     f"Cannot convert {self.crs_from(self.left_combobox)} to {self.crs_to(self.right_combobox)}")
                return

            crs_to = self.crs_to(self.right_combobox)
            self.gdf_transformed = gdf.to_crs(f"epsg:{crs_to}")

            # Save the transformed data to a new CSV file

            self.export_transformed_coordinates(self.dst_filepath)
            self.loadData(self.right_table, self.dst_filepath)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MyWindow()
    instruction_screen = InstructionScreen()
    instruction_screen.show()
    sys.exit(app.exec_())
