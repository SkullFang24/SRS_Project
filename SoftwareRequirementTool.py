import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class RequirementTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Software Requirement Engineering Tool")
        self.root.geometry("1366x768")
        self.root.minsize(1366,768)

        self.conn = sqlite3.connect("requirements.db")
        self.create_tables()

        self.notebook = ttk.Notebook(self.root)

        self.elicitate_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.traceability_tab = ttk.Frame(self.notebook)
        self.status_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.elicitate_tab, text='Elicitate Requirement')
        self.notebook.add(self.analysis_tab, text='Analyze Requirements')
        self.notebook.add(self.traceability_tab, text='Trace Requirements')
        self.notebook.add(self.status_tab, text='Track Requirement Status')

        self.notebook.pack(expand=1, fill="both")

        self.create_elicitate_tab()
        self.create_analysis_tab()
        self.create_traceability_tab()
        self.create_status_tab()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                priority TEXT NOT NULL,
                date_created TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traceability_matrix (
                requirement_id INTEGER,
                traced_to INTEGER,
                FOREIGN KEY(requirement_id) REFERENCES requirements(id),
                FOREIGN KEY(traced_to) REFERENCES requirements(id),
                UNIQUE(requirement_id, traced_to)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_tracker (
                requirement_id INTEGER PRIMARY KEY,
                status TEXT NOT NULL,
                FOREIGN KEY(requirement_id) REFERENCES requirements(id)
            )
        ''')
        self.conn.commit()

    def create_elicitate_tab(self):
        frame = ttk.Frame(self.elicitate_tab)
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Enter Requirement Text:").grid(row=0, column=0, sticky='w')
        self.requirement_text_entry = ttk.Entry(frame, width=50)
        self.requirement_text_entry.grid(row=0, column=1, pady=10)

        ttk.Label(frame, text="Priority:").grid(row=1, column=0, sticky='w')
        self.priority_combobox = ttk.Combobox(frame, values=["High", "Medium", "Low"], state="readonly")
        self.priority_combobox.grid(row=1, column=1, pady=10)

        ttk.Button(frame, text="Add Requirement", command=self.elicitate_requirement).grid(row=2, column=0, columnspan=2, pady=20)

    def elicitate_requirement(self):
        requirement_text = self.requirement_text_entry.get()
        priority = self.priority_combobox.get()

        if requirement_text and priority:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO requirements (text, priority, date_created, status)
                VALUES (?, ?, ?, ?)
            ''', (requirement_text, priority, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Pending"))
            requirement_id = cursor.lastrowid

            self.conn.commit()

            messagebox.showinfo("Success", f"Requirement {requirement_id} added successfully.")
        else:
            messagebox.showwarning("Error", "Please enter both requirement text and priority.")

    def create_analysis_tab(self):
        frame = ttk.Frame(self.analysis_tab)
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Analyze Requirements:").grid(row=0, column=0, sticky='w', pady=10)

        ttk.Button(frame, text="Perform Analysis", command=self.perform_analysis).grid(row=1, column=0, pady=20)

        self.analysis_result_label = ttk.Label(frame, text="")
        self.analysis_result_label.grid(row=2, column=0)

    def perform_analysis(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM requirements WHERE status="Pending"')
        pending_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM requirements WHERE status="Completed"')
        completed_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM requirements WHERE status="In Progress"')
        in_progress_count = cursor.fetchone()[0]

        analysis_result = f"Pending Requirements: {pending_count}\nCompleted Requirements: {completed_count}\nIn Progress Requirements: {in_progress_count}"
        self.analysis_result_label.config(text=analysis_result)

    def create_traceability_tab(self):
        frame = ttk.Frame(self.traceability_tab)
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Trace Requirements:").grid(row=0, column=0, sticky='w', pady=10)
        self.treeview = ttk.Treeview(frame, columns=('ID', 'Text', 'Priority', 'Status'))
        
        self.treeview['show'] = 'headings'
        self.treeview.column('ID', anchor=tk.W, width=50)
        self.treeview.column('Text', anchor=tk.W, width=300)
        self.treeview.column('Priority', anchor=tk.W, width=100)
        self.treeview.column('Status', anchor=tk.W, width=100)

        self.treeview.heading('ID', text='ID', anchor=tk.W)
        self.treeview.heading('Text', text='Text', anchor=tk.W)
        self.treeview.heading('Priority', text='Priority', anchor=tk.W)
        self.treeview.heading('Status', text='Status', anchor=tk.W)

        self.treeview.grid(row=1, column=0, pady=10)

        ttk.Label(frame, text="Select Source Requirement ID:").grid(row=2, column=0, sticky='w', pady=10)
        self.source_requirement_var = tk.StringVar()
        self.source_requirement_combobox = ttk.Combobox(frame, textvariable=self.source_requirement_var, state="readonly")
        self.source_requirement_combobox.grid(row=2, column=1, pady=10)

        ttk.Label(frame, text="Select Traced Requirement IDs:").grid(row=3, column=0, sticky='w', pady=10)
        self.traced_requirement_var = tk.StringVar()
        self.traced_requirement_entry = ttk.Entry(frame, textvariable=self.traced_requirement_var)
        self.traced_requirement_entry.grid(row=3, column=1, pady=10)

        ttk.Button(frame, text="Trace Requirements", command=self.trace_requirements).grid(row=4, column=0, columnspan=2, pady=20)

        self.populate_requirements_combobox()

    def populate_requirements_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, text, priority, status FROM requirements')
        requirements = cursor.fetchall()

        requirement_ids = [str(requirement[0]) for requirement in requirements]
        self.source_requirement_combobox['values'] = requirement_ids

        for requirement in requirements:
            self.treeview.insert('', 'end', values=requirement)


    def trace_requirements(self):
        source_requirement_id = self.source_requirement_var.get()
        traced_requirement_ids = self.traced_requirement_var.get().split(',')

        if source_requirement_id and traced_requirement_ids:
            cursor = self.conn.cursor()
            try:
                cursor.execute('BEGIN TRANSACTION')
                for traced_requirement_id in traced_requirement_ids:
                    cursor.execute('''
                        INSERT INTO traceability_matrix (requirement_id, traced_to)
                        VALUES (?, ?)
                    ''', (source_requirement_id, traced_requirement_id))
                cursor.execute('COMMIT')

                for item in self.treeview.get_children():
                    self.treeview.delete(item)

                self.populate_requirements_combobox()

                messagebox.showinfo("Success", "Traceability relationships added successfully.")
            except sqlite3.IntegrityError:
                cursor.execute('ROLLBACK')
                messagebox.showwarning("Error", "Traceability relationship already exists.")
        else:
            messagebox.showwarning("Error", "Please select source requirement and provide traced requirement IDs.")

    def create_status_tab(self):
        frame = ttk.Frame(self.status_tab)
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Track Requirement Status:").grid(row=0, column=0, sticky='w', pady=10)

        ttk.Label(frame, text="Select Requirement ID:").grid(row=1, column=0, sticky='w', pady=10)
        self.track_status_requirement_var = tk.StringVar()
        self.track_status_requirement_combobox = ttk.Combobox(frame, textvariable=self.track_status_requirement_var, state="readonly")
        self.track_status_requirement_combobox.grid(row=1, column=1, pady=10)

        ttk.Label(frame, text="Select New Status:").grid(row=2, column=0, sticky='w', pady=10)
        self.new_status_var = tk.StringVar()
        self.new_status_combobox = ttk.Combobox(frame, values=["Pending", "In Progress", "Completed"], textvariable=self.new_status_var, state="readonly")
        self.new_status_combobox.grid(row=2, column=1, pady=10)

        ttk.Button(frame, text="Update Status", command=self.update_requirement_status).grid(row=3, column=0, columnspan=2, pady=20)

        self.populate_status_combobox()

    def populate_status_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM requirements')
        requirement_ids = [str(requirement[0]) for requirement in cursor.fetchall()]
        self.track_status_requirement_combobox['values'] = requirement_ids

    def update_requirement_status(self):
        requirement_id = self.track_status_requirement_var.get()
        new_status = self.new_status_var.get()

        if requirement_id and new_status:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE requirements SET status=? WHERE id=?', (new_status, requirement_id))
            self.conn.commit()
            messagebox.showinfo("Success", f"Status of Requirement {requirement_id} updated to {new_status}.")
        else:
            messagebox.showwarning("Error", "Please select a requirement and provide a new status.")


if __name__ == "__main__":
    root = tk.Tk()
    app = RequirementTool(root)
    root.mainloop()
