import datetime
import sqlite3
import win32gui
import win32process
import psutil
import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WindowsUsageTracker:
    def __init__(self):
        # Initialisation de la base de données
        self.conn = sqlite3.connect('usage_stats.db')
        self.create_tables()
        
        # Création de l'interface
        self.root = tk.Tk()
        self.root.title("Suivi du temps d'utilisation")
        self.root.geometry("800x600")
        self.root.iconphoto(False, tk.PhotoImage(file="app_icon.png"))  # Ajout de l'icône
        
        self.setup_gui()
        self.start_tracking()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER
            )
        ''')
        self.conn.commit()

    def setup_gui(self):
        # Création des onglets
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Onglet temps réel
        self.realtime_frame = ttk.Frame(notebook)
        notebook.add(self.realtime_frame, text='Temps Réel')
        
        # Onglet calendrier
        self.calendar_frame = ttk.Frame(notebook)
        notebook.add(self.calendar_frame, text='Calendrier')
        
        # Onglet statistiques
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text='Statistiques')

        self.setup_realtime_tab()
        self.setup_calendar_tab()
        self.setup_stats_tab()

    def setup_realtime_tab(self):
        # Affichage des moyennes
        self.averages_label = tk.Label(self.realtime_frame, text="", font=("Arial", 12))
        self.averages_label.pack(pady=10)
        
        # Liste des applications en cours
        self.app_listbox = tk.Listbox(self.realtime_frame, width=70, height=20)
        self.app_listbox.pack(pady=10)
        
        # Bouton de rafraîchissement
        refresh_btn = ttk.Button(self.realtime_frame, text="Rafraîchir", 
                                 command=self.update_current_apps)
        refresh_btn.pack(pady=5)

    def setup_calendar_tab(self):
        # Calendrier
        self.cal = calendar.Calendar()
        
        # Frame pour la navigation
        nav_frame = ttk.Frame(self.calendar_frame)
        nav_frame.pack(fill='x', pady=5)
        
        # Boutons de navigation
        prev_btn = ttk.Button(nav_frame, text="<<", command=self.prev_month)
        prev_btn.pack(side='left', padx=5)
        
        self.month_label = ttk.Label(nav_frame, text="")
        self.month_label.pack(side='left', padx=5)
        
        next_btn = ttk.Button(nav_frame, text=">>", command=self.next_month)
        next_btn.pack(side='left', padx=5)
        
        # Grille du calendrier
        self.calendar_grid = ttk.Frame(self.calendar_frame)
        self.calendar_grid.pack(fill='both', expand=True, pady=10)
        
        self.current_date = datetime.now()
        self.update_calendar()

    def setup_stats_tab(self):
        # Frame pour les graphiques
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.stats_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Boutons pour changer la période
        period_frame = ttk.Frame(self.stats_frame)
        period_frame.pack(fill='x', pady=5)
        
        ttk.Button(period_frame, text="Semaine", 
                  command=lambda: self.update_stats('week')).pack(side='left', padx=5)
        ttk.Button(period_frame, text="Mois", 
                  command=lambda: self.update_stats('month')).pack(side='left', padx=5)
        ttk.Button(period_frame, text="Année", 
                  command=lambda: self.update_stats('year')).pack(side='left', padx=5)

    def start_tracking(self):
        self.track_active_window()
        self.update_current_apps()
        self.update_averages()  # Mise à jour des moyennes
        self.update_stats('week')
        self.root.after(1000, self.start_tracking)

    def track_active_window(self):
        try:
            window = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(window)
            app_name = psutil.Process(pid).name()
            
            current_time = datetime.now()
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO app_usage (app_name, start_time, end_time, duration)
                VALUES (?, ?, ?, ?)
            ''', (app_name, current_time, current_time, 1))
            
            self.conn.commit()
        except:
            pass

    def update_current_apps(self):
        self.app_listbox.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT app_name, SUM(duration) as total_duration
            FROM app_usage
            WHERE start_time >= datetime('now', '-1 day')
            GROUP BY app_name
            ORDER BY total_duration DESC
        ''')
        
        results = cursor.fetchall()
        if not results:
            self.app_listbox.insert(tk.END, "Aucune donnée disponible")
            return
            
        for app_name, duration in results:
            minutes = duration // 60
            seconds = duration % 60
            self.app_listbox.insert(tk.END, 
                                    f"{app_name}: {minutes}min {seconds}s")

    def update_averages(self):
        cursor = self.conn.cursor()

        # Moyennes pour différentes périodes
        averages = {}
        periods = {
            'Jour': '1 day',
            'Semaine': '7 days',
            'Mois': '30 days',
            'Année': '365 days'
        }
        
        for label, duration in periods.items():
            cursor.execute(f'''
                SELECT AVG(duration)
                FROM app_usage
                WHERE start_time >= datetime('now', '-{duration}')
            ''')
            result = cursor.fetchone()[0]
            averages[label] = round(result / 3600, 2) if result else 0

        # Mise à jour du texte
        averages_text = "\n".join(
            [f"Moyenne {label} : {value} heures" for label, value in averages.items()]
        )
        self.averages_label.config(text=averages_text)

    def update_calendar(self):
        # Nettoyer la grille existante
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
            
        # En-têtes des jours
        days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        for i, day in enumerate(days):
            ttk.Label(self.calendar_grid, text=day).grid(row=0, column=i, pady=2)
            
        # Mise à jour du mois affiché
        self.month_label.config(
            text=f"{calendar.month_name[self.current_date.month]} {self.current_date.year}")
            
        # Remplissage du calendrier
        cal_days = self.cal.monthdatescalendar(self.current_date.year, 
                                                self.current_date.month)
        
        for week_num, week in enumerate(cal_days, 1):
            for day_num, day in enumerate(week):
                frame = ttk.Frame(self.calendar_grid, relief='solid')
                frame.grid(row=week_num, column=day_num, sticky='nsew', padx=1, pady=1)
                
                ttk.Label(frame, text=str(day.day)).pack()
                
                # Ajouter le temps total d'utilisation pour ce jour
                total_time = self.get_day_usage(day)
                if total_time > 0:
                    hours = total_time // 3600
                    minutes = (total_time % 3600) // 60
                    ttk.Label(frame, 
                              text=f"{hours}h {minutes}m").pack()

    def get_day_usage(self, date):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(duration)
            FROM app_usage
            WHERE date(start_time) = date(?)
        ''', (date.strftime('%Y-%m-%d'),))
        
        result = cursor.fetchone()[0]
        return result if result else 0

    def update_stats(self, period):
        self.ax1.clear()
        self.ax2.clear()
        
        if period == 'week':
            days = 7
            group_by = 'date(start_time)'
            format_str = '%Y-%m-%d'
        elif period == 'month':
            days = 30
            group_by = 'date(start_time)'
            format_str = '%Y-%m-%d'
        else:  # year
            days = 365
            group_by = "strftime('%Y-%m', start_time)"
            format_str = '%Y-%m'
            
        cursor = self.conn.cursor()
        
        # Statistiques globales
        cursor.execute(f'''
            SELECT {group_by} as period, SUM(duration) as total
            FROM app_usage
            WHERE start_time >= datetime('now', '-{days} days')
            GROUP BY period
            ORDER BY period
        ''')
        
        results = cursor.fetchall()
        if not results:
            self.ax1.text(0.5, 0.5, 'Aucune donnée disponible', 
                          ha='center', va='center')
            self.ax2.text(0.5, 0.5, 'Aucune donnée disponible', 
                          ha='center', va='center')
        else:
            periods, totals = zip(*results)
            self.ax1.bar(periods, totals)
            self.ax1.set_title(f'Utilisation totale par {period}')
            self.ax1.tick_params(axis='x', rotation=45)
            
            # Top applications
            cursor.execute(f'''
                SELECT app_name, SUM(duration) as total
                FROM app_usage
                WHERE start_time >= datetime('now', '-{days} days')
                GROUP BY app_name
                ORDER BY total DESC
                LIMIT 5
            ''')
            
            app_results = cursor.fetchall()
            if app_results:
                apps, app_totals = zip(*app_results)
                self.ax2.pie(app_totals, labels=apps, autopct='%1.1f%%')
                self.ax2.set_title('Top 5 applications')
            else:
                self.ax2.text(0.5, 0.5, 'Aucune donnée disponible', 
                              ha='center', va='center')
        
        self.fig.tight_layout()
        self.canvas.draw()

    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, 
                                                          month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()

    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, 
                                                          month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WindowsUsageTracker()
    app.run()
