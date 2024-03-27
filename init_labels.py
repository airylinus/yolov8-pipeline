#!/bin/python3
import os
import json
import sys
from typing import List


labels_count = {}
no_shapes_count = 0

def list_labels(raw_labels_dir: str) -> [str]: 
    raw_labels = []
    file_count = 0
    global no_shapes_count
    fs = os.listdir(raw_labels_dir)
    for fn in fs:
        if not fn.endswith('.json'):
            continue
        with open(os.path.join(raw_labels_dir, fn), 'r', encoding='utf-8') as f:
            fc = f.read()
            json_data = json.loads(fc)
            if 'shapes' in json_data:
                file_count += 1
                for shape in json_data['shapes']:
                    label_name = shape['label']
                    count_labels(label_name)
            if len(json_data['shapes']) == 0:
                no_shapes_count += 1
                f.close()
                os.remove(os.path.join(raw_labels_dir, fn))
     
    sorted_labels = sorted(labels_count.items(), key=lambda x: x[1], reverse=True)
    # print("Sorted labels by count:")
    for label_name, count in sorted_labels:
        print(f"{label_name}: {count}")
        raw_labels.append(label_name)
    print(f"No shapes count: {no_shapes_count}")
    print(f"Total files: {file_count}")
    return raw_labels


def generate_labels_file(output_dir: str, raw_labels: [str]):
    with open(os.path.join(output_dir, 'labels.txt'), 'w+', encoding='utf-8') as f:
        for label in raw_labels:
            f.write(label + '\n')
    return


def count_labels(labes_name: str):
    global labels_count
    labels_count[labes_name] = labels_count.get(labes_name, 0) + 1


if __name__ == '__main__':
    # print("Starting...")
    raw_labeled_dir = sys.argv[1]
    output_dir = sys.argv[2]
    print (f"Raw labeled dir: {raw_labeled_dir}")
    print (f"Output dir: {output_dir}")
    labels = list_labels(raw_labeled_dir)
    generate_labels_file(output_dir, labels)
