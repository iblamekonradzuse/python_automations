import os
import shutil
import sys

def organize_files(source_directory='.'):
    ubung_dir = os.path.join(source_directory, 'ubung')
    vorlesung_dir = os.path.join(source_directory, 'vorlesung')
    abgabe_dir = os.path.join(source_directory, 'abgabe')
    
    for directory in [ubung_dir, vorlesung_dir, abgabe_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    all_files = [f for f in os.listdir(source_directory) 
                if os.path.isfile(os.path.join(source_directory, f))]
    
    files_moved = 0
    
    for filename in all_files:
        source_path = os.path.join(source_directory, filename)
        
        if filename == os.path.basename(__file__):
            continue
            
        if filename.startswith('A'):
            target_dir = ubung_dir
        elif filename.startswith('Math'):
            target_dir = vorlesung_dir
        elif filename.startswith('B'):
            target_dir = abgabe_dir
        else:
            continue
        
        target_path = os.path.join(target_dir, filename)
        try:
            shutil.move(source_path, target_path)
            print(f"Moved '{filename}' to {os.path.basename(target_dir)}/")
            files_moved += 1
        except Exception as e:
            print(f"Error moving '{filename}': {e}")
    
    print(f"\nTotal files moved: {files_moved}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        organize_files(directory)
    else:
        organize_files()
