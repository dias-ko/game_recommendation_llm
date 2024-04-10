import sqlite3
from dict_matcher import TitleDictMatcher

def save_data(data, filename):
  with open(filename, "a", encoding='utf-8') as f:
      f.write(data + "\n")

def get_top_comments(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    data = []
    matcher = TitleDictMatcher()

    count = 0
    cursor.execute("SELECT * FROM Submissions")
    for row in cursor.fetchall():
        count += 1
        submission_id = row[0]
        
        submission_text = row[1]
        cursor.execute(
            "SELECT comment FROM Comments WHERE sid = ? AND score > 0 ORDER BY score DESC",
            (submission_id,),
        )

        for comment_row in cursor.fetchall():
            comment_text = comment_row[0]

            temp = matcher(comment_text)
            if temp:
                save_data(("[INST] " + submission_text + " [/INST] " + comment_text).replace("\n", " "), "train.txt")    
                break

        print(count)

    conn.close()

    return data

database_file = "submissions.db"
data = get_top_comments(database_file)