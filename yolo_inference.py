#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv8模型推理脚本
使用训练好的模型对图片进行推理，并将结果保存为标注文件格式
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image

# 导入YOLOv8相关库
try:
    from ultralytics import YOLO
except ImportError:
    print("请安装ultralytics: pip install ultralytics")
    exit(1)


class YOLOInference:
    def __init__(self, model_path: str, labels_file: str):
        """初始化YOLO推理器

        Args:
            model_path: YOLO模型文件路径 (.pt)
            labels_file: 标签文件路径 (labels.txt)
        """
        self.model = YOLO(model_path)
        self.labels = self.load_labels(labels_file)
        print(f"Loaded model: {model_path}")
        print(f"Loaded {len(self.labels)} labels: {self.labels}")

    def load_labels(self, labels_file: str) -> List[str]:
        """加载标签文件

        Args:
            labels_file: 标签文件路径

        Returns:
            标签列表
        """
        with open(labels_file, 'r', encoding='utf-8') as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]
        return labels

    def get_image_info(self, image_path: str) -> Tuple[int, int]:
        """获取图片尺寸

        Args:
            image_path: 图片路径

        Returns:
            (width, height)
        """
        with Image.open(image_path) as img:
            return img.size  # (width, height)

    def create_annotation_template(self, image_path: str) -> dict:
        """创建标注文件模板

        Args:
            image_path: 图片路径

        Returns:
            标注文件模板字典
        """
        width, height = self.get_image_info(image_path)

        return {
            "version": "2.4.4",
            "flags": {},
            "shapes": [],
            "imagePath": os.path.basename(image_path),
            "imageData": None,
            "imageHeight": height,
            "imageWidth": width
        }

    def bbox_to_points(self, bbox: List[float]) -> List[List[float]]:
        """将YOLO格式的bbox转换为4个点的坐标

        Args:
            bbox: [x1, y1, x2, y2] 或 [x_center, y_center, width, height]

        Returns:
            4个点的坐标列表 [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
        """
        x1, y1, x2, y2 = bbox
        return [
            [float(x1), float(y1)],
            [float(x2), float(y1)],
            [float(x2), float(y2)],
            [float(x1), float(y2)]
        ]

    def predict_image(self, image_path: str, conf_threshold: float = 0.25) -> List[dict]:
        """对单张图片进行推理

        Args:
            image_path: 图片路径
            conf_threshold: 置信度阈值

        Returns:
            推理结果列表，每个元素包含label和points
        """
        results = self.model(image_path, conf=conf_threshold)

        shapes = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    # 获取类别索引和置信度
                    class_id = int(box.cls.item())
                    confidence = float(box.conf.item())

                    # 获取边界框坐标 [x1, y1, x2, y2]
                    bbox = box.xyxy[0].tolist()

                    # 获取标签名
                    if 0 <= class_id < len(self.labels):
                        label_name = self.labels[class_id]
                    else:
                        print(f"Warning: class_id {class_id} out of range, using 'unknown'")
                        label_name = "unknown"

                    # 转换为标注格式
                    shape = {
                        "label": label_name,
                        "score": confidence,
                        "points": self.bbox_to_points(bbox),
                        "group_id": None,
                        "description": "",
                        "difficult": False,
                        "shape_type": "rectangle",
                        "flags": {},
                        "attributes": {},
                        "kie_linking": []
                    }
                    shapes.append(shape)

        return shapes

    def process_directory(self, image_dir: str, output_dir: Optional[str] = None,
                         conf_threshold: float = 0.25, save_images: bool = False):
        """处理目录中的所有图片

        Args:
            image_dir: 图片目录
            output_dir: 输出目录，如果为None则使用图片目录
            conf_threshold: 置信度阈值
            save_images: 是否保存推理结果图片
        """
        if output_dir is None:
            output_dir = image_dir

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

        # 遍历目录中的所有图片
        image_paths = []
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_paths.append(os.path.join(root, file))

        print(f"Found {len(image_paths)} images to process")

        processed_count = 0
        for image_path in image_paths:
            try:
                print(f"Processing: {image_path}")

                # 生成对应的JSON文件路径
                relative_path = os.path.relpath(image_path, image_dir)
                json_filename = Path(relative_path).stem + '.json'
                json_path = os.path.join(output_dir, json_filename)

                # 检查是否已存在标注文件
                if os.path.exists(json_path):
                    # 读取现有文件
                    with open(json_path, 'r', encoding='utf-8') as f:
                        annotation_data = json.load(f)
                    print(f"Appending to existing annotation file: {json_path}")
                else:
                    # 创建新文件
                    annotation_data = self.create_annotation_template(image_path)
                    print(f"Creating new annotation file: {json_path}")

                # 进行推理
                new_shapes = self.predict_image(image_path, conf_threshold)

                if new_shapes:
                    # 添加新的标注
                    annotation_data["shapes"].extend(new_shapes)
                    print(f"Added {len(new_shapes)} detections")

                    # 保存文件
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(annotation_data, f, indent=2, ensure_ascii=False)

                    processed_count += 1
                else:
                    print("No detections found")

                # 可选：保存推理结果图片
                if save_images:
                    results = self.model(image_path, conf=conf_threshold)
                    for result in results:
                        result.save(filename=os.path.join(output_dir, f"{Path(image_path).stem}_result.jpg"))

            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
                continue

        print(f"Processing completed. Processed {processed_count} images.")


def main():
    parser = argparse.ArgumentParser(description="YOLOv8模型推理脚本")
    parser.add_argument("model_path", help="YOLO模型文件路径 (.pt)")
    parser.add_argument("labels_file", help="标签文件路径 (labels.txt)")
    parser.add_argument("image_dir", help="图片目录路径")
    parser.add_argument("--output_dir", "-o", help="输出目录路径 (默认为图片目录)")
    parser.add_argument("--conf", "-c", type=float, default=0.25,
                       help="置信度阈值 (默认: 0.25)")
    parser.add_argument("--save_images", "-s", action="store_true",
                       help="保存推理结果图片")

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.model_path):
        print(f"模型文件不存在: {args.model_path}")
        return 1

    if not os.path.exists(args.labels_file):
        print(f"标签文件不存在: {args.labels_file}")
        return 1

    if not os.path.exists(args.image_dir):
        print(f"图片目录不存在: {args.image_dir}")
        return 1

    # 创建推理器并处理
    try:
        inference = YOLOInference(args.model_path, args.labels_file)
        inference.process_directory(
            args.image_dir,
            args.output_dir,
            args.conf,
            args.save_images
        )
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())