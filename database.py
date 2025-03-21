import sqlite3

def init_db():
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    
    # Tabella Utenti
    c.execute('''CREATE TABLE IF NOT EXISTS users
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              password TEXT NOT NULL,
              role TEXT NOT NULL)''')
    
    # Tabella Studenti
    c.execute('''CREATE TABLE IF NOT EXISTS students
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              email TEXT UNIQUE NOT NULL,
              hourly_cost REAL NOT NULL)''')
    
    # Tabella Materie
    c.execute('''CREATE TABLE IF NOT EXISTS subjects
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              teacher_id INTEGER NOT NULL,
              FOREIGN KEY(teacher_id) REFERENCES users(id))''')
    
    # Tabella Lezioni
    c.execute('''CREATE TABLE IF NOT EXISTS lessons
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              student_id INTEGER NOT NULL,
              subject_id INTEGER NOT NULL,
              date DATE NOT NULL,
              duration REAL NOT NULL,
              notes TEXT,
              FOREIGN KEY(student_id) REFERENCES students(id),
              FOREIGN KEY(subject_id) REFERENCES subjects(id))''')
    
    # Inserimento utente admin di default
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', 'admin', 'insegnante'))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()
    return user


def get_user_role(username):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE username=?', (username,))
    role = c.fetchone()
    conn.close()
    return role[0] if role else None


def add_student(name, email, hourly_cost):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO students (name, email, hourly_cost) VALUES (?, ?, ?)',
                (name, email, hourly_cost))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def add_subject(name, teacher_id):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    c.execute('INSERT INTO subjects (name, teacher_id) VALUES (?, ?)',
            (name, teacher_id))
    conn.commit()
    conn.close()


def add_lesson(student_id, subject_id, date, duration, notes):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    c.execute('INSERT INTO lessons (student_id, subject_id, date, duration, notes) VALUES (?, ?, ?, ?, ?)',
            (student_id, subject_id, date, duration, notes))
    conn.commit()
    conn.close()


def get_student(student_id):
    conn = sqlite3.connect('planner.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM students WHERE id=?', (student_id,))
    student = c.fetchone()
    conn.close()
    return dict(student) if student else None


def update_student(student_id, name, email, hourly_cost):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE students SET name=?, email=?, hourly_cost=? WHERE id=?',
                (name, email, hourly_cost, student_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_student(student_id):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    
    # Verifica se lo studente ha lezioni associate
    c.execute('SELECT COUNT(*) FROM lessons WHERE student_id=?', (student_id,))
    count = c.fetchone()[0]
    
    if count > 0:
        conn.close()
        return False, f"Impossibile eliminare lo studente: ci sono {count} lezioni associate"
    
    # Elimina lo studente se non ha lezioni associate
    c.execute('DELETE FROM students WHERE id=?', (student_id,))
    conn.commit()
    conn.close()
    return True, "Studente eliminato con successo"


def get_subject(subject_id):
    conn = sqlite3.connect('planner.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM subjects WHERE id=?', (subject_id,))
    subject = c.fetchone()
    conn.close()
    return dict(subject) if subject else None


def update_subject(subject_id, name, teacher_id):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE subjects SET name=?, teacher_id=? WHERE id=?',
                (name, teacher_id, subject_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def delete_subject(subject_id):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    
    # Verifica se la materia ha lezioni associate
    c.execute('SELECT COUNT(*) FROM lessons WHERE subject_id=?', (subject_id,))
    count = c.fetchone()[0]
    
    if count > 0:
        conn.close()
        return False, f"Impossibile eliminare la materia: ci sono {count} lezioni associate"
    
    # Elimina la materia se non ha lezioni associate
    c.execute('DELETE FROM subjects WHERE id=?', (subject_id,))
    conn.commit()
    conn.close()
    return True, "Materia eliminata con successo"


def get_lesson(lesson_id):
    conn = sqlite3.connect('planner.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM lessons WHERE id=?', (lesson_id,))
    lesson = c.fetchone()
    conn.close()
    return dict(lesson) if lesson else None


def update_lesson(lesson_id, student_id, subject_id, date, duration, notes):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE lessons SET student_id=?, subject_id=?, date=?, duration=?, notes=? WHERE id=?',
                (student_id, subject_id, date, duration, notes, lesson_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def delete_lesson(lesson_id):
    conn = sqlite3.connect('planner.db')
    c = conn.cursor()
    c.execute('DELETE FROM lessons WHERE id=?', (lesson_id,))
    conn.commit()
    conn.close()
    return True, "Lezione eliminata con successo"