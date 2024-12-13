import sys
from datasets import load_dataset
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                          QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget)
import mysql.connector
import xml.etree.ElementTree as ET

class ChessDBViewer(QMainWindow):
   def __init__(self):
       super().__init__()
       self.setWindowTitle("Chess MySQL Viewer")
       self.setGeometry(100, 100, 1000, 800)
       
       main_widget = QWidget()
       self.setCentralWidget(main_widget)
       layout = QVBoxLayout(main_widget)

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

       layout.addWidget(QLabel("Results:"))
       self.results = QTextEdit()
       self.results.setReadOnly(True)
       layout.addWidget(self.results)

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
           self.show_database()
       except Exception as e:
           self.results.setText(f"Connection failed: {str(e)}")

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
                   rating = int(player.find('rating').text)
                   if rating > 2500:
                       name = player.find('name').text
                       country = player.find('country').text
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

   def import_openings(self):
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
               output.append("-" * len(output[0]))
               for row in rows:
                   output.append(" | ".join(str(val) for val in row))
               
               self.results.setText("\n".join(output))
           else:
               self.conn.commit()
               self.results.setText(f"Query executed successfully. Affected rows: {self.cursor.rowcount}")
       except Exception as e:
           self.conn.rollback()
           self.results.setText(f"Query failed: {str(e)}")

def main():
   app = QApplication(sys.argv)
   window = ChessDBViewer() 
   window.show()
   sys.exit(app.exec())

if __name__ == "__main__":
   main()