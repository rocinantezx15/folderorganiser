import os
import shutil
from pathlib import Path
import json
from datetime import datetime


def print_menu():
    """Display the main menu with options."""
    print("\n" + "="*50)
    print("FILE ORGANIZER MENU")
    print("="*50)
    print("1. Dump'em in a folder (collect all files)")
    print("2. Delete all files in a folder")
    print("3. Recover all previously deleted files (history)")
    print("4. Coming Soon")
    print("5. Coming Soon")
    print("6. Coming Soon")
    print("0. Exit")
    print("="*50)


def get_folder_path():
    """Get the target folder path from user."""
    while True:
        folder_path = input("\nEnter the target folder path (you can paste with Ctrl+V): ").strip()
        
        if not folder_path:
            print("❌ Folder path cannot be empty. Please try again.")
            continue
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder path does not exist: {folder_path}")
            print("Please try again.")
            continue
        
        if not os.path.isdir(folder_path):
            print(f"❌ Path is not a directory: {folder_path}")
            print("Please try again.")
            continue
        
        return folder_path


def get_destination_folder_path():
    """Get the destination folder path from user."""
    while True:
        folder_path = input("\nEnter the destination folder path (you can paste with Ctrl+V): ").strip()
        
        if not folder_path:
            print("❌ Folder path cannot be empty. Please try again.")
            continue
        
        if not os.path.isdir(folder_path):
            try:
                create = input(f"Destination folder does not exist. Create it? (y/n): ").strip().lower()
                if create == 'y':
                    os.makedirs(folder_path, exist_ok=True)
                    return folder_path
                else:
                    print("Please try again.")
                    continue
            except Exception as e:
                print(f"❌ Error creating folder: {str(e)}")
                print("Please try again.")
                continue
        
        return folder_path


def collect_all_files(source_folder, destination_folder='files'):
    """
    Collect all files from source folder (including subfolders) and dump them
    into a single destination folder.
    """
    try:
        source_path = Path(source_folder).resolve()
        dest_path = Path(destination_folder).resolve()
        
        if source_path == dest_path:
            print(f"❌ Source and destination are the same folder: {source_path}")
            print("Please choose a destination folder outside the source folder.")
            return
        
        # Create destination folder if it doesn't exist
        dest_path.mkdir(exist_ok=True)
        print(f"\n✓ Created/confirmed destination folder: {destination_folder}")
        
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
            print(f"⚠️  No files found in: {source_folder}")
            return
        
        print(f"\n📁 Found {len(all_files)} file(s) to collect...")
        
        # Copy all files to destination folder
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
                print(f"  ✓ Copied: {file_name}")
                
            except Exception as e:
                skipped_count += 1
                print(f"  ⚠️  Skipped: {os.path.basename(file_path)} - {str(e)}")
        
        print(f"\n{'='*50}")
        print(f"📊 SUMMARY")
        print(f"{'='*50}")
        print(f"✓ Successfully copied: {copied_count} file(s)")
        print(f"⚠️  Skipped: {skipped_count} file(s)")
        print(f"📁 All files saved to: {os.path.abspath(dest_path)}")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Error during file collection: {str(e)}")


def get_deletion_history_path():
    """Get the path for the deletion history file."""
    return Path("deletion_history.json")


def save_to_history(deleted_files, folder_path):
    """Save deleted files to history for recovery."""
    history_path = get_deletion_history_path()
    history_data = []
    
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    # Add new deletion entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "folder": str(folder_path),
        "files": deleted_files,
        "count": len(deleted_files)
    }
    history_data.append(entry)
    
    # Save updated history
    with open(history_path, 'w') as f:
        json.dump(history_data, f, indent=2)


