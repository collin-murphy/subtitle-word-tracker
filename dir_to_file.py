from config import SUBS_DIR
SUBS_DIR = ''
DIRS = ''
FINAL_DIR = ''
import os, shutil

# converts directory of subtitles to files instead
def convert_dirs_to_files(dir):
    print("Converting directories to files...")
    affected_dirs = []
    for f in os.listdir(dir):
        file_path = os.path.join(dir, f)\
        
        if os.path.isdir(file_path):
            print(f"{f} is a directory")
            affected_dirs.append(file_path)
            for sub in os.listdir(file_path):
                if(sub.endswith(".srt")):
                    print("moving file...")
                    shutil.move(os.path.join(file_path, sub), os.path.join(FINAL_DIR, f"{f}.srt"))
                    break
                
        else:
            print(f"{f} is not a directory")

    return affected_dirs

def remove_directories(dirs):
    print("Removing directories...")
    for d in dirs:
        print(f"Removing {d}")
        shutil.rmtree(d)

def single_dir():
    dirs = convert_dirs_to_files(SUBS_DIR)
    remove_directories(dirs)

def create_output_dir():
    if not os.path.exists(FINAL_DIR):
        os.mkdir(FINAL_DIR)

def multiple_dirs():
    for i in range(6):
        dirs = convert_dirs_to_files(f"{DIRS}{i+1}")
        remove_directories(dirs)

# main function of the program
def main():
    create_output_dir()
    single_dir()

if __name__ == "__main__":
    main()
