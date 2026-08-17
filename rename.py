import os

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False
        
    original = content
    # Display names
    content = content.replace("IT Support Systems", "IT Support Systems")
    content = content.replace("IT Support Systems", "IT Support Systems")
    content = content.replace("IT Support", "IT Support")
    
    # Internal names (docker, secrets, package.json, etc)
    content = content.replace("it-support-systems", "it-support-systems")
    content = content.replace("it_support_systems", "it_support_systems")
    
    # Let's fix the repo URL if it got changed to lowercase
    content = content.replace("Nethumini/IT-Support-Systems", "Nethumini/IT-Support-Systems")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    root_dir = r"d:\RESEARCH\it-support-systems"
    skip_dirs = {'.git', 'venv', 'node_modules', '__pycache__', 'dist', 'build', '.idea', '.vscode'}
    skip_exts = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.db', '.pdf', '.zip'}
    
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove skipped dirs
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in skip_exts:
                continue
            
            filepath = os.path.join(dirpath, filename)
            if replace_in_file(filepath):
                count += 1
                print(f"Updated {filepath}")
                
    print(f"Total files updated: {count}")

if __name__ == '__main__':
    main()
