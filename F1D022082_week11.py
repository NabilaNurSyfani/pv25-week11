import sys
import sqlite3
import csv
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMenuBar, QAction, QFileDialog, QTabWidget, QMessageBox, QInputDialog, QHeaderView, QDockWidget
)

class BukuApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Week 11 - Manajemen Buku")
        self.setGeometry(200, 200, 650, 500)

        self.conn = sqlite3.connect("katalog.db")
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                pengarang TEXT,
                tahun INTEGER
            )
        """)
        self.conn.commit()

        self.initUI()

    def initUI(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        # Menu File
        fileMenu = self.menuBar.addMenu("File")
        saveAction = QAction("Simpan", self)
        exportAction = QAction("Ekspor ke CSV", self)
        exitAction = QAction("Keluar", self)
        saveAction.triggered.connect(self.saveData)
        exportAction.triggered.connect(self.exportCSV)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exportAction)
        fileMenu.addAction(exitAction)

        # Menu Edit
        editMenu = self.menuBar.addMenu("Edit")
        searchAction = QAction("Cari Judul", self)
        deleteAction = QAction("Hapus Data", self)
        autoFillAction = QAction("Auto Fill", self)
        deleteAction.triggered.connect(self.deleteData)
        autoFillAction.triggered.connect(self.autoFill)
        searchAction.triggered.connect(self.focusSearch)
        editMenu.addAction(searchAction)
        editMenu.addAction(deleteAction)
        editMenu.addAction(autoFillAction)

        # Tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab Data Buku
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Data Buku")
        tab1_layout = QVBoxLayout()
        form_layout = QVBoxLayout()

        # Input Judul
        judul_layout = QHBoxLayout()
        judul_label = QLabel("Judul:")
        judul_label.setFixedWidth(70)
        self.judulInput = QLineEdit()
        paste_button = QPushButton("Paste from Clipboard")
        paste_button.setStyleSheet("background-color: #3D90D7; color: white; padding: 5px; font-weight: bold;")
        paste_button.setFixedWidth(150)
        paste_button.clicked.connect(self.pasteFromClipboard)
        judul_layout.addWidget(judul_label)
        judul_layout.addWidget(self.judulInput)
        judul_layout.addWidget(paste_button)
        form_layout.addLayout(judul_layout)

        # Input Pengarang
        pengarang_layout = QHBoxLayout()
        pengarang_label = QLabel("Pengarang:")
        pengarang_label.setFixedWidth(70)
        self.pengarangInput = QLineEdit()
        pengarang_layout.addWidget(pengarang_label)
        pengarang_layout.addWidget(self.pengarangInput)
        form_layout.addLayout(pengarang_layout)

        # Input Tahun
        tahun_layout = QHBoxLayout()
        tahun_label = QLabel("Tahun:")
        tahun_label.setFixedWidth(70)
        self.tahunInput = QLineEdit()
        tahun_layout.addWidget(tahun_label)
        tahun_layout.addWidget(self.tahunInput)
        form_layout.addLayout(tahun_layout)

        # Tombol Simpan
        save_button = QPushButton("Simpan")
        save_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; font-weight: bold;")
        save_button.clicked.connect(self.saveData)
        form_layout.addWidget(save_button, alignment=Qt.AlignCenter)

        # Pencarian
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Cari judul...")
        self.searchBox.textChanged.connect(self.loadData)
        form_layout.addWidget(self.searchBox)

        # Tabel Data Buku
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.cellDoubleClicked.connect(self.editCell)
        form_layout.addWidget(self.table)

        # Tombol Hapus
        delete_button = QPushButton("Hapus Data")
        delete_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px; font-weight: bold;")
        delete_button.clicked.connect(self.deleteData)
        form_layout.addWidget(delete_button, alignment=Qt.AlignCenter)

        tab1_layout.addLayout(form_layout)
        self.tab1.setLayout(tab1_layout)

        # Tab Ekspor
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "Ekspor")
        tab2_layout = QVBoxLayout()
        label = QLabel("Gunakan menu File > Ekspor ke CSV untuk menyimpan data.")
        label.setAlignment(Qt.AlignCenter)
        tab2_layout.addWidget(label)
        self.tab2.setLayout(tab2_layout)
        
        # Dock Widget
        self.helpDock = QDockWidget("Bantuan", self)
        self.helpDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        help_content = QLabel()
        help_content.setWordWrap(True)
        help_content.setText(
            "📚 Petunjuk Penggunaan:\n\n"
            "- Isi form Judul, Pengarang, dan Tahun lalu klik Simpan.\n"
            "- Gunakan kotak pencarian untuk mencari berdasarkan Judul.\n"
            "- Klik dua kali pada sel tabel untuk mengedit.\n"
            "- Gunakan menu File untuk menyimpan dan ekspor ke CSV.\n"
            "- Data dapat dihapus dengan memilih baris dan klik Hapus Data."
        )

        help_widget = QWidget()
        help_layout = QVBoxLayout()
        help_layout.addWidget(help_content)
        help_widget.setLayout(help_layout)

        self.helpDock.setWidget(help_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.helpDock)

        # Status Bar
        self.statusBar().showMessage("Nabila Nur Syfani | F1D022082")
        self.loadData()

    def pasteFromClipboard(self):
        clipboard = QApplication.clipboard()
        self.judulInput.setText(clipboard.text())
        QMessageBox.information(self, "Berhasil", "Judul berhasil disalin dari clipboard!")

    def saveData(self):
        judul = self.judulInput.text().strip()
        pengarang = self.pengarangInput.text().strip()
        tahun = self.tahunInput.text().strip()
        if judul and pengarang and tahun:
            self.c.execute("INSERT INTO buku (judul, pengarang, tahun) VALUES (?, ?, ?)", (judul, pengarang, tahun))
            self.conn.commit()
            self.judulInput.clear()
            self.pengarangInput.clear()
            self.tahunInput.clear()
            self.loadData()
        else:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi!")

    def loadData(self):
        filter_text = self.searchBox.text()
        if filter_text:
            self.c.execute("SELECT * FROM buku WHERE judul LIKE ?", (f"%{filter_text}%",))
        else:
            self.c.execute("SELECT * FROM buku")
        rows = self.c.fetchall()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(rows):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def deleteData(self):
        selected = self.table.currentRow()
        if selected >= 0:
            id_item = self.table.item(selected, 0)
            if id_item:
                id_val = id_item.text()
                confirm = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus data ini?")
                if confirm == QMessageBox.Yes:
                    self.c.execute("DELETE FROM buku WHERE id = ?", (id_val,))
                    self.conn.commit()
                    self.loadData()
        else:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin dihapus!")

    def exportCSV(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File", "", "CSV Files (*.csv)")
        if path:
            self.c.execute("SELECT * FROM buku")
            rows = self.c.fetchall()
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(rows)
            QMessageBox.information(self, "Sukses", "Data berhasil diekspor!")

    def autoFill(self):
        self.judulInput.setText("")
        self.pengarangInput.setText("")
        self.tahunInput.setText("")

    def focusSearch(self):
        self.searchBox.setFocus()

    def editCell(self, row, column):
        item = self.table.item(row, column)
        if item and column in [1, 2, 3]:
            new_value, ok = QInputDialog.getText(self, "Edit Data", "Edit nilai:", text=item.text())
            if ok and new_value:
                column_name = ["judul", "pengarang", "tahun"][column - 1]
                book_id = self.table.item(row, 0).text()
                self.c.execute(f"UPDATE buku SET {column_name} = ? WHERE id = ?", (new_value, book_id))
                self.conn.commit()
                self.loadData()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BukuApp()
    window.show()
    sys.exit(app.exec_())