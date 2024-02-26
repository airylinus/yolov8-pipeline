#!/usr/bin/env python3
import sys
import os
import json

root_dir = os.path.dirname(os.path.abspath(__file__))

def run(labeled_images_dir, output_dir):
    print("output_dir: ", output_dir)
    labels = fix_labels(labeled_images_dir, output_dir)
    print("labels: ", labels) 
    print("labels length: ", len(labels))
    


def fix_labels(labeled_images_dir, output_dir):
    old_labels = read_labels(output_dir)
    print(len(old_labels))
    labeled_labels = read_labeled_labels(labeled_images_dir)
    for label in labeled_labels:
        if label not in old_labels:
            old_labels.append(label)
    print(len(old_labels))
    with open(os.path.join(root_dir, output_dir, 'fixed_labels.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(old_labels))
    return old_labels
 

def read_labels(output_dir):
    if os.path.exists(os.path.join(root_dir, output_dir, 'labels.txt')):
        with open(os.path.join(root_dir, output_dir, 'labels.txt'), 'r', encoding='utf-8') as f:
            labels = f.read().splitlines()
            print("labels from file: ", labels)
            return labels
    else:
        print("no labels from file: ", labels)
        return []


def read_labeled_labels(labeled_images_dir):
    label_files = os.listdir(labeled_images_dir)
    labels = {}
    for label_file in label_files:
        if not label_file.endswith('.json'):
            continue
        label_file_path = os.path.join(root_dir, labeled_images_dir, label_file)
        with open(label_file_path, 'r', encoding='utf-8') as f:
            label_data = json.load(f)
            for shape in label_data['shapes']:
                label = shape['label']
                if label not in labels:
                    labels[label] = 1 
    print("Labels: ", labels)
    print("Total labels: ", len(labels))
    return labels


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python data-prepare.py [labeled_images_dir] [output_dir]")
        print("Example: python data-prepare.py v8-0125 data-v8")
        exit(1)
    print(root_dir)
    run(sys.argv[1], sys.argv[2])
