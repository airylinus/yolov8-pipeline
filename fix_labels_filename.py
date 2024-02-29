import sys
import json
import os



def main():
    print("Hello, World!")
    # fix_labels_filename("D:\\dataset\\gzsle\\data-v8\\test", "image_12_0226.json")
    fix_path("D:\\dataset\\gzsle\\data-v8\\test")
    sys.exit(0)


def fix_path(label_path: str) -> str:
    fs = os.listdir(label_path)
    for f in fs:
        if f.endswith(".json"):
            fix_labels_filename(label_path, f)
    return label_path


def fix_labels_filename(file_path: str, filename: str):
    if not os.path.isfile(os.path.join(file_path, filename)):
        print(f"File {filename} not found in {file_path}")
        return False
    with open(os.path.join(file_path, filename), "r", encoding="utf-8") as f:
        data = json.load(f)
        if "imagePath" in data:
            data["imagePath"] = filename.split(".")[0] + ".jpg"
        else:
            print(f"imagePath not found in {filename}")
        f.close()
        os.remove(os.path.join(file_path, filename))
        with open(os.path.join(file_path, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            print(f"Fixed {filename}")
            return True

if __name__ == "__main__":
    main()
