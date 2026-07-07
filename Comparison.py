import sys
from pathlib import Path


def list_files(folder_path):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Path not found: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")

    files = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            files[str(path.relative_to(folder))] = path

    return files


def compare_folders(folder1, folder2):
    files1 = list_files(folder1)
    files2 = list_files(folder2)

    differences = []

    for relative_path in sorted(set(files1) | set(files2)):
        if relative_path not in files1:
            differences.append(f"Only in {folder2}: {relative_path}")
            differences.append(f"File {relative_path} is missing in {folder1}, line {files2[relative_path].read_text(encoding='utf-8')}")
        
        elif relative_path not in files2:
            differences.append(f"Only in {folder1}: {relative_path}")
        else:
            if files1[relative_path].read_bytes() != files2[relative_path].read_bytes():
                differences.append(f"Different content: {relative_path}")

    return differences


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Comparison.py <folder1> <folder2>")
        sys.exit(2)

    folder1 = sys.argv[1]
    folder2 = sys.argv[2]

    try:
        differences = compare_folders(folder1, folder2)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(error)
        sys.exit(2)

    if differences:
        print("Differences found:")
        for difference in differences:
            print(f"- {difference}")
        sys.exit(1)

    print("No differences found.")
    sys.exit(0)
