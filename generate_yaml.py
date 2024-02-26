import os
import sys

root_dir = os.path.abspath(os.path.dirname(__file__)) 

def run(dataset_dir):
    if not os.path.exists(dataset_dir):
        print("Dataset directory not found: {}".format(dataset_dir))
        exit(1)
    labels_file = os.path.join(dataset_dir, "fixed_labels.txt")
    if not os.path.exists(labels_file):
        print("Labels file not found: {}".format(labels_file))
        exit(1)
    with open(labels_file, "r", encoding="utf-8") as f:
        labels = f.readlines()
    labels = [label.strip() for label in labels]
    yaml_file = os.path.join(root_dir, dataset_dir, "dataset.yaml")
    with open(yaml_file, "w") as f:
        f.write("train: ./train/images\n")
        f.write("val: ./val/images\n")
        f.write("nc: " + str(len(labels)) + "\n")
        f.write("name: \n")
        for _, label in enumerate(labels):
            f.write("  - " + label + "\n")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python generate_yaml.py <dataset_dir>")
        exit(1)
    dataset_dir = sys.argv[1]
    run(dataset_dir)