import streamlit as st
import sqlite3
import pandas as pd
import io
from datetime import datetime

# Configurazione iniziale della pagina
st.set_page_config(page_title='Planner Lezioni', layout='wide')

# Funzioni di gestione database e autenticazione saranno implementate qui
from database import init_db, authenticate_user, get_user_role, add_student, add_subject, add_lesson, \
    update_student, delete_student, update_subject, delete_subject, update_lesson, delete_lesson, \
    get_student, get_subject, get_lesson

# Inizializzazione database
init_db()

# Gestione sessione
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        with st.form("Login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            submitted = st.form_submit_button("Login")
            
            if submitted:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_role = get_user_role(username)
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Credenziali non valide")
    else:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
        
        if st.session_state.user_role == 'insegnante':
            render_teacher_dashboard()
        else:
            render_student_dashboard()

def render_teacher_dashboard():
    st.title('Dashboard Insegnante')
    
    # Definizione delle tab
    tab_names = ["Studenti", "Materie", "Pianificazione Lezioni", "Report"]
    
    # Crea i tab
    tabs = st.tabs(tab_names)
    
    # Contenuto delle tab
    with tabs[0]:  # Tab Studenti
        render_students_tab()
    
    with tabs[1]:  # Tab Materie
        render_subjects_tab()
    
    with tabs[2]:  # Tab Pianificazione Lezioni
        render_lessons_tab()
    
    with tabs[3]:  # Tab Report
        render_reports_tab()
    
def render_students_tab():
    # Gestione stato per modifica studente
    if 'edit_student_id' not in st.session_state:
        st.session_state.edit_student_id = None
    
    # Visualizza lista studenti esistenti
    conn = sqlite3.connect('planner.db')
    students_df = pd.read_sql('SELECT id, name, email, hourly_cost FROM students', conn)
    conn.close()
    
    if not students_df.empty:
        st.subheader('Studenti Registrati')
        
        # Aggiungi colonne per i pulsanti di modifica e cancellazione
        col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 0.5, 0.5])
        with col1:
            st.write("ID")
        with col2:
            st.write("Nome")
        with col3:
            st.write("Email")
        with col4:
            st.write("Costo Orario")
        with col5:
            st.write("Modifica")
        with col6:
            st.write("Elimina")
        
        for _, row in students_df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 0.5, 0.5])
            with col1:
                st.write(row['id'])
            with col2:
                st.write(row['name'])
            with col3:
                st.write(row['email'])
            with col4:
                st.write(f"€{row['hourly_cost']:.2f}")
            with col5:
                if st.button("✏️", key=f"edit_student_{row['id']}"):
                    st.session_state.edit_student_id = row['id']
                    st.rerun()
            with col6:
                if st.button("🗑️", key=f"delete_student_{row['id']}"):
                    success, message = delete_student(row['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Form per modificare studente esistente
    if st.session_state.edit_student_id is not None:
        st.subheader('Modifica Studente')
        student = get_student(st.session_state.edit_student_id)
        if student:
            with st.form("Modifica Studente"):
                name = st.text_input("Nome Studente", value=student['name'])
                email = st.text_input("Email", value=student['email'])
                hourly_cost = st.number_input("Costo Orario", min_value=0.0, value=student['hourly_cost'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Aggiorna"):
                        if name and email:  # Verifica che i campi obbligatori siano compilati
                            if update_student(st.session_state.edit_student_id, name, email, hourly_cost):
                                st.success("Studente aggiornato con successo")
                                st.session_state.edit_student_id = None
                                st.rerun()
                            else:
                                st.error("Email già esistente")
                        else:
                            st.warning("Compila tutti i campi obbligatori")
                with col2:
                    if st.form_submit_button("Annulla"):
                        st.session_state.edit_student_id = None
                        st.rerun()
    
    # Form per aggiungere nuovo studente
    st.subheader('Aggiungi Nuovo Studente')
    with st.form("Nuovo Studente"):
        name = st.text_input("Nome Studente")
        email = st.text_input("Email")
        hourly_cost = st.number_input("Costo Orario", min_value=0.0)
        if st.form_submit_button("Salva"):
            if name and email:  # Verifica che i campi obbligatori siano compilati
                if add_student(name, email, hourly_cost):
                    st.success("Studente aggiunto con successo")
                    st.rerun()  # Aggiorna la lista
                else:
                    st.error("Email già esistente")
            else:
                st.warning("Compila tutti i campi obbligatori")


def render_subjects_tab():
    # Gestione stato per modifica materia
    if 'edit_subject_id' not in st.session_state:
        st.session_state.edit_subject_id = None
    
    # Visualizza materie esistenti
    conn = sqlite3.connect('planner.db')
    subjects_df = pd.read_sql('SELECT id, name FROM subjects', conn)
    conn.close()
    
    if not subjects_df.empty:
        st.subheader('Materie Disponibili')
        
        # Aggiungi colonne per i pulsanti di modifica e cancellazione
        col1, col2, col3, col4 = st.columns([1, 3, 0.5, 0.5])
        with col1:
            st.write("ID")
        with col2:
            st.write("Nome")
        with col3:
            st.write("Modifica")
        with col4:
            st.write("Elimina")
        
        for _, row in subjects_df.iterrows():
            col1, col2, col3, col4 = st.columns([1, 3, 0.5, 0.5])
            with col1:
                st.write(row['id'])
            with col2:
                st.write(row['name'])
            with col3:
                if st.button("✏️", key=f"edit_subject_{row['id']}"):
                    st.session_state.edit_subject_id = row['id']
                    st.rerun()
            with col4:
                if st.button("🗑️", key=f"delete_subject_{row['id']}"):
                    success, message = delete_subject(row['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Form per modificare materia esistente
    if st.session_state.edit_subject_id is not None:
        st.subheader('Modifica Materia')
        subject = get_subject(st.session_state.edit_subject_id)
        if subject:
            with st.form("Modifica Materia"):
                name = st.text_input("Nome Materia", value=subject['name'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Aggiorna"):
                        if name:  # Verifica che il campo nome sia compilato
                            # Ottieni l'ID dell'insegnante corrente
                            conn = sqlite3.connect('planner.db')
                            c = conn.cursor()
                            c.execute('SELECT id FROM users WHERE username = ?', (st.session_state.username,))
                            result = c.fetchone()
                            teacher_id = result[0] if result else 1  # Default a 1 se non trovato
                            conn.close()
                            
                            if update_subject(st.session_state.edit_subject_id, name, teacher_id):
                                st.success("Materia aggiornata con successo")
                                st.session_state.edit_subject_id = None
                                st.rerun()
                            else:
                                st.error("Errore durante l'aggiornamento della materia")
                        else:
                            st.warning("Inserisci il nome della materia")
                with col2:
                    if st.form_submit_button("Annulla"):
                        st.session_state.edit_subject_id = None
                        st.rerun()
    
    # Form per aggiungere nuova materia
    st.subheader('Aggiungi Nuova Materia')
    with st.form("Nuova Materia"):
        name = st.text_input("Nome Materia")
        if st.form_submit_button("Salva"):
            if name:  # Verifica che il campo nome sia compilato
                # Ottieni l'ID dell'insegnante corrente
                conn = sqlite3.connect('planner.db')
                c = conn.cursor()
                c.execute('SELECT id FROM users WHERE username = ?', (st.session_state.username,))
                result = c.fetchone()
                teacher_id = result[0] if result else 1  # Default a 1 se non trovato
                conn.close()
                
                add_subject(name, teacher_id)
                st.success("Materia aggiunta con successo")
                st.rerun()  # Aggiorna la lista
            else:
                st.warning("Inserisci il nome della materia")


def render_lessons_tab():
    # Gestione stato per modifica lezione
    if 'edit_lesson_id' not in st.session_state:
        st.session_state.edit_lesson_id = None
    
    conn = sqlite3.connect('planner.db')
    
    # Verifica se ci sono studenti e materie prima di mostrare il form
    students = pd.read_sql('SELECT id, name FROM students', conn)
    subjects = pd.read_sql('SELECT id, name FROM subjects', conn)
    
    # Visualizza lezioni esistenti
    lessons_df = pd.read_sql_query('''
        SELECT lessons.id, students.name as studente, subjects.name as materia, 
        lessons.date, lessons.duration, lessons.notes,
        lessons.student_id, lessons.subject_id
        FROM lessons
        JOIN students ON lessons.student_id = students.id
        JOIN subjects ON lessons.subject_id = subjects.id
        ORDER BY lessons.date DESC
    ''', conn)
    
    if not lessons_df.empty:
        st.subheader('Lezioni Programmate')
        # Converto la colonna date in datetime
        lessons_df['date'] = pd.to_datetime(lessons_df['date'])
        
        # Aggiungi colonne per i pulsanti di modifica e cancellazione
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 2, 2, 1, 1, 0.5, 0.5])
        with col1:
            st.write("ID")
        with col2:
            st.write("Studente")
        with col3:
            st.write("Materia")
        with col4:
            st.write("Data")
        with col5:
            st.write("Durata (ore)")
        with col6:
            st.write("Modifica")
        with col7:
            st.write("Elimina")
        
        for _, row in lessons_df.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 2, 2, 1, 1, 0.5, 0.5])
            with col1:
                st.write(row['id'])
            with col2:
                st.write(row['studente'])
            with col3:
                st.write(row['materia'])
            with col4:
                st.write(row['date'].strftime('%d/%m/%Y'))
            with col5:
                st.write(f"{row['duration']:.1f}")
            with col6:
                if st.button("✏️", key=f"edit_lesson_{row['id']}"):
                    st.session_state.edit_lesson_id = row['id']
                    st.rerun()
            with col7:
                if st.button("🗑️", key=f"delete_lesson_{row['id']}"):
                    success, message = delete_lesson(row['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Form per modificare lezione esistente
    if st.session_state.edit_lesson_id is not None:
        st.subheader('Modifica Lezione')
        lesson = get_lesson(st.session_state.edit_lesson_id)
        if lesson:
            with st.form("Modifica Lezione"):
                student_id = st.selectbox('Studente', students['id'], 
                                         format_func=lambda x: students[students['id'] == x]['name'].values[0],
                                         index=students.index[students['id'] == lesson['student_id']].tolist()[0] if lesson['student_id'] in students['id'].values else 0)
                subject_id = st.selectbox('Materia', subjects['id'], 
                                         format_func=lambda x: subjects[subjects['id'] == x]['name'].values[0],
                                         index=subjects.index[subjects['id'] == lesson['subject_id']].tolist()[0] if lesson['subject_id'] in subjects['id'].values else 0)
                date = st.date_input('Data lezione', pd.to_datetime(lesson['date']).date())
                duration = st.number_input('Durata (ore)', min_value=0.5, max_value=8.0, step=0.5, value=float(lesson['duration']))
                notes = st.text_area('Note', value=lesson['notes'] if lesson['notes'] else "")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Aggiorna"):
                        if update_lesson(st.session_state.edit_lesson_id, student_id, subject_id, date, duration, notes):
                            st.success("Lezione aggiornata con successo")
                            st.session_state.edit_lesson_id = None
                            st.rerun()
                        else:
                            st.error("Errore durante l'aggiornamento della lezione")
                with col2:
                    if st.form_submit_button("Annulla"):
                        st.session_state.edit_lesson_id = None
                        st.rerun()
    
    # Form per aggiungere nuova lezione
    st.subheader('Pianifica Nuova Lezione')
    
    if students.empty:
        st.warning('Aggiungi almeno uno studente prima di pianificare lezioni')
    elif subjects.empty:
        st.warning('Aggiungi almeno una materia prima di pianificare lezioni')
    else:
        with st.form("Nuova Lezione"):
            student_id = st.selectbox('Studente', students['id'], format_func=lambda x: students[students['id'] == x]['name'].values[0])
            subject_id = st.selectbox('Materia', subjects['id'], format_func=lambda x: subjects[subjects['id'] == x]['name'].values[0])
            date = st.date_input('Data lezione', datetime.now())
            duration = st.number_input('Durata (ore)', min_value=0.5, max_value=8.0, step=0.5)
            notes = st.text_area('Note')
            
            if st.form_submit_button('Pianifica Lezione'):
                add_lesson(student_id, subject_id, date, duration, notes)
                st.success('Lezione programmata con successo!')
                st.rerun()  # Aggiorna la lista
    
    conn.close()


def render_student_dashboard():
    st.title('Dashboard Studente')
    conn = sqlite3.connect('planner.db')
    
    # Verifica se l'utente esiste come studente
    student = pd.read_sql_query(
        'SELECT id FROM students WHERE email = ?',
        conn,
        params=(st.session_state.username,)
    )
    
    if not student.empty:
        student_id = student.iloc[0]['id']
        df = pd.read_sql_query(
            '''SELECT lessons.date, subjects.name as materia, duration, notes 
               FROM lessons 
               JOIN subjects ON lessons.subject_id = subjects.id
               WHERE student_id = ?''',
            conn,
            params=(student_id,)
        )
        
        if not df.empty:
            # Converto la colonna date in datetime
            df['date'] = pd.to_datetime(df['date'])
            st.dataframe(df)
        else:
            st.info('Non hai ancora lezioni programmate.')
    else:
        st.warning('Il tuo account non è associato a nessuno studente.')
    
    conn.close()

def render_reports_tab():
    st.subheader('Report Lezioni')
    
    conn = sqlite3.connect('planner.db')
    # Query per ottenere tutte le lezioni con dettagli
    df = pd.read_sql_query('''
        SELECT lessons.id, lessons.date, students.name as studente, subjects.name as materia, 
               duration, (duration * students.hourly_cost) as costo, notes,
               lessons.student_id, lessons.subject_id
        FROM lessons
        JOIN students ON lessons.student_id = students.id
        JOIN subjects ON lessons.subject_id = subjects.id
    ''', conn)
    conn.close()
    
    if df.empty:
        st.info('Non ci sono ancora lezioni registrate per generare report.')
        return
    
    # Converto la colonna date in datetime se non lo è già
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
        
    # Calendario interattivo
    st.subheader('Calendario Lezioni')
    
    # Gestione stato per il calendario
    if 'calendar_date' not in st.session_state:
        st.session_state.calendar_date = datetime.now()
    
    # Controlli per navigare nel calendario
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button('◀ Mese precedente'):
            st.session_state.calendar_date = st.session_state.calendar_date.replace(day=1) - pd.Timedelta(days=1)
            st.session_state.calendar_date = st.session_state.calendar_date.replace(day=1)
            st.rerun()
    with col2:
        st.write(f"### {st.session_state.calendar_date.strftime('%B %Y')}")
    with col3:
        if st.button('Mese successivo ▶'):
            next_month = st.session_state.calendar_date.replace(day=28) + pd.Timedelta(days=4)
            st.session_state.calendar_date = next_month.replace(day=1)
            st.rerun()
    
    # Creazione del calendario
    current_date = st.session_state.calendar_date.replace(day=1)
    month_days = pd.date_range(start=current_date, 
                              end=current_date.replace(day=28) + pd.Timedelta(days=4), 
                              freq='D')
    month_days = month_days[month_days.month == current_date.month]
    
    # Giorni della settimana
    weekdays = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom']
    cols = st.columns(7)
    for i, day in enumerate(weekdays):
        with cols[i]:
            st.write(f"**{day}**")
    
    # Calcolo del primo giorno del mese (0 = lunedì, 6 = domenica)
    first_day_weekday = current_date.weekday()
    
    # Creazione delle righe del calendario
    day_counter = 1
    for week in range(6):  # Massimo 6 settimane in un mese
        cols = st.columns(7)
        for weekday in range(7):
            with cols[weekday]:
                if week == 0 and weekday < first_day_weekday:
                    # Giorni vuoti prima dell'inizio del mese
                    st.write("")
                elif day_counter <= len(month_days):
                    # Giorni del mese corrente
                    day_date = current_date.replace(day=day_counter)
                    
                    # Verifica se ci sono lezioni in questo giorno
                    day_lessons = df[df['date'].dt.date == day_date.date()]
                    
                    if not day_lessons.empty:
                        # Giorno con lezioni (evidenziato)
                        if st.button(f"**{day_counter}** 📚", key=f"day_{day_counter}"):
                            st.session_state.selected_day = day_date.date()
                            st.rerun()
                    else:
                        # Giorno senza lezioni
                        if st.button(f"{day_counter}", key=f"day_{day_counter}"):
                            st.session_state.selected_day = day_date.date()
                            st.rerun()
                    
                    day_counter += 1
                else:
                    # Giorni dopo la fine del mese
                    break
        if day_counter > len(month_days):
            break
    
    # Visualizzazione dettaglio lezioni per il giorno selezionato
    if 'selected_day' in st.session_state:
        selected_day = st.session_state.selected_day
        st.subheader(f"Lezioni del {selected_day.strftime('%d/%m/%Y')}")
        
        day_lessons = df[df['date'].dt.date == selected_day]
        
        if not day_lessons.empty:
            for _, lesson in day_lessons.iterrows():
                with st.expander(f"{lesson['studente']} - {lesson['materia']} ({lesson['duration']} ore)"):
                    st.write(f"**Studente:** {lesson['studente']}")
                    st.write(f"**Materia:** {lesson['materia']}")
                    st.write(f"**Durata:** {lesson['duration']} ore")
                    st.write(f"**Costo:** €{lesson['costo']:.2f}")
                    if lesson['notes']:
                        st.write(f"**Note:** {lesson['notes']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Modifica", key=f"edit_cal_lesson_{lesson['id']}"):
                            st.session_state.edit_lesson_id = lesson['id']
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Elimina", key=f"delete_cal_lesson_{lesson['id']}"):
                            success, message = delete_lesson(lesson['id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
        else:
            st.info(f"Nessuna lezione programmata per il {selected_day.strftime('%d/%m/%Y')}")
            if st.button("➕ Aggiungi lezione", key="add_lesson_from_calendar"):
                st.session_state.add_lesson_date = selected_day
                st.rerun()
    
    # Filtri per il report
    st.subheader('Report Statistiche')
    col1, col2 = st.columns(2)
    with col1:
        date_range = st.date_input('Filtra per periodo', [datetime.now().replace(day=1), datetime.now()])
    with col2:
        periodo = st.selectbox('Raggruppa per', ['Giornaliero', 'Settimanale', 'Mensile'])
    
    # Filtro per data
    filtered = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]
    
    if filtered.empty:
        st.warning('Nessuna lezione trovata nel periodo selezionato.')
        return
    
    # Raggruppamento per periodo
    if periodo == 'Giornaliero':
        grouped = filtered.groupby(pd.Grouper(key='date', freq='D')).sum(numeric_only=True)
    elif periodo == 'Settimanale':
        grouped = filtered.groupby(pd.Grouper(key='date', freq='W-MON')).sum(numeric_only=True)
    else:  # Mensile
        grouped = filtered.groupby(pd.Grouper(key='date', freq='M')).sum(numeric_only=True)
    
    # Visualizzazione grafico
    st.subheader('Andamento Costi')
    if not grouped.empty and 'costo' in grouped.columns:
        st.bar_chart(grouped['costo'])
    else:
        st.info('Dati insufficienti per generare il grafico.')
    
    # Dettaglio lezioni
    st.subheader('Dettaglio Lezioni')
    studenti_list = filtered['studente'].unique().tolist()
    if studenti_list:
        studente = st.selectbox('Filtra per studente', ['Tutti'] + studenti_list)
        if studente != 'Tutti':
            filtered = filtered[filtered['studente'] == studente]
    
    # Mostra tabella dettaglio
    if not filtered.empty:
        st.dataframe(filtered)
        
        # Funzione per esportare in Excel
        @st.cache_data
        def convert_to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()
        
        # Bottone per scaricare Excel
        excel_data = convert_to_excel(filtered)
        st.download_button(
            label='Esporta in Excel',
            data=excel_data,
            file_name='report_lezioni.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    main()