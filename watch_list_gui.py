from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QGroupBox,
    QPushButton, QTabWidget, QScrollArea, QGridLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QRadioButton, QButtonGroup,
    QSizePolicy, QCheckBox, QFrame, QAbstractScrollArea)
from PySide6.QtCore import (Qt)
import mysql.connector



# ---------- CONFIGURE THESE ----------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'hy460', 
    'database': 'sys' 
}

# ---------- DATABASE FUNCTIONS ----------
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def get_all_genres():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT genre FROM genres ORDER BY genre")
    genres = [row[0] for row in cursor.fetchall()]
    conn.close()
    return genres

def insert_movie(title, type, duration, status, genres):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movies (title_, type_, duration_, status_)
        VALUES (%s, %s, %s, %s)
    """, (title, type, duration, status))
    movie_id = cursor.lastrowid

    for genre in genres:
        cursor.execute("SELECT genre_id FROM genres WHERE genre = %s", (genre,))
        genre_id = cursor.fetchone()
        if genre_id:
            cursor.execute("INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)", (movie_id, genre_id[0]))

    conn.commit()
    conn.close()

def update_status(name, new_status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE movies SET status_ = %s WHERE title_ = %s", (new_status, name))
    conn.commit()
    conn.close()

def get_movie_by_title(title):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT title_, type_, duration_, status_ FROM movies WHERE title_ = %s", (title,))
    results = cursor.fetchall()
    
    conn.close()
    
    return results

def get_filtered_movies(genres=None, type_filter=None, status_filter=None):
    conn = connect_db()
    cursor = conn.cursor()

    if status_filter == "Watched":
        query = '''
            SELECT DISTINCT m.title_, m.type_, m.duration_, m.status_
            FROM movies m
            LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.genre_id
            WHERE m.status_='Watched'
        '''
    elif status_filter == "Not Watched":    
        query = '''
            SELECT DISTINCT m.title_, m.type_, m.duration_, m.status_
            FROM movies m
            LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.genre_id
            WHERE m.status_='Not Watched'
        '''
    elif status_filter == "Watching":    
        query = '''
            SELECT DISTINCT m.title_, m.type_, m.duration_, m.status_
            FROM movies m
            LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.genre_id
            WHERE m.status_='Watching'
        '''
    else:
        query = '''
            SELECT DISTINCT m.title_, m.type_, m.duration_, m.status_
            FROM movies m
            LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.genre_id
            WHERE 1=1
        '''

    params = []

    if genres:
        placeholders = ','.join(['%s'] * len(genres))
        query += f" AND g.genre IN ({placeholders})"
        params.extend(genres)

    if type_filter:
        query += " AND m.type_ = %s"
        params.append(type_filter)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# ---------- GUI ----------
class MovieDBGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Movie Database")
        self.setMinimumSize(1000, 800)

        #self.sort_states = {i: None for i in range(4)}  # 0 to 3 columns
        #self.original_data = []
        
        self.original_table_data = []
        self.sort_states = {}  # Tracks state for each column


        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.init_insert_tab()
        self.init_update_tab()
        self.init_view_tab()

    #region: insert tab
    def init_insert_tab(self):
        insert_tab = QWidget()
        self.tabs.addTab(insert_tab, "📋 Insert Movie")
        layout = QVBoxLayout(insert_tab)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)

        header = QLabel("🎬 Insert New Movie")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #444;")
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(header)

        # Movie Title
        title_label = QLabel("🎬 Movie Title:")
        title_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(title_label)

        self.insert_name = QLineEdit()
        self.insert_name.setStyleSheet("padding: 8px; font-size: 14px;")
        self.insert_name.setPlaceholderText("Enter the movie title...")
        self.insert_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.insert_name)

        # Type
        type_label = QLabel("🎞️ Select Type:")
        type_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(type_label)

        type_group = QButtonGroup(insert_tab)
        type_layout = QHBoxLayout()
        self.type_movie = QRadioButton("Movie")
        self.type_series = QRadioButton("Series")
        self.type_movie.setChecked(True)
        type_group.addButton(self.type_movie)
        type_group.addButton(self.type_series)
        type_layout.addWidget(self.type_movie)
        type_layout.addWidget(self.type_series)
        layout.addLayout(type_layout)

        # Duration
        duration_label = QLabel("⏱️ Duration:")
        duration_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(duration_label)

        self.insert_length = QLineEdit()
        self.insert_length.setStyleSheet("padding: 8px; font-size: 14px;")
        self.insert_length.setPlaceholderText("e.g. 2:13")
        self.insert_length.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.insert_length)

        # Status
        status_label = QLabel("📌 Viewing Status:")
        status_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(status_label)

        status_group = QButtonGroup(insert_tab)
        status_layout = QHBoxLayout()
        self.status_watched = QRadioButton("Watched")
        self.status_watching = QRadioButton("Watching")
        self.status_not_watched = QRadioButton("Not Watched")
        self.status_not_watched.setChecked(True)
        status_group.addButton(self.status_watched)
        status_group.addButton(self.status_watching)
        status_group.addButton(self.status_not_watched)
        status_layout.addWidget(self.status_watched)
        status_layout.addWidget(self.status_watching)
        status_layout.addWidget(self.status_not_watched)
        layout.addLayout(status_layout)

        # Genre Grid
        genre_label = QLabel("🎭 Choose Genres:")
        genre_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(genre_label)

        genre_container = QFrame()
        genre_container.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 6px; padding: 8px; }")
        genre_layout = QGridLayout(genre_container)
        genre_layout.setSpacing(10)

        self.genre_checkboxes = []
        genres = get_all_genres()
        cols = 4  # Adjust this for more/less columns
        for i, genre in enumerate(genres):
            cb = QCheckBox(genre)
            self.genre_checkboxes.append(cb)
            genre_layout.addWidget(cb, i // cols, i % cols)

        layout.addWidget(genre_container)

        # Submit Button
        insert_btn = QPushButton("➕ Add Movie to Database")
        insert_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        insert_btn.setFixedHeight(40)
        layout.addWidget(insert_btn)

        insert_btn.clicked.connect(self.insert_movie)


    def insert_movie(self):
        name = self.insert_name.text()
        length = self.insert_length.text()
        
        type_ = "Movie" if self.type_movie.isChecked() else "Series"
        
        if self.status_watched.isChecked():
            status = "Watched"
        elif self.status_watching.isChecked():
            status = "Watching"
        else:
            status = "Not Watched"

        genres = [cb.text() for cb in self.genre_checkboxes if cb.isChecked()]
        if not all([name, length]):
            QMessageBox.warning(self, "Missing Info", "Please fill all fields.")
            return

        try:
            insert_movie(name, type_, length, status, genres)
            QMessageBox.information(self, "Success", "Movie inserted successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    #endregion

    #region: update tab
    def init_update_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        title = QLabel("🎯 Update Movie Status")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #444;")
        layout.addWidget(title)

        form_layout = QVBoxLayout()

        name_label = QLabel("🎬 Movie Title:")
        name_label.setStyleSheet("font-size: 14px;")
        form_layout.addWidget(name_label)

        self.update_name = QLineEdit()
        self.update_name.setPlaceholderText("Enter the movie title...")
        self.update_name.setStyleSheet("padding: 8px; font-size: 14px;")
        form_layout.addWidget(self.update_name)

        status_label = QLabel("📌 Select New Status:")
        status_label.setStyleSheet("font-size: 14px;")
        form_layout.addWidget(status_label)

        self.status_group = QButtonGroup(self)
        self.status_buttons = {}

        for status_text in ["Watched", "Watching", "Not Watched"]:
            btn = QRadioButton(status_text)
            btn.setStyleSheet("font-size: 13px; padding: 4px;")
            self.status_group.addButton(btn)
            self.status_buttons[status_text] = btn
            form_layout.addWidget(btn)

        layout.addLayout(form_layout)

        update_btn = QPushButton("✅ Update Status")
        update_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        update_btn.clicked.connect(self.update_movie_status)
        layout.addWidget(update_btn)

        self.tabs.addTab(tab, "✏️ Update Status")

    def update_movie_status(self):
        name = self.update_name.text()
        selected_status = None
        for text, btn in self.status_buttons.items():
            if btn.isChecked():
                selected_status = text
                break

        if not name or not selected_status:
            QMessageBox.warning(self, "Missing Info", "Please enter the name and select a status.")
            return

        try:
            update_status(name, selected_status)
            QMessageBox.information(self, "Success", "Status updated.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    #endregion
    
    #region: view tab
    def init_view_tab(self):
        view_tab = QWidget()
        self.tabs.addTab(view_tab, "🎬 View Movies")

        main_layout = QVBoxLayout(view_tab)

        # --- TOP HALF: Filters (left) and Table (right) ---
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # --- Left Panel: Filters ---
        filters_widget = QWidget()
        filters_layout = QVBoxLayout(filters_widget)
        filters_widget.setMinimumWidth(300)  # Keep a good width for filters
        top_layout.addWidget(filters_widget)

        # Search title
        title_label = QLabel("🎬 Movie Title:")
        title_label.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(title_label)
        
        self.view_name = QLineEdit()
        self.view_name.setStyleSheet("padding: 8px; font-size: 14px;")
        self.view_name.setPlaceholderText("Enter the movie title...")
        self.view_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        filters_layout.addWidget(self.view_name)

        # Type filter
        type_label = QLabel("🎞️ Type:")
        type_label.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(type_label)

        self.view_type_group = QButtonGroup(filters_widget)
        self.view_type_all = QRadioButton("All")
        self.view_type_movie = QRadioButton("Movie")
        self.view_type_series = QRadioButton("Series")
        self.view_type_all.setChecked(True)
        for btn in [self.view_type_all, self.view_type_movie, self.view_type_series]:
            self.view_type_group.addButton(btn)
            filters_layout.addWidget(btn)

        # Status filter
        status_label = QLabel("📌 Status:")
        status_label.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(status_label)

        self.status_filter_group = QButtonGroup(filters_widget)
        self.view_status_all = QRadioButton("All")
        self.view_status_watched = QRadioButton("Watched")
        self.view_status_watching = QRadioButton("Watching")
        self.view_status_not_watched = QRadioButton("Not Watched")
        self.view_status_all.setChecked(True)
        for btn in [self.view_status_all, self.view_status_watched, self.view_status_watching, self.view_status_not_watched]:
            self.status_filter_group.addButton(btn)
            filters_layout.addWidget(btn)

        # Genre filter
        genre_label = QLabel("🎭 Genres:")
        genre_label.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(genre_label)

        genre_scroll = QScrollArea()
        genre_scroll.setWidgetResizable(True)
        genre_widget = QWidget()
        genre_scroll.setWidget(genre_widget)
        genre_grid = QGridLayout(genre_widget)
        self.filter_checkboxes = []
        genres = get_all_genres()
        cols = 2
        for i, genre in enumerate(genres):
            cb = QCheckBox(genre)
            self.filter_checkboxes.append(cb)
            genre_grid.addWidget(cb, i // cols, i % cols)
        filters_layout.addWidget(genre_scroll)

        #filters_layout.addStretch()
        
        
        
        #filters_layout.addStretch()

        # --- Right Panel: Movie Table ---
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Title", "Type", "Duration", "Status"])
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setStyleSheet("font-size: 13px;")
        self.results_table.horizontalHeader().sectionClicked.connect(self.sort_by_column)
        
        self.results_table.setColumnWidth(0, 250)
        self.results_table.setColumnWidth(2, 125)

        top_layout.addWidget(self.results_table)

        # --- BOTTOM: Buttons ---
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        button_layout.addStretch()
        filter_btn = QPushButton("🔍 Apply Filters")
        filter_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        filter_btn.setFixedHeight(40)
        filter_btn.clicked.connect(self.apply_filters)
        button_layout.addWidget(filter_btn)
        button_layout.addStretch()
        
        search_btn = QPushButton("🔍 Search Title")
        search_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        search_btn.setFixedHeight(40)
        search_btn.clicked.connect(self.search_tiltle)
        button_layout.addWidget(search_btn)
        button_layout.addStretch()
        
        reset_btn = QPushButton("♻️ Reset Filters")
        reset_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        reset_btn.setFixedHeight(40)
        reset_btn.clicked.connect(self.reset_filters)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()

        self.apply_filters()

    def reset_filters(self):
        self.view_type_all.setChecked(True)
        self.view_status_all.setChecked(True)
        for cb in self.filter_checkboxes:
            cb.setChecked(False)
        
        self.load_all_movies()

    def load_all_movies(self):
        self.results_table.setRowCount(0)
        movies = get_filtered_movies()
        for row, movie in enumerate(movies):
            self.results_table.insertRow(row)
            for col, value in enumerate(movie):
                self.results_table.setItem(row, col, QTableWidgetItem(str(value)))


    def apply_filters(self):
        
        self.original_table_data = []
        self.sort_states.clear()
        
        selected_genres = [cb.text() for cb in self.filter_checkboxes if cb.isChecked()]
        
        if self.view_type_movie.isChecked():
            type_filter = "Movie"
        elif self.view_type_series.isChecked():
            type_filter = "Series"
        else:
            type_filter = None

        if self.view_status_watched.isChecked():
            status_filter = "Watched"
        elif self.view_status_watching.isChecked():
            status_filter = "Watching"
        elif self.view_status_not_watched.isChecked():
            status_filter = "Not Watched"
        else:
            status_filter = None

        results = get_filtered_movies(genres=selected_genres, type_filter=type_filter, status_filter=status_filter)
        self.populate_table(results)
         
         
         
            
    def search_tiltle(self):
        
        title = self.view_name.text()
        result = get_movie_by_title(title)
        self.populate_table(result)
        if not result:
            QMessageBox.information(self, "Info", f"No movie/series named {title} found.")

    def populate_table(self, data):
        self.original_data = data
        self.results_table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def display_movies(self, movies):
        self.results_table.setRowCount(0)
        for row_num, row_data in enumerate(movies):
            self.results_table.insertRow(row_num)
            for col_num, val in enumerate(row_data):
                self.results_table.setItem(row_num, col_num, QTableWidgetItem(str(val)))

    def sort_by_column(self, index):
        if not self.original_table_data:
            # Save original order
            self.original_table_data = [
                [self.results_table.item(row, col).text() for col in range(self.results_table.columnCount())]
                for row in range(self.results_table.rowCount())
            ]

        # Cycle: 0 = asc, 1 = desc, 2 = original
        state = self.sort_states.get(index, -1)
        state = (state + 1) % 3
        self.sort_states[index] = state

        if state == 2:
            # Restore original data
            self.results_table.setSortingEnabled(False)
            self.results_table.setRowCount(0)
            self.results_table.setRowCount(len(self.original_table_data))
            for row_idx, row_data in enumerate(self.original_table_data):
                for col_idx, value in enumerate(row_data):
                    self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(value))
        else:
            # Sort ascending or descending
            self.results_table.setSortingEnabled(True)
            order = Qt.SortOrder.AscendingOrder if state == 0 else Qt.SortOrder.DescendingOrder
            self.results_table.sortItems(index, order)

    #endregion

if __name__ == "__main__":
    app = QApplication([])
    window = MovieDBGUI()
    window.show()
    app.exec()
