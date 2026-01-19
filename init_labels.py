#!/bin/python3
import os
import json
import sys
from typing import List


labels_count = {}
no_shapes_count = 0
existing_labels = set()

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

def load_existing_labels(existing_labels_file: str) -> [str]:
    """加载现有的标签文件"""
    if os.path.exists(existing_labels_file):
        with open(existing_labels_file, 'r', encoding='utf-8') as f:
            existing = [line.strip() for line in f.readlines() if line.strip()]
        global existing_labels
        existing_labels = set(existing)
        print(f"Loaded existing labels: {existing}")
        return existing
    return []

def merge_labels(existing_labels_list: [str], new_labels: [str]) -> [str]:
    """合并现有标签和新标签，保持现有标签顺序，新标签按频率排序追加"""
    # 创建结果列表，从现有标签开始
    merged = existing_labels_list.copy()

    # 找出新标签（不在现有标签中的）
    new_only = [label for label in new_labels if label not in existing_labels]

    # 将新标签追加到现有标签后面
    merged.extend(new_only)

    print(f"Merged labels: existing {len(existing_labels_list)}, new {len(new_only)}, total {len(merged)}")
    if new_only:
        print(f"New labels added: {new_only}")

    return merged


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

    # 检查是否有第三个参数作为现有标签文件路径
    existing_labels_file = None
    if len(sys.argv) > 3:
        existing_labels_file = sys.argv[3]

    print (f"Raw labeled dir: {raw_labeled_dir}")
    print (f"Output dir: {output_dir}")

    # 加载现有标签（如果提供）
    existing_labels_list = []
    if existing_labels_file and os.path.exists(existing_labels_file):
        existing_labels_list = load_existing_labels(existing_labels_file)
        print(f"Using existing labels from: {existing_labels_file}")
    else:
        print("No existing labels file provided or file not found, generating new labels")

    # 获取新数据中的标签
    new_labels = list_labels(raw_labeled_dir)

    # 合并标签
    final_labels = merge_labels(existing_labels_list, new_labels)

    # 生成标签文件
    generate_labels_file(output_dir, final_labels)
