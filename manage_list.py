import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser, filedialog
import json
import os
import shutil
from pathlib import Path
import datetime
import subprocess
import threading

DATA_DIR = Path("data")
BACKUP_DIR = Path("backups")
LIST_FILE = DATA_DIR / "_list.json"
EDITORS_FILE = DATA_DIR / "_editors.json"
REQS_FILE = DATA_DIR / "_requirements.json"
SETTINGS_FILE = DATA_DIR / "_settings.json"

class ListManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GDPS List Manager - Ultimate Edition")
        self.geometry("1000x800")

        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Menu Bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Data", command=self.backup_data)
        file_menu.add_command(label="Restore Backup", command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.init_settings_tab()
        self.init_levels_tab()
        self.init_editors_tab()
        self.init_reqs_tab()
        
        self.load_data()

    def load_data(self):
        # Ensure directories
        DATA_DIR.mkdir(exist_ok=True)
        BACKUP_DIR.mkdir(exist_ok=True)

        # Settings
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r") as f:
                self.settings_data = json.load(f)
        else:
            self.settings_data = {
                "title": "CCL - GDPS List",
                "primary_color": "#003366",
                "telegram_link": "https://t.me/chaigdpscl",
                "submit_link": "#",
                "list_name_header": "CCL"
            }
        
        # List Order
        if LIST_FILE.exists():
            with open(LIST_FILE, "r") as f:
                self.level_files = json.load(f)
        else:
            self.level_files = []

        # Editors
        if EDITORS_FILE.exists():
            with open(EDITORS_FILE, "r") as f:
                self.editors_data = json.load(f)
        else:
            self.editors_data = []

        # Requirements
        if REQS_FILE.exists():
            with open(REQS_FILE, "r") as f:
                self.reqs_data = json.load(f)
        else:
            self.reqs_data = []

        self.refresh_settings_ui()
        self.refresh_levels_list()
        self.refresh_editors_ui()
        self.refresh_reqs_ui()

    def backup_data(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"backup_{ts}"
        backup_path.mkdir()
        for f in DATA_DIR.glob("*"):
            if f.is_file():
                shutil.copy(f, backup_path)
        messagebox.showinfo("Backup", f"Backup created at:\n{backup_path}")

    def restore_backup(self):
        backup_path = filedialog.askdirectory(initialdir=BACKUP_DIR, title="Select Backup Folder")
        if not backup_path: return
        
        if messagebox.askyesno("Restore", "This will OVERWRITE current data. Continue?"):
            for f in Path(backup_path).glob("*"):
                if f.is_file():
                    shutil.copy(f, DATA_DIR)
            self.load_data()
            messagebox.showinfo("Restore", "Data restored successfully!")

    def deploy_to_github(self):
        self.save_everything()
        repo_url = self.settings_data.get("github_url", "").strip()
        
        if not repo_url:
            messagebox.showerror("Error", "Please enter a GitHub Repository URL in Settings first.")
            return

        def run_git():
            try:
                # 1. Check Git
                subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except (FileNotFoundError, subprocess.CalledProcessError):
                messagebox.showerror("Error", "Git is not installed or not found in PATH.")
                return

            try:
                # 2. Smart Deploy
                commands = []
                
                # Check if already initialized
                is_initialized = (DATA_DIR.parent / ".git").exists()
                
                if not is_initialized:
                    commands.append(["git", "init"])
                    commands.append(["git", "branch", "-M", "main"])

                # Check remote
                current_remote = ""
                if is_initialized:
                    try:
                        res = subprocess.run(["git", "remote", "get-url", "origin"], stdout=subprocess.PIPE, text=True)
                        current_remote = res.stdout.strip()
                    except:
                        pass
                
                if current_remote != repo_url:
                    if current_remote:
                        commands.append(["git", "remote", "remove", "origin"])
                    commands.append(["git", "remote", "add", "origin", repo_url])

                # Standard update flow
                commands.append(["git", "add", "."])
                commands.append(["git", "commit", "-m", f"Update site data {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"])
                commands.append(["git", "push", "-u", "origin", "main"])
                
                log = ""
                for cmd in commands:
                    # Run command
                    try:
                        if cmd[0] == "git" and cmd[1] == "push":
                             # Push might take time, let's treat it carefully, maybe capture output better
                             pass

                        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        log += f"> {' '.join(cmd)}\n"
                        if result.returncode != 0:
                            # Ignore "nothing to commit"
                            if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                                log += "  (Nothing to commit)\n"
                            elif "remote origin already exists" in result.stderr:
                                pass
                            else:
                                log += f"{result.stderr}\n"
                    except Exception as ex:
                        log += f"Error running {cmd}: {ex}\n"

                messagebox.showinfo("Deploy Result", f"Update Process Finished.\n\nLog:\n{log}")
                
            except Exception as e:
                messagebox.showerror("Deploy Error",str(e))

        threading.Thread(target=run_git).start()

    def save_everything(self):
        # 1. Save Settings
        self.settings_data["title"] = self.ent_title.get()
        self.settings_data["list_name_header"] = self.ent_header.get()
        self.settings_data["telegram_link"] = self.ent_telegram.get()
        self.settings_data["submit_link"] = self.ent_submit.get()
        self.settings_data["github_url"] = self.ent_github.get()
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings_data, f, indent=4)

        # 2. Save List Order
        with open(LIST_FILE, "w") as f:
            json.dump(self.level_files, f, indent=4)
        
        # 3. Save Editors
        try:
            editors_text = self.editors_text.get("1.0", tk.END).strip()
            self.editors_data = json.loads(editors_text)
            with open(EDITORS_FILE, "w") as f:
                json.dump(self.editors_data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error Saving Editors", f"Invalid JSON in Editors tab:\n{e}")
            return

        # 4. Save Requirements
        reqs_text = self.reqs_text.get("1.0", tk.END).strip()
        self.reqs_data = [line for line in reqs_text.split('\n') if line.strip()]
        with open(REQS_FILE, "w") as f:
            json.dump(self.reqs_data, f, indent=4)

        messagebox.showinfo("Success", "All settings SAVED! Check the website (Refresh F5).")

    # --- 1. Settings Tab ---
    def init_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Site Settings")

        ttk.Label(frame, text="Global Website Settings", font=("Arial", 16, "bold")).pack(pady=10)
        
        form = ttk.Frame(frame)
        form.pack(pady=10)

        def add_field(label, var_name):
            ttk.Label(form, text=label).grid(sticky="e", padx=5, pady=5)
            ent = ttk.Entry(form, width=50)
            ent.grid(row=form.grid_size()[1]-1, column=1, padx=5, pady=5)
            setattr(self, var_name, ent)

        add_field("Website Tab Title:", "ent_title")
        add_field("Header Name (e.g. CCL):", "ent_header")
        add_field("Telegram/Discord Link:", "ent_telegram")
        add_field("Submit Record Link:", "ent_submit")
        add_field("GitHub Repository URL:", "ent_github")
        
        # Color Picker
        ttk.Label(form, text="Primary Color:").grid(sticky="e", padx=5, pady=5)
        self.btn_color = tk.Button(form, text="Pick Color", command=self.pick_color, bg="white")
        self.btn_color.grid(row=form.grid_size()[1]-1, column=1, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="SAVE ALL GLOBAL SETTINGS", command=self.save_everything).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="SAVE & DEPLOY TO GITHUB", command=self.deploy_to_github).pack(side="left", padx=10)

    def refresh_settings_ui(self):
        self.ent_title.delete(0, tk.END)
        self.ent_title.insert(0, self.settings_data.get("title", ""))
        
        self.ent_header.delete(0, tk.END)
        self.ent_header.insert(0, self.settings_data.get("list_name_header", ""))
        
        self.ent_telegram.delete(0, tk.END)
        self.ent_telegram.insert(0, self.settings_data.get("telegram_link", ""))
        
        self.ent_submit.delete(0, tk.END)
        self.ent_submit.insert(0, self.settings_data.get("submit_link", ""))

        self.ent_github.delete(0, tk.END)
        self.ent_github.insert(0, self.settings_data.get("github_url", ""))

        c = self.settings_data.get("primary_color", "#0066ff")
        self.btn_color.config(bg=c, text=c)

    def pick_color(self):
        color = colorchooser.askcolor(title="Choose Primary Color")
        if color[1]:
            self.settings_data["primary_color"] = color[1]
            self.btn_color.config(bg=color[1], text=color[1])

    # --- 2. Levels Tab ---
    def init_levels_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Levels")

        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(toolbar, text="Add Level", command=self.add_level).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Edit Level Details", command=self.edit_level).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Delete Level", command=self.delete_level).pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(toolbar, text="Move Up", command=lambda: self.move_level(-1)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Move Down", command=lambda: self.move_level(1)).pack(side="left", padx=2)
        
        ttk.Button(toolbar, text="SAVE LIST ORDER", command=self.save_everything).pack(side="right", padx=5)

        # Search
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill="x", padx=5)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_levels)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=5)

        # Listbox
        self.levels_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, font=("Consolas", 10))
        self.levels_listbox.pack(expand=True, fill="both", padx=5, pady=5)
        self.levels_listbox.bind("<Double-Button-1>", lambda e: self.edit_level())
        
        # Status Bar
        self.status = ttk.Label(frame, text="Ready", relief=tk.SUNKEN, anchor="w")
        self.status.pack(fill="x")

    def filter_levels(self, *args):
        query = self.search_var.get().lower()
        self.levels_listbox.delete(0, tk.END)
        for i, fname in enumerate(self.level_files):
            if query in fname.lower():
                display = self._get_level_display(i, fname)
                self.levels_listbox.insert(tk.END, display)
            else:
                # Also check name in file
                try:
                    with open(DATA_DIR / f"{fname}.json", "r") as f:
                        data = json.load(f)
                        if query in data.get("name", "").lower():
                            display = self._get_level_display(i, fname)
                            self.levels_listbox.insert(tk.END, display)
                except:
                    pass

    def _get_level_display(self, i, fname):
        try:
            with open(DATA_DIR / f"{fname}.json", "r") as f:
                data = json.load(f)
                name = data.get('name', 'Unknown')
                return f"#{i+1} - {name} ({fname})"
        except:
            return f"#{i+1} - {fname} (Error loading JSON)"

    def refresh_levels_list(self):
        self.search_var.set("") # Clear filter to show all
        self.levels_listbox.delete(0, tk.END)
        for i, fname in enumerate(self.level_files):
            display = self._get_level_display(i, fname)
            self.levels_listbox.insert(tk.END, display)
        self.status.config(text=f"Total Levels: {len(self.level_files)}")

    def add_level(self):
        filename = simpledialog.askstring("New Level", "Enter filename (e.g. MyLevel):")
        if not filename: return
        filename = filename.strip()
        if filename in self.level_files:
            messagebox.showerror("Error", "Level filename already exists!")
            return
        
        # Create default data
        default_data = {
            "id": 0,
            "name": filename,
            "author": "Author",
            "creators": [],
            "verifier": "Verifier",
            "verification": "https://youtu.be/example",
            "percentToQualify": 100,
            "password": "Free to Copy",
            "records": []
        }
        
        with open(DATA_DIR / f"{filename}.json", "w") as f:
            json.dump(default_data, f, indent=4)
        
        self.level_files.append(filename)
        self.refresh_levels_list()
        self.save_everything() 
        self.edit_level_dialog(filename)

    def edit_level(self):
        sel = self.levels_listbox.curselection()
        if not sel: return
        # Handle Move/Edit when filtered
        # Simple approach: get the filename from the text string
        item_text = self.levels_listbox.get(sel[0])
        # Format: #1 - Name (Filename)
        # Extract Filename from parens at end
        filename = item_text.split("(")[-1].replace(")", "")
        self.edit_level_dialog(filename)

    def delete_level(self):
        sel = self.levels_listbox.curselection()
        if not sel: return
        item_text = self.levels_listbox.get(sel[0])
        filename = item_text.split("(")[-1].replace(")", "")
        
        if messagebox.askyesno("Confirm", f"Delete {filename}? This will remove the JSON file."):
            try:
                os.remove(DATA_DIR / f"{filename}.json")
            except OSError:
                pass
            if filename in self.level_files:
                self.level_files.remove(filename)
            self.refresh_levels_list()
            self.save_everything() 

    def move_level(self, direction):
        # Only allowed if NOT filtering
        if self.search_var.get():
            messagebox.showwarning("Warning", "Cannot move levels while searching. Clear search first.")
            return

        sel = self.levels_listbox.curselection()
        if not sel: return
        idx = sel[0]
        new_idx = idx + direction
        if 0 <= new_idx < len(self.level_files):
            self.level_files[idx], self.level_files[new_idx] = self.level_files[new_idx], self.level_files[idx]
            self.refresh_levels_list()
            self.levels_listbox.selection_set(new_idx)

    def edit_level_dialog(self, filename):
        file_path = DATA_DIR / f"{filename}.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except:
            messagebox.showerror("Error", "Could not load level file")
            return

        win = tk.Toplevel(self)
        win.title(f"Editing {filename}")
        win.geometry("800x800")

        # Tabs in Editor
        nb = ttk.Notebook(win)
        nb.pack(expand=True, fill="both", padx=5, pady=5)
        
        tab_details = ttk.Frame(nb)
        tab_records = ttk.Frame(nb)
        nb.add(tab_details, text="Details")
        nb.add(tab_records, text="Records")

        # --- Details Tab ---
        entries = {}
        
        r = 0
        def add_entry(parent, label, key, default=""):
            nonlocal r
            ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", pady=5, padx=5)
            e = ttk.Entry(parent, width=50)
            e.insert(0, str(data.get(key, default)))
            e.grid(row=r, column=1, sticky="ew", padx=5, pady=5)
            entries[key] = e
            r += 1
            return e

        add_entry(tab_details, "Level Name:", "name")
        add_entry(tab_details, "Level ID:", "id")
        add_entry(tab_details, "Password:", "password")
        add_entry(tab_details, "Author:", "author")
        add_entry(tab_details, "Creators (comma sep):", "_creators", ",".join(data.get("creators", [])))
        add_entry(tab_details, "Verifier:", "verifier")
        add_entry(tab_details, "Verification Link (YouTube):", "verification")
        add_entry(tab_details, "Percent to Qualify:", "percentToQualify", "100")
        add_entry(tab_details, "Points (-1 = Auto):", "points", "-1")
        
        tab_details.columnconfigure(1, weight=1)

        # --- Records Tab ---
        ttk.Label(tab_records, text="Manage Records").pack(pady=5)
        
        rec_toolbar = ttk.Frame(tab_records)
        rec_toolbar.pack(fill="x")
        
        rec_list_frame = ttk.Frame(tab_records)
        rec_list_frame.pack(fill="both", expand=True)
        
        records_list = tk.Listbox(rec_list_frame, font=("Consolas", 10))
        records_list.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(rec_list_frame, orient="vertical", command=records_list.yview)
        sb.pack(side="right", fill="y")
        records_list.config(yscrollcommand=sb.set)

        current_records = data.get("records", [])

        def refresh_records_ui():
            records_list.delete(0, tk.END)
            for i, rec in enumerate(current_records):
                records_list.insert(tk.END, f"{i+1}. {rec['user']} | {rec['percent']}% | {rec['hz']}Hz | {rec.get('link','')}")

        refresh_records_ui()

        def add_record():
            d = tk.Toplevel(win)
            d.title("New Record")
            
            f = ttk.Frame(d, padding=10)
            f.pack()
            
            ttk.Label(f, text="User:").grid(row=0, column=0)
            e_user = ttk.Entry(f)
            e_user.grid(row=0, column=1)
            
            ttk.Label(f, text="Video Link:").grid(row=1, column=0)
            e_link = ttk.Entry(f)
            e_link.grid(row=1, column=1)
            
            ttk.Label(f, text="Percent:").grid(row=2, column=0)
            e_pct = ttk.Entry(f)
            e_pct.insert(0, "100")
            e_pct.grid(row=2, column=1)
            
            ttk.Label(f, text="Hz:").grid(row=3, column=0)
            e_hz = ttk.Entry(f)
            e_hz.insert(0, "360")
            e_hz.grid(row=3, column=1)
            
            def save_rec():
                try:
                    current_records.append({
                        "user": e_user.get(),
                        "link": e_link.get(),
                        "percent": int(e_pct.get()),
                        "hz": int(e_hz.get()),
                        "mobile": False 
                    })
                    refresh_records_ui()
                    d.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Percent and Hz must be numbers")

            ttk.Button(f, text="Add", command=save_rec).grid(row=4, columnspan=2, pady=10)

        def delete_record():
            sel = records_list.curselection()
            if not sel: return
            if messagebox.askyesno("Delete", "Delete selected record?"):
                current_records.pop(sel[0])
                refresh_records_ui()

        ttk.Button(rec_toolbar, text="Add Record", command=add_record).pack(side="left", padx=5)
        ttk.Button(rec_toolbar, text="Delete Selected", command=delete_record).pack(side="left", padx=5)

        def save_level():
            # Update data dict
            data["name"] = entries["name"].get()
            try:
                data["id"] = int(entries["id"].get())
                data["percentToQualify"] = int(entries["percentToQualify"].get())
                data["points"] = float(entries["points"].get())
            except ValueError:
                messagebox.showerror("Error", "ID and Percent must be integers, Points can be decimal")
                return

            data["password"] = entries["password"].get()
            data["author"] = entries["author"].get()
            data["verifier"] = entries["verifier"].get()
            data["verification"] = entries["verification"].get()
            
            creators_str = entries["_creators"].get()
            data["creators"] = [c.strip() for c in creators_str.split(",") if c.strip()]
            
            data["records"] = current_records
            
            # Write to file
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            
            # Refresh main list
            self.refresh_levels_list()
            messagebox.showinfo("Saved", f"Level '{filename}' saved successfully.")
            win.destroy()

        ttk.Button(win, text="SAVE THIS LEVEL", command=save_level).pack(pady=10, fill="x", padx=10)

    # --- 3. Editors Tab ---
    def init_editors_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Editors")
        
        ttk.Label(frame, text="Edit Editors JSON directly (Advanced):").pack(anchor="w", padx=5, pady=5)
        self.editors_text = tk.Text(frame)
        self.editors_text.pack(expand=True, fill="both", padx=5, pady=5)
        
    def refresh_editors_ui(self):
        self.editors_text.delete("1.0", tk.END)
        self.editors_text.insert("1.0", json.dumps(self.editors_data, indent=4))

    # --- 4. Requirements Tab ---
    def init_reqs_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Requirements")
        
        ttk.Label(frame, text="Edit Requirements (One per line):").pack(anchor="w", padx=5, pady=5)
        self.reqs_text = tk.Text(frame)
        self.reqs_text.pack(expand=True, fill="both", padx=5, pady=5)

    def refresh_reqs_ui(self):
        self.reqs_text.delete("1.0", tk.END)
        self.reqs_text.insert("1.0", "\n".join(self.reqs_data))

if __name__ == "__main__":
    app = ListManager()
    app.mainloop()
