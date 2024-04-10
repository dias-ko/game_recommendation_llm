import sqlite3
from dict_matcher import TitleDictMatcher
import multiprocessing

class DatabaseParser(multiprocessing.Process):
    def __init__(self, db_file, table_name, start_index, end_index, callback):
        super().__init__()
        self.db_file = db_file
        self.table_name = table_name
        self.start_index = start_index
        self.end_index = end_index

    def run(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        matcher = TitleDictMatcher()

        query = f"SELECT * FROM {self.table_name} LIMIT {self.end_index - self.start_index + 1} OFFSET {self.start_index}"

        cursor.execute(query)
        rows = cursor.fetchall()

        process_data(self.start_index, f"data/data{self.start_index}-{self.end_index}.txt", cursor, matcher, rows)

        conn.close()

def parse_database(db_file, table_name, num_processes, callback=None):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_entries = cursor.fetchone()[0]
    print("TOTAL:", total_entries)
    conn.close()

    chunk_size = (total_entries + num_processes - 1) // num_processes
    processes = []

    for i in range(num_processes):
        start_index = i * chunk_size
        end_index = min(start_index + chunk_size - 1, total_entries - 1)
        process = DatabaseParser(db_file, table_name, start_index, end_index, callback)
        processes.append(process)

    for process in processes:
       process.start()

    for process in processes:
        process.join()

def save_data(data, filename):
  with open(filename, "a", encoding='utf-8') as f:
      for row in data:
          f.write(row + "\n")

def process_data(index, filename, cursor, matcher, rows):
    count = index
    data = []
    for row in rows:
        count += 1
        submission_id = row[0]
        submission_text = row[1]

        if len(submission_text) < 32:
            continue

        cursor.execute("SELECT comment, score FROM Comments WHERE sid = ? AND score > 0 ORDER BY score DESC", (submission_id,))
            
        for comment_row in cursor.fetchall():
            comment_text = comment_row[0]
            score = comment_row[1]

            games = [game for game, _, _ in matcher(comment_text)]
            if games:
                games_str = "[" + ", ".join(games) + "]"
                data.append((str(count) + "\t" + games_str + "\t" + str(score) + "\t" + submission_text.replace("\t", " ") + "\t" + comment_text.replace("\t", " ") + "\t" ).replace("\n", " "))
                break
        if count % 100 == 0:
            save_data(data, filename)
            data = []
            print(index, count)

if __name__ == "__main__":
    parse_database("submissions.db", "Submissions", 6)