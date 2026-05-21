import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pathlib import Path
import threading
import json
from datetime import datetime


class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        self.root.state("zoomed")
        
        # Color Palette
        self.DARK_BG = "#1a1a1a"
        self.GREY_BG = "#2b2b2b"
        self.GREY_LIGHT = "#404040"
        self.RUBY_RED = "#e0115f"
        self.BLACKISH_RED = "#4a0000"
        self.TEXT_COLOR = "#ffffff"
        self.TEXT_MUTED = "#cccccc"
        
        # Configure root window
        self.root.configure(bg=self.DARK_BG)
        
        # Current selection
        self.selected_folder = tk.StringVar(value="")
        self.destination_folder = tk.StringVar(value="")
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI."""
        # Title Section
        title_frame = tk.Frame(self.root, bg=self.BLACKISH_RED)
        title_frame.pack(fill=tk.X, pady=0)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 FILE ORGANIZER",
            font=("Helvetica", 24, "bold"),
            bg=self.BLACKISH_RED,
            fg=self.RUBY_RED
        )
        title_label.pack(pady=15)
        
        # Main Content Frame with scrolling support
        container_frame = tk.Frame(self.root, bg=self.DARK_BG)
        container_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.canvas = tk.Canvas(
            container_frame,
            bg=self.DARK_BG,
            highlightthickness=0,
            yscrollincrement=20
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(container_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        content_frame = tk.Frame(self.canvas, bg=self.DARK_BG)
        self.canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        content_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        # Folder Selection Section
        folder_label = tk.Label(
            content_frame,
            text="📂 Select Target Folder",
            font=("Helvetica", 12, "bold"),
            bg=self.DARK_BG,
            fg=self.RUBY_RED
        )
        folder_label.pack(anchor="w", pady=(0, 10))
        
        folder_frame = tk.Frame(content_frame, bg=self.GREY_BG)
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.selected_folder,
            font=("Helvetica", 10),
            bg="#292929",
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0,
            width=70
        )
        self.folder_entry.pack(fill=tk.X, padx=10, pady=(10, 3))

        folder_hint = tk.Label(
            folder_frame,
            text="Paste source folder path here or use Browse",
            font=("Helvetica", 8),
            bg=self.GREY_BG,
            fg=self.TEXT_MUTED,
            anchor="w"
        )
        folder_hint.pack(fill=tk.X, padx=10)
        
        browse_btn = self.create_button(
            content_frame,
            "Browse Folder",
            self.select_folder,
            bg=self.RUBY_RED
        )
        browse_btn.pack(fill=tk.X, pady=(0, 15))
        
        # Destination Folder Section (for dump option)
        dest_label = tk.Label(
            content_frame,
            text="📂 Select Destination Folder (for Dump option)",
            font=("Helvetica", 12, "bold"),
            bg=self.DARK_BG,
            fg=self.RUBY_RED
        )
        dest_label.pack(anchor="w", pady=(0, 10))
        
        dest_frame = tk.Frame(content_frame, bg=self.GREY_BG)
        dest_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.dest_entry = tk.Entry(
            dest_frame,
            textvariable=self.destination_folder,
            font=("Helvetica", 10),
            bg="#292929",
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0,
            width=70
        )
        self.dest_entry.pack(fill=tk.X, padx=10, pady=(10, 3))

        dest_hint = tk.Label(
            dest_frame,
            text="Paste destination folder path here or use Browse",
            font=("Helvetica", 8),
            bg=self.GREY_BG,
            fg=self.TEXT_MUTED,
            anchor="w"
        )
        dest_hint.pack(fill=tk.X, padx=10)
        
        dest_browse_btn = self.create_button(
            content_frame,
            "Browse Destination",
            self.select_destination_folder,
            bg=self.RUBY_RED
        )
        dest_browse_btn.pack(fill=tk.X, pady=(0, 20))
        
        # Options Section
        options_label = tk.Label(
            content_frame,
            text="⚙️  Select Action",
            font=("Helvetica", 12, "bold"),
            bg=self.DARK_BG,
            fg=self.RUBY_RED
        )
        options_label.pack(anchor="w", pady=(0, 10))
        
        # Radio buttons
        self.selected_option = tk.StringVar(value="dump")
        
        options_frame = tk.Frame(content_frame, bg=self.DARK_BG)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        options = [
            ("Dump'em in a folder (collect all files)", "dump"),
            ("Delete all files in a folder", "delete"),
            ("Recover all previously deleted files", "recover"),
        ]
        
        for text, value in options:
            rb = tk.Radiobutton(
                options_frame,
                text=text,
                variable=self.selected_option,
                value=value,
                font=("Helvetica", 10),
                bg=self.DARK_BG,
                fg=self.TEXT_COLOR,
                selectcolor=self.GREY_LIGHT,
                activebackground=self.DARK_BG,
                activeforeground=self.RUBY_RED
            )
            rb.pack(anchor="w", pady=5)
        
        # Action Buttons
        button_frame = tk.Frame(content_frame, bg=self.DARK_BG)
        button_frame.pack(fill=tk.X, pady=20)
        
        execute_btn = self.create_button(
            button_frame,
            "▶ Execute",
            self.execute_action,
            bg=self.RUBY_RED,
            width=15
        )
        execute_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = self.create_button(
            button_frame,
            "↻ Reset",
            self.reset_form,
            bg=self.GREY_LIGHT,
            width=15
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress/Status Section
        status_label = tk.Label(
            content_frame,
            text="📊 Status",
            font=("Helvetica", 12, "bold"),
            bg=self.DARK_BG,
            fg=self.RUBY_RED
        )
        status_label.pack(anchor="w", pady=(10, 5))
        
        status_frame = tk.Frame(content_frame, bg=self.GREY_BG)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable text widget for status
        scrollbar = ttk.Scrollbar(status_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.status_text = tk.Text(
            status_frame,
            height=8,
            bg=self.GREY_BG,
            fg=self.TEXT_MUTED,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT,
            bd=0
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.status_text.yview)
        
        # Configure text tags for colored output
        self.status_text.tag_config("success", foreground="#00ff00")
        self.status_text.tag_config("error", foreground="#ff4444")
        self.status_text.tag_config("warning", foreground="#ffaa00")
        self.status_text.tag_config("info", foreground=self.RUBY_RED)
        
        self.log_status("Ready to organize files!", "info")
    
    def create_button(self, parent, text, command, bg, width=None):
        """Create a styled button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Helvetica", 10, "bold"),
            bg=bg,
            fg=self.TEXT_COLOR if bg == self.RUBY_RED else "#000000",
            activebackground=self.RUBY_RED if bg == self.RUBY_RED else "#555555",
            activeforeground=self.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            width=width,
            cursor="hand2"
        )
        return btn
    
    def select_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(title="Select Target Folder")
        if folder:
            self.selected_folder.set(folder)
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.log_status(f"Selected: {folder}", "success")
    
    def select_destination_folder(self):
        """Open destination folder selection dialog."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_folder.set(folder)
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)
            self.log_status(f"Destination selected: {folder}", "success")

    def log_status(self, message, tag="info"):
        """Add message to status text."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n", tag)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()

    def reset_form(self):
        """Reset the form."""
        self.selected_folder.set("")
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, "")
        self.destination_folder.set("")
        self.dest_entry.delete(0, tk.END)
        self.dest_entry.insert(0, "")
        self.selected_option.set("dump")
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.log_status("Form reset. Ready to organize files!", "info")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def execute_action(self):
        """Execute the selected action."""
        action = self.selected_option.get()
        
        if action == "dump":
            if not self.selected_folder.get():
                messagebox.showerror("Error", "Please select a source folder first!")
                return
            if not self.destination_folder.get():
                messagebox.showerror("Error", "Please select a destination folder first!")
                return
        elif action in ["delete", "recover"]:
            if action == "delete" and not self.selected_folder.get():
                messagebox.showerror("Error", "Please select a folder first!")
                return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "An operation is already in progress!")
            return
        
        if action == "dump":
            # Run in separate thread to prevent GUI freezing
            thread = threading.Thread(target=self.collect_all_files)
            thread.start()
        elif action == "delete":
            thread = threading.Thread(target=self.delete_all_files)
            thread.start()
        elif action == "recover":
            thread = threading.Thread(target=self.recover_deleted_files)
            thread.start()
    
    def collect_all_files(self):
        """Collect all files from source folder and dump them into destination folder."""
        try:
            self.is_processing = True
            self.log_status("🔄 Starting file collection...", "info")
            
            source_folder = self.selected_folder.get()
            source_path = Path(source_folder).resolve()
            dest_path = Path(self.destination_folder.get()).resolve()
            
            self.log_status(f"📥 Copying files from: {source_path}", "info")
            self.log_status(f"📤 Copying files to:   {dest_path}", "info")
            
            if source_path == dest_path:
                self.log_status(f"⚠️  Destination is inside the source folder. This will cause duplicate or recursive copies.", "warning")
                self.log_status(f"❌ Source and destination are the same folder: {source_path}", "error")
                messagebox.showerror(
                    "Invalid Destination",
                    "Source and destination cannot be the same folder. Please choose a destination outside the source."
                )
                self.is_processing = False
                return
            
            # Create destination folder
            dest_path.mkdir(parents=True, exist_ok=True)
            self.log_status(f"✓ Created/confirmed destination folder: {dest_path.absolute()}", "success")
            
            # Collect all files recursively, skipping the destination folder if it is inside the source
            all_files = []
            for root, dirs, files in os.walk(source_path):
                root_path = Path(root).resolve()
                # Stop walking into the destination folder if it is nested under the source
                dirs[:] = [d for d in dirs if not (
                    dest_path == (root_path / d).resolve() or
                    dest_path in (root_path / d).resolve().parents
                )]
                if dest_path == root_path or dest_path in root_path.parents:
                    continue
                for file in files:
                    file_path = Path(root_path) / file
                    if dest_path == file_path.resolve() or dest_path in file_path.resolve().parents:
                        continue
                    all_files.append(str(file_path))
            
            if not all_files:
                self.log_status(f"⚠️  No files found in: {source_folder}", "warning")
                self.is_processing = False
                return
            
            self.log_status(f"📁 Found {len(all_files)} file(s) to collect...", "info")
            self.log_status("", "info")
            
            copied_count = 0
            skipped_count = 0
            
            for file_path in all_files:
                try:
                    file_name = os.path.basename(file_path)
                    dest_file_path = dest_path / file_name
                    
                    # Handle duplicate file names
                    if dest_file_path.exists():
                        base_name = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
                        extension = file_name.rsplit('.', 1)[1] if '.' in file_name else ''
                        counter = 1
                        
                        while dest_file_path.exists():
                            if extension:
                                new_name = f"{base_name}_{counter}.{extension}"
                            else:
                                new_name = f"{base_name}_{counter}"
                            dest_file_path = dest_path / new_name
                            counter += 1
                    
                    shutil.copy2(file_path, dest_file_path)
                    copied_count += 1
                    self.log_status(f"  ✓ Copied: {file_name}", "success")
                    
                except Exception as e:
                    skipped_count += 1
                    self.log_status(f"  ⚠️  Skipped: {os.path.basename(file_path)} - {str(e)}", "error")
            
            self.log_status("", "info")
            self.log_status("=" * 50, "info")
            self.log_status(f"✓ Successfully copied: {copied_count} file(s)", "success")
            self.log_status(f"⚠️  Skipped: {skipped_count} file(s)", "warning" if skipped_count > 0 else "success")
            self.log_status(f"📁 All files saved to: {dest_path.absolute()}", "success")
            self.log_status("=" * 50, "info")
            
            messagebox.showinfo(
                "Success",
                f"✓ Copied: {copied_count}\n⚠️  Skipped: {skipped_count}\n\n📁 Files saved to: {dest_path.absolute()}"
            )
            
        except Exception as e:
            self.log_status(f"❌ Error: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            self.is_processing = False

    def get_history_path(self):
        return Path("deletion_history.json")

    def save_deletion_history(self, deleted_files, folder_path):
        history_path = self.get_history_path()
        history_data = []
        if history_path.exists():
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    history_data = json.load(f)
            except Exception:
                history_data = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "folder": folder_path,
            "files": deleted_files,
            "count": len(deleted_files)
        }
        history_data.append(entry)

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2)

    def delete_all_files(self):
        try:
            self.is_processing = True
            self.log_status("🔄 Starting deletion of all files...", "warning")

            target_folder = self.selected_folder.get()
            target_path = Path(target_folder)
            if not target_path.exists():
                self.log_status(f"❌ Folder does not exist: {target_folder}", "error")
                self.is_processing = False
                return

            all_files = []
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)

            if not all_files:
                self.log_status(f"⚠️  No files found in: {target_folder}", "warning")
                self.is_processing = False
                return

            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Delete {len(all_files)} file(s) from {target_folder}?\nThis will save recovery metadata to history."
            )
            if not confirm:
                self.log_status("❌ Deletion cancelled by user.", "error")
                self.is_processing = False
                return

            deleted_files = []
            deleted_count = 0
            skipped_count = 0

            for file_path in all_files:
                try:
                    file_name = os.path.basename(file_path)
                    os.remove(file_path)
                    deleted_files.append({"name": file_name, "path": file_path})
                    deleted_count += 1
                    self.log_status(f"  ✓ Deleted: {file_name}", "success")
                except Exception as e:
                    skipped_count += 1
                    self.log_status(f"  ⚠️  Failed to delete: {os.path.basename(file_path)} - {str(e)}", "error")

            if deleted_files:
                self.save_deletion_history(deleted_files, target_folder)

            self.log_status("", "info")
            self.log_status("=" * 50, "info")
            self.log_status(f"✓ Successfully deleted: {deleted_count} file(s)", "success")
            self.log_status(f"⚠️  Failed to delete: {skipped_count} file(s)", "warning")
            self.log_status(f"📁 Deletion history saved to: {self.get_history_path().absolute()}", "success")
            self.log_status("=" * 50, "info")

            messagebox.showinfo(
                "Deletion Complete",
                f"✓ Deleted: {deleted_count}\n⚠️  Failed: {skipped_count}\n\nHistory saved to: {self.get_history_path().absolute()}"
            )

        except Exception as e:
            self.log_status(f"❌ Error during deletion: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.is_processing = False

    def recover_deleted_files(self):
        try:
            self.is_processing = True
            history_path = self.get_history_path()
            if not history_path.exists():
                self.log_status("⚠️  No deletion history found.", "warning")
                messagebox.showinfo("No History", "No deletion history found. Nothing to recover.")
                self.is_processing = False
                return

            with open(history_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)

            if not history_data:
                self.log_status("⚠️  Deletion history is empty.", "warning")
                messagebox.showinfo("No History", "Deletion history is empty. Nothing to recover.")
                self.is_processing = False
                return

            recovery_prompt = "Select recovery option:\n\n"
            for idx, entry in enumerate(history_data, 1):
                recovery_prompt += f"{idx}. {entry['timestamp']} — {entry['folder']} ({entry['count']} files)\n"
            recovery_prompt += "\nEnter the number to recover that entry, or type 'all' to recover all."

            choice = self.ask_input("Recover History", recovery_prompt)
            if choice is None:
                self.log_status("❌ Recovery cancelled by user.", "error")
                self.is_processing = False
                return

            selected_entries = []
            if choice.lower() == "all":
                selected_entries = history_data
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(history_data):
                        selected_entries = [history_data[idx]]
                    else:
                        raise ValueError("Invalid selection")
                except Exception:
                    self.log_status("❌ Invalid recovery selection.", "error")
                    messagebox.showerror("Invalid Selection", "Please enter a valid entry number or 'all'.")
                    self.is_processing = False
                    return

            recovered_count = 0
            failed_count = 0
            for entry in selected_entries:
                for file_info in entry["files"]:
                    original_path = Path(file_info["path"])
                    try:
                        original_path.parent.mkdir(parents=True, exist_ok=True)
                        if not original_path.exists():
                            original_path.touch()
                            recovered_count += 1
                            self.log_status(f"  ✓ Recovered (recreated): {file_info['name']}", "success")
                        else:
                            self.log_status(f"  ⚠️  File already exists: {file_info['name']}", "warning")
                    except Exception as e:
                        failed_count += 1
                        self.log_status(f"  ❌ Failed to recover: {file_info['name']} - {str(e)}", "error")

            self.log_status("", "info")
            self.log_status("=" * 50, "info")
            self.log_status(f"✓ Successfully recovered: {recovered_count} file(s)", "success")
            self.log_status(f"❌ Failed to recover: {failed_count} file(s)", "error")
            self.log_status("=" * 50, "info")
            messagebox.showinfo(
                "Recovery Complete",
                f"✓ Recovered: {recovered_count}\n❌ Failed: {failed_count}"
            )

        except Exception as e:
            self.log_status(f"❌ Error during recovery: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.is_processing = False

    def ask_input(self, title, prompt):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()

        prompt_label = tk.Label(dialog, text=prompt, font=("Helvetica", 10), wraplength=480, justify="left")
        prompt_label.pack(padx=15, pady=15)

        entry_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=entry_var, width=60)
        entry.pack(padx=15, pady=(0, 10))
        entry.focus()

        result = {"value": None}

        def submit():
            result["value"] = entry_var.get().strip()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="OK", command=submit, width=10, bg=self.RUBY_RED, fg=self.TEXT_COLOR).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel, width=10, bg=self.GREY_LIGHT).pack(side=tk.LEFT, padx=5)

        self.root.wait_window(dialog)
        return result["value"]


def main():
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