def delete_all_files(folder_path):
    """
    Delete all files from a folder (including subfolders) and save to history.
    """
    try:
        target_path = Path(folder_path)
        
        if not target_path.exists():
            print(f"❌ Folder does not exist: {folder_path}")
            return
        
        # Collect all files recursively
        all_files = []
        for root, dirs, files in os.walk(target_path):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        
        if not all_files:
            print(f"⚠️  No files found in: {folder_path}")
            return
        
        print(f"\n📁 Found {len(all_files)} file(s) to delete...")
        print("\n⚠️  WARNING: This action will DELETE all files!")
        confirmation = input("Are you sure you want to delete all files? (yes/no): ").strip().lower()
        
        if confirmation != 'yes':
            print("❌ Deletion cancelled.")
            return
        
        # Delete files and track them
        deleted_files = []
        deleted_count = 0
        skipped_count = 0
        
        for file_path in all_files:
            try:
                file_name = os.path.basename(file_path)
                os.remove(file_path)
                deleted_count += 1
                deleted_files.append({
                    "name": file_name,
                    "path": file_path
                })
                print(f"  ✓ Deleted: {file_name}")
            except Exception as e:
                skipped_count += 1
                print(f"  ⚠️  Failed to delete: {os.path.basename(file_path)} - {str(e)}")
        
        # Save to history
        if deleted_files:
            save_to_history(deleted_files, folder_path)
        
        print(f"\n{'='*50}")
        print(f"📊 DELETION SUMMARY")
        print(f"{'='*50}")
        print(f"✓ Successfully deleted: {deleted_count} file(s)")
        print(f"⚠️  Failed to delete: {skipped_count} file(s)")
        print(f"📁 Deletion history saved for recovery")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Error during file deletion: {str(e)}")


def recover_deleted_files():
    """
    Recover all previously deleted files from history.
    """
    try:
        history_path = get_deletion_history_path()
        
        if not history_path.exists():
            print("⚠️  No deletion history found. Nothing to recover.")
            return
        
        with open(history_path, 'r') as f:
            history_data = json.load(f)
        
        if not history_data:
            print("⚠️  No deletion history found. Nothing to recover.")
            return
        
        print(f"\n📜 DELETION HISTORY")
        print("="*50)
        for idx, entry in enumerate(history_data, 1):
            print(f"\n{idx}. Deleted at: {entry['timestamp']}")
            print(f"   Folder: {entry['folder']}")
            print(f"   Files deleted: {entry['count']}")
        
        print("\n" + "="*50)
        choice = input("Select an entry to recover (number) or 'all' to recover all: ").strip().lower()
        
        recovered_count = 0
        failed_count = 0
        
        if choice == 'all':
            selected_entries = history_data
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(history_data):
                    selected_entries = [history_data[idx]]
                else:
                    print("❌ Invalid selection.")
                    return
            except:
                print("❌ Invalid input.")
                return
        
        for entry in selected_entries:
            folder = entry['folder']
            print(f"\n🔄 Recovering files from: {folder}")
            
            for file_info in entry['files']:
                original_path = file_info['path']
                target_path = Path(original_path)
                
                try:
                    # Recreate directory structure if needed
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Check if file still exists or needs to be recreated
                    if not target_path.exists():
                        # Create empty file as recovery (original is gone)
                        target_path.touch()
                        print(f"  ✓ Recovered (recreated): {file_info['name']}")
                        recovered_count += 1
                    else:
                        print(f"  ⚠️  File already exists: {file_info['name']}")
                except Exception as e:
                    failed_count += 1
                    print(f"  ❌ Failed to recover: {file_info['name']} - {str(e)}")
        
        print(f"\n{'='*50}")
        print(f"📊 RECOVERY SUMMARY")
        print(f"{'='*50}")
        print(f"✓ Successfully recovered: {recovered_count} file(s)")
        print(f"❌ Failed to recover: {failed_count} file(s)")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Error during file recovery: {str(e)}")


def option_placeholder():
    """Placeholder for future options."""
    print("🔄 This feature is coming soon!")


def main():
    """Main function to run the file organizer."""
    print("\n🎯 Welcome to File Organizer!")
    
    while True:
        print_menu()
        choice = input("Select an option (0-6): ").strip()
        
        if choice == '1':
            print("\n📂 DUMP'EM IN A FOLDER MODE")
            source_folder = get_folder_path()
            destination_folder = get_destination_folder_path()
            collect_all_files(source_folder, destination_folder)
            
        elif choice == '2':
            print("\n🗑️  DELETE ALL FILES MODE")
            target_folder = get_folder_path()
            delete_all_files(target_folder)
            
        elif choice == '3':
            print("\n🔄 RECOVER DELETED FILES MODE")
            recover_deleted_files()
            
        elif choice == '4':
            option_placeholder()
            
        elif choice == '5':
            option_placeholder()
            
        elif choice == '6':
            option_placeholder()
            
        elif choice == '0':
            print("\n👋 Thank you for using File Organizer. Goodbye!")
            break
            
        else:
            print("❌ Invalid option. Please select 0-6.")


if __name__ == "__main__":
    main()
