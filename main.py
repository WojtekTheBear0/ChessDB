import sys
from datasets import load_dataset
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, 
                            QFileDialog, QHBoxLayout, QTableWidget, QTableWidgetItem,
                            QComboBox, QFormLayout, QScrollArea)
import mysql.connector
import xml.etree.ElementTree as ET
import chess.pgn

class ChessDBViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess MySQL Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Add Tab Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Database Tab
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)
        self.setup_db_tab(db_layout)
        self.tabs.addTab(db_tab, "Database")
        
        # Matches Tab
        matches_tab = QWidget()
        matches_layout = QVBoxLayout(matches_tab)
        self.setup_matches_tab(matches_layout)
        self.tabs.addTab(matches_tab, "Matches")
        
        # Data Management Tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        self.setup_data_management_tab(data_layout)
        self.tabs.addTab(data_tab, "Data Management")

        relations_tab = QWidget()
        relations_layout = QVBoxLayout(relations_tab)
        self.setup_relations_tab(relations_layout)
        self.tabs.addTab(relations_tab, "Relations")
        
    def setup_relations_tab(self, layout):
        # Add dropdown for selecting the junction table
        table_select_layout = QHBoxLayout()
        table_select_layout.addWidget(QLabel("Select Junction Table:"))
        self.junction_selector = QComboBox()
        self.junction_selector.addItems(["match_endgame", "book_opening"])
        self.junction_selector.currentTextChanged.connect(self.load_junction_data)
        table_select_layout.addWidget(self.junction_selector)
        layout.addLayout(table_select_layout)

        # Add section for viewing relationships
        self.junction_table = QTableWidget()
        layout.addWidget(self.junction_table)

        # Add section for creating new relationships
        form_widget = QWidget()
        self.junction_form_layout = QFormLayout(form_widget)
        
        # Match-Endgame specific fields
        self.match_event_input = QComboBox()
        self.match_round_input = QComboBox()
        self.endgame_fen_input = QComboBox()
        
        # Populate dropdowns when connection is established
        self.junction_form_layout.addRow("Match Event:", self.match_event_input)
        self.junction_form_layout.addRow("Match Round:", self.match_round_input)
        self.junction_form_layout.addRow("Endgame FEN:", self.endgame_fen_input)
        
        # Add relationship button
        add_relation_btn = QPushButton("Add Relationship")
        add_relation_btn.clicked.connect(self.add_junction_relationship)
        self.junction_form_layout.addRow("", add_relation_btn)
        
        layout.addWidget(form_widget)
        
        # Status display for relations tab
        self.relations_status = QTextEdit()
        self.relations_status.setReadOnly(True)
        self.relations_status.setMaximumHeight(100)
        layout.addWidget(self.relations_status)


    def load_junction_data(self):
        if not hasattr(self, 'cursor'):
            self.relations_status.setText("Please connect to database first!")
            return

        junction_table = self.junction_selector.currentText()
        try:
            if junction_table == "match_endgame":
                # Populate the dropdowns
                self.cursor.execute("SELECT DISTINCT Event FROM `match`")
                events = [row[0] for row in self.cursor.fetchall()]
                self.match_event_input.clear()
                self.match_event_input.addItems(events)
                
                self.cursor.execute("SELECT DISTINCT FEN FROM endgame")
                fens = [row[0] for row in self.cursor.fetchall()]
                self.endgame_fen_input.clear()
                self.endgame_fen_input.addItems(fens)
                
                # Update rounds when event is selected
                self.match_event_input.currentTextChanged.connect(self.update_rounds)
                
                # Load existing relationships
                self.cursor.execute("""
                    SELECT me.Match_Event, me.Match_Round, me.Endgame_FEN, 
                           e.Type, e.Result
                    FROM match_endgame me
                    JOIN endgame e ON me.Endgame_FEN = e.FEN
                    ORDER BY me.Match_Event, me.Match_Round
                """)
                
                rows = self.cursor.fetchall()
                self.junction_table.setRowCount(len(rows))
                self.junction_table.setColumnCount(5)
                self.junction_table.setHorizontalHeaderLabels([
                    "Match Event", "Round", "Endgame FEN", "Endgame Type", "Result"
                ])
                
                for i, row in enumerate(rows):
                    for j, value in enumerate(row):
                        self.junction_table.setItem(i, j, QTableWidgetItem(str(value)))
                
                self.relations_status.setText(f"Loaded {len(rows)} match-endgame relationships")
            
        except Exception as e:
            self.relations_status.setText(f"Error loading junction data: {str(e)}")


    def update_rounds(self, event):
        try:
            self.cursor.execute("SELECT Round FROM `match` WHERE Event = %s", (event,))
            rounds = [row[0] for row in self.cursor.fetchall()]
            self.match_round_input.clear()
            self.match_round_input.addItems(rounds)
        except Exception as e:
            self.relations_status.setText(f"Error updating rounds: {str(e)}")

    def add_junction_relationship(self):
        if not hasattr(self, 'cursor'):
            self.relations_status.setText("Please connect to database first!")
            return

        junction_table = self.junction_selector.currentText()
        try:
            if junction_table == "match_endgame":
                event = self.match_event_input.currentText()
                round_num = self.match_round_input.currentText()
                fen = self.endgame_fen_input.currentText()
                
                # Check if relationship already exists
                self.cursor.execute("""
                    SELECT COUNT(*) FROM match_endgame 
                    WHERE Match_Event = %s AND Match_Round = %s AND Endgame_FEN = %s
                """, (event, round_num, fen))
                
                if self.cursor.fetchone()[0] > 0:
                    self.relations_status.setText("This relationship already exists!")
                    return
                
                # Insert new relationship
                self.cursor.execute("""
                    INSERT INTO match_endgame (Match_Event, Match_Round, Endgame_FEN)
                    VALUES (%s, %s, %s)
                """, (event, round_num, fen))
                
                self.conn.commit()
                self.relations_status.setText("Relationship added successfully!")
                self.load_junction_data()  # Refresh the view
                
        except Exception as e:
            self.conn.rollback()
            self.relations_status.setText(f"Error adding relationship: {str(e)}")

    def setup_data_management_tab(self, layout):
        # Table selector
        table_select_layout = QHBoxLayout()
        table_select_layout.addWidget(QLabel("Select Table:"))
        self.table_selector = QComboBox()
        self.table_selector.addItems([
            "master", "yearlytop100", "opening", "match", "endgame",
            "book", "book_opening", "match_endgame"  # Added junction tables
        ])
        self.table_selector.currentTextChanged.connect(self.load_table_data)
        table_select_layout.addWidget(self.table_selector)
        layout.addLayout(table_select_layout)
    def setup_data_management_tab(self, layout):
    # Table selector
        table_select_layout = QHBoxLayout()
        table_select_layout.addWidget(QLabel("Select Table:"))
        self.table_selector = QComboBox()
        self.table_selector.addItems([
            "master", 
            "yearlytop100", 
            "opening", 
            "match", 
            "endgame",
            "book",  # Added book
            "book_opening",  # Added book_opening junction table
            "match_endgame"  # Added match_endgame junction table
        ])
        self.table_selector.currentTextChanged.connect(self.load_table_data)
        table_select_layout.addWidget(self.table_selector)
        layout.addLayout(table_select_layout)

        # View section
        view_group = QWidget()
        view_layout = QVBoxLayout(view_group)
        
        # Table view
        self.data_table = QTableWidget()
        view_layout.addWidget(self.data_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.load_table_data)
        view_layout.addWidget(refresh_btn)
        
        layout.addWidget(view_group)

        # Insert section
        insert_scroll = QScrollArea()
        insert_scroll.setWidgetResizable(True)
        insert_widget = QWidget()
        self.insert_layout = QFormLayout(insert_widget)
        insert_scroll.setWidget(insert_widget)
        
        # Dynamic form fields will be added here
        self.input_fields = {}
        
        # Insert button
        insert_btn = QPushButton("Insert Data")
        insert_btn.clicked.connect(self.insert_data)
        self.insert_layout.addRow("", insert_btn)
        
        layout.addWidget(insert_scroll)
        
        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(100)
        layout.addWidget(self.status_display)

    def setup_db_tab(self, layout):
        # Database connection UI components
        layout.addWidget(QLabel("MySQL Connection"))
        
        layout.addWidget(QLabel("Host:"))
        self.host = QLineEdit("localhost")
        layout.addWidget(self.host)
        
        layout.addWidget(QLabel("Username:"))
        self.username = QLineEdit("root")
        layout.addWidget(self.username)
        
        layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_db)
        layout.addWidget(connect_btn)

        show_db_btn = QPushButton("Show Database Structure")
        show_db_btn.clicked.connect(self.show_database)
        layout.addWidget(show_db_btn)

        import_btn = QPushButton("Import Masters XML") 
        import_btn.clicked.connect(self.import_masters)
        layout.addWidget(import_btn)

        top_import_btn = QPushButton("Import Top Masters XML") 
        top_import_btn.clicked.connect(self.import_top_masters)
        layout.addWidget(top_import_btn)

        import_openings_btn = QPushButton("Import Openings")
        import_openings_btn.clicked.connect(self.import_openings)
        layout.addWidget(import_openings_btn)
        
        check_masters_btn = QPushButton("Show Masters Data")
        check_masters_btn.clicked.connect(self.show_masters)
        layout.addWidget(check_masters_btn)

        layout.addWidget(QLabel("SQL Query:"))
        self.query = QTextEdit()
        self.query.setPlaceholderText("Enter your SQL query here...")
        layout.addWidget(self.query)
        
        execute_btn = QPushButton("Execute Query")
        execute_btn.clicked.connect(self.execute_query)
        layout.addWidget(execute_btn)

        import_endgame_btn = QPushButton("Import Endgame TBS")
        import_endgame_btn.clicked.connect(self.import_endgame_tbs)
        layout.addWidget(import_endgame_btn)

        layout.addWidget(QLabel("Results:"))
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)

    def setup_matches_tab(self, layout):
        header_layout = QHBoxLayout()
        
        import_matches_btn = QPushButton("Import Matches TXT")
        import_matches_btn.clicked.connect(self.import_matches_txt)
        header_layout.addWidget(import_matches_btn)
        
        show_matches_btn = QPushButton("Show All Matches")
        show_matches_btn.clicked.connect(self.show_all_matches)
        header_layout.addWidget(show_matches_btn)
        
        layout.addLayout(header_layout)
        
        self.matches_table = QTableWidget()
        layout.addWidget(self.matches_table)

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host.text(),
                user=self.username.text(),
                password=self.password.text(),
                database="ChessDB"
            )
            self.cursor = self.conn.cursor()
            self.results.setText("Connected to MySQL successfully!")
            self.status_display.setText("Connected to MySQL successfully!")
            self.show_database()
            self.load_table_data()
        except Exception as e:
            self.results.setText(f"Connection failed: {str(e)}")
            self.status_display.setText(f"Connection failed: {str(e)}")

    def show_database(self):
        if not hasattr(self, 'cursor'):
            self.results.setText("Please connect to database first!")
            return

        try:
            output = ["=== ChessDB Structure ===\n"]
            
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                output.append(f"\n=== Table: {table_name} ===")
                
                self.cursor.execute(f"DESCRIBE `{table_name}`")
                columns = self.cursor.fetchall()
                output.append("\nColumns:")
                for col in columns:
                    output.append(f"- {col[0]}: {col[1]}")
                
                self.cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
                rows = self.cursor.fetchall()
                if rows:
                    output.append("\nSample Data:")
                    column_names = [desc[0] for desc in self.cursor.description]
                    output.append(" | ".join(column_names))
                    output.append("-" * len(" | ".join(column_names)))
                    for row in rows:
                        output.append(" | ".join(str(val) for val in row))
                output.append("\n" + "="*50)

            self.results.setText("\n".join(output))
        except Exception as e:
            self.results.setText(f"Failed to show database structure: {str(e)}")

    def show_masters(self):
        if not hasattr(self, 'cursor'):
            self.results.setText("Please connect to database first!")
            return
            
        try:
            self.cursor.execute("SELECT * FROM master ORDER BY Rating DESC")
            rows = self.cursor.fetchall()
            if rows:
                output = ["=== Masters Table Contents ===\n"]
                output.append("Name | Country | Rating")
                output.append("-" * 40)
                for row in rows:
                    output.append(f"{row[0]} | {row[1]} | {row[2]}")
                self.results.setText("\n".join(output))
            else:
                self.results.setText("No data found in masters table")
        except Exception as e:
            self.results.setText(f"Query failed: {str(e)}")

    def import_masters(self):
        if not hasattr(self, 'conn'):
            self.results.setText("Please connect to database first!")
            return
            
        try:
            cursor = self.conn.cursor()
            tree = ET.parse('masters.xml')
            root = tree.getroot()
            
            for player in root.findall('player'):
                try:
                    rating_elem = player.find('rating')
                    if rating_elem is None:
                        continue
                    
                    rating = int(rating_elem.text)
                    if rating > 2500:
                        name_elem = player.find('name')
                        country_elem = player.find('country')
                        
                        if None in (name_elem, country_elem):
                            print("Skipping player - missing required data")
                            continue
                            
                        name = name_elem.text
                        country = country_elem.text
                        
                        cursor.execute("""
                            INSERT INTO master (Name, Country, Rating) 
                            VALUES (%s, %s, %s)
                        """, (name, country, rating))
                except Exception as e:
                    print(f"Error processing player: {e}")
                    continue
            
            self.conn.commit()
            self.results.setText("Masters data imported successfully!")
            self.show_database()
        except Exception as e:
            self.conn.rollback()
            self.results.setText(f"Import failed: {str(e)}")

    def import_top_masters(self):
        if not hasattr(self, 'conn'):
            self.results.setText("Please connect to database first!")
            return
            
        try:
            cursor = self.conn.cursor()
            tree = ET.parse('masters.xml')
            root = tree.getroot()
            
            current_rank = 1
            
            for player in root.findall('player'):
                try:
                    rating_elem = player.find('rating')
                    if rating_elem is None:
                        continue
                        
                    rating = int(rating_elem.text)
                    if rating > 2635:
                        name_elem = player.find('name')
                        year_elem = player.find('birthday')
                        
                        if None in (name_elem, year_elem):
                            print(f"Skipping player - missing name or birthday")
                            continue
                            
                        name = name_elem.text
                        year = year_elem.text
                        
                        cursor.execute("""
                            INSERT INTO yearlytop100 
                            (`Year`, `Rank`, `Player_Name`, `Rating`) 
                            VALUES 
                            (%s, %s, %s, %s)
                        """, (year, current_rank, name, rating))
                        
                        current_rank += 1
                        
                except Exception as e:
                    print(f"Error processing top 100 player: {e}")
                    continue
            
            self.conn.commit()
            self.results.setText("Top Masters data imported successfully!")
            self.show_database()
        except Exception as e:
            self.conn.rollback()
            self.results.setText(f"Import failed: {str(e)}")

    def import_openings(self):
        if not hasattr(self, 'cursor'):
            self.results.setText("Please connect to database first!")
            return
            
        try:
            dataset = load_dataset("Lichess/chess-openings", split="train")
            df = dataset.to_pandas()
            count = 0
            
            for _, row in df[['pgn', 'name', 'eco']].head(500).iterrows():
                self.cursor.execute("""
                    INSERT INTO opening (FEN, Name, ECO) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    Name = VALUES(Name), 
                    ECO = VALUES(ECO)
                """, (row['pgn'], row['name'], row['eco']))
                count += 1
                
            self.conn.commit()
            self.results.setText(f"Imported {count} openings successfully")
        except Exception as e:
            self.conn.rollback()
            self.results.setText(f"Import failed: {str(e)}")

    def execute_query(self):
        if not hasattr(self, 'cursor'):
            self.results.setText("Please connect to database first!")
            return
            
        try:
            query = self.query.toPlainText()
            self.cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()
                
                output = [" | ".join(columns)]
                output.append("-" * len(" | ".join(columns)))
                for row in rows:
                    output.append(" | ".join(str(val) for val in row))
                
                self.results.setText("\n".join(output))
            else:
                self.conn.commit()
                self.results.setText(f"Query executed successfully. Affected rows: {self.cursor.rowcount}")
        except Exception as e:
            self.conn.rollback()
            self.results.setText(f"Query failed: {str(e)}")

    def import_matches_txt(self):
        if not hasattr(self, 'conn'):
            self.results.setText("Please connect to database first!")
            return

        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Matches TXT File", "", 
                                                 "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as pgn_file:
                    game_number = 1
                    imported_count = 0
                    while True:
                        game = chess.pgn.read_game(pgn_file)
                        if game is None:
                            break
                        
                        headers = game.headers
                        event = headers.get("Event", "Unknown Event")
                        round_num = headers.get("Round", "?")
                        if round_num == "?":
                            round_num = "Unknown"
                            
                        white_name = headers.get("White", "Unknown White")
                        black_name = headers.get("Black", "Unknown Black")
                        result = headers.get("Result", "Unknown Result")
                        pgn_text = str(game)
                        eco = headers.get("ECO", "")
                        
                        try:
                            self.cursor.execute("""
                                INSERT INTO `match` (Event, Round, White_Name, Black_Name, Result, PGN, Opening)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (event, round_num, white_name, black_name, result, pgn_text, eco))
                            imported_count += 1
                        except Exception as db_e:
                            print(f"Error importing game #{game_number}: {db_e}")
                            continue
                        
                        game_number += 1
                
                self.conn.commit()
                self.results.setText(f"Imported {imported_count} matches successfully from {file_name}!")
                self.show_all_matches()
            except Exception as e:
                self.conn.rollback()
                self.results.setText(f"Import failed: {str(e)}")

    def show_all_matches(self):
        if not hasattr(self, 'cursor'):
            self.results.setText("Please connect to database first!")
            return
        
        try:
            self.cursor.execute("SELECT * FROM `match`")
            rows = self.cursor.fetchall()
            column_names = [desc[0] for desc in self.cursor.description]
            
            self.matches_table.setRowCount(len(rows))
            self.matches_table.setColumnCount(len(column_names))
            self.matches_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    self.matches_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            
            self.results.setText(f"Displayed {len(rows)} matches.")
        except Exception as e:
            self.results.setText(f"Failed to retrieve matches: {str(e)}")

    def import_endgame_tbs(self):
        if not hasattr(self, 'conn'):
            self.results.setText("Please connect to database first!")
            return

        options = QFileDialog.Option.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Endgame TBS Files", 
            "", 
            "TBS Files (*.tbs);;All Files (*)",
            options=options
        )
        
        if not files:
            return

        try:
            cursor = self.conn.cursor()
            total_imported = 0
            
            for file_path in files:
                endgame_type = self.get_endgame_type(file_path)
                positions = self.parse_tbs_file(file_path)
                
                for pos in positions:
                    try:
                        cursor.execute("""
                            INSERT INTO endgame (FEN, Result, Type)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            Result = VALUES(Result),
                            Type = VALUES(Type)
                        """, (pos[0], pos[1], endgame_type))
                        total_imported += 1
                    except Exception as e:
                        print(f"Error importing position: {e}")
                        continue

            self.conn.commit()
            self.results.setText(f"Successfully imported {total_imported} endgame positions!")
            
        except Exception as e:
            self.conn.rollback()
            self.results.setText(f"Import failed: {str(e)}")

    def get_endgame_type(self, file_path: str) -> str:
        """Extract endgame type from filename (e.g., 'kqk.tbs' -> 'KQK')"""
        base_name = file_path.split('/')[-1].split('\\')[-1]  # Handle both Unix and Windows paths
        endgame_type = base_name.split('.')[0].upper()
        return endgame_type

    def parse_tbs_file(self, file_path: str) -> list:
        """Parse a tablebase file and return list of positions"""
        positions = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        fen = parts[0].strip()
                        result = parts[1].strip()
                        positions.append((fen, result))
        except Exception as e:
            print(f"Error parsing TBS file {file_path}: {e}")
        return positions

    def load_table_data(self):
        if not hasattr(self, 'cursor'):
            self.status_display.setText("Please connect to database first!")
            return

        table_name = self.table_selector.currentText()
        try:
            # Get column information
            self.cursor.execute(f"DESCRIBE `{table_name}`")  # Added backticks
            columns = self.cursor.fetchall()
            
            # Update table view
            self.cursor.execute(f"SELECT * FROM `{table_name}`")  # Added backticks
            rows = self.cursor.fetchall()
            
            self.data_table.setRowCount(len(rows))
            self.data_table.setColumnCount(len(columns))
            self.data_table.setHorizontalHeaderLabels([col[0] for col in columns])
            
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.data_table.setItem(i, j, QTableWidgetItem(str(value)))
            
            # Update insert form
            self.update_insert_form(columns)
            
            self.status_display.setText(f"Loaded {len(rows)} rows from {table_name}")
        except Exception as e:
            self.status_display.setText(f"Error loading data: {str(e)}")

    def update_insert_form(self, columns):
        # Clear existing fields
        while self.insert_layout.rowCount() > 0:
            self.insert_layout.removeRow(0)
        self.input_fields = {}

        # Add new fields based on column information
        for col in columns:
            col_name = col[0]
            field_type = col[1]
            
            if 'int' in field_type.lower():
                field = QLineEdit()
                field.setPlaceholderText("Enter number...")
            elif 'text' in field_type.lower():
                field = QTextEdit()
                field.setMaximumHeight(100)
            else:
                field = QLineEdit()
                field.setPlaceholderText(f"Enter {col_name}...")
            
            self.input_fields[col_name] = field
            self.insert_layout.addRow(f"{col_name}:", field)

        # Add insert button
        insert_btn = QPushButton("Insert Data")
        insert_btn.clicked.connect(self.insert_data)
        self.insert_layout.addRow("", insert_btn)

    def insert_data(self):
        if not hasattr(self, 'cursor'):
            self.status_display.setText("Please connect to database first!")
            return

        table_name = self.table_selector.currentText()
        values = {}
        
        # Collect values from input fields
        for col_name, field in self.input_fields.items():
            if isinstance(field, QTextEdit):
                values[col_name] = field.toPlainText()
            else:
                values[col_name] = field.text()

        try:
            # Construct and execute INSERT query
            columns = ', '.join(f'`{col}`' for col in values.keys())  # Added backticks
            placeholders = ', '.join(['%s'] * len(values))
            query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"  # Added backticks
            
            self.cursor.execute(query, list(values.values()))
            self.conn.commit()
            
            self.status_display.setText("Data inserted successfully!")
            self.load_table_data()  # Refresh the view
            
            # Clear input fields
            for field in self.input_fields.values():
                if isinstance(field, QTextEdit):
                    field.clear()
                else:
                    field.setText("")
                    
        except Exception as e:
            self.conn.rollback()
            self.status_display.setText(f"Error inserting data: {str(e)}")
def main():
   app = QApplication(sys.argv)
   window = ChessDBViewer() 
   window.show()
   sys.exit(app.exec())

if __name__ == "__main__":
   main()