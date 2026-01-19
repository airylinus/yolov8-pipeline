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

    def calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """计算两个边界框的IOU (Intersection over Union)

        Args:
            bbox1: 第一个边界框 [x1, y1, x2, y2]
            bbox2: 第二个边界框 [x1, y1, x2, y2]

        Returns:
            IOU 值 (0.0 到 1.0)
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2

        # 计算交集区域
        x1_inter = max(x1_1, x1_2)
        y1_inter = max(y1_1, y1_2)
        x2_inter = min(x2_1, x2_2)
        y2_inter = min(y2_1, y2_2)

        # 没有交集
        if x2_inter <= x1_inter or y2_inter <= y1_inter:
            return 0.0

        # 计算交集面积
        inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)

        # 计算两个框的面积
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)

        # 计算并集面积
        union_area = area1 + area2 - inter_area

        # 计算IOU
        if union_area == 0:
            return 0.0

        return inter_area / union_area

    def points_to_bbox(self, points: List[List[float]]) -> List[float]:
        """将4个点的坐标转换为边界框格式

        Args:
            points: [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]

        Returns:
            [x1, y1, x2, y2]
        """
        x_coords = [point[0] for point in points]
        y_coords = [point[1] for point in points]

        x1 = min(x_coords)
        y1 = min(y_coords)
        x2 = max(x_coords)
        y2 = max(y_coords)

        return [x1, y1, x2, y2]

    def filter_duplicate_detections(self, new_shapes: List[dict],
                                  existing_shapes: List[dict],
                                  iou_threshold: float = 0.85) -> List[dict]:
        """过滤重复的检测结果

        Args:
            new_shapes: 新的检测结果
            existing_shapes: 现有的标注
            iou_threshold: IOU阈值，大于此值认为是重复检测

        Returns:
            过滤后的新检测结果列表
        """
        filtered_shapes = []

        for new_shape in new_shapes:
            is_duplicate = False

            # 将新检测的points转换为bbox
            new_bbox = self.points_to_bbox(new_shape["points"])
            new_label = new_shape["label"]

            # 检查与现有标注的IOU
            for existing_shape in existing_shapes:
                if existing_shape["label"] == new_label:  # 只比较相同标签的标注
                    existing_bbox = self.points_to_bbox(existing_shape["points"])
                    iou = self.calculate_iou(new_bbox, existing_bbox)

                    if iou > iou_threshold:
                        print(f"Duplicate detection found for {new_label} "
                              f"(IOU: {iou:.3f} > {iou_threshold}), skipping...")
                        is_duplicate = True
                        break

            if not is_duplicate:
                filtered_shapes.append(new_shape)

        return filtered_shapes

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
                existing_shapes = []
                if os.path.exists(json_path):
                    # 读取现有文件
                    with open(json_path, 'r', encoding='utf-8') as f:
                        annotation_data = json.load(f)
                    existing_shapes = annotation_data.get("shapes", [])
                    print(f"Appending to existing annotation file: {json_path} "
                          f"({len(existing_shapes)} existing annotations)")
                else:
                    # 创建新文件
                    annotation_data = self.create_annotation_template(image_path)
                    print(f"Creating new annotation file: {json_path}")

                # 进行推理
                new_shapes = self.predict_image(image_path, conf_threshold)

                if new_shapes:
                    # 过滤重复检测
                    if existing_shapes:
                        filtered_shapes = self.filter_duplicate_detections(
                            new_shapes, existing_shapes, iou_threshold=0.85)
                        added_count = len(filtered_shapes)
                        skipped_count = len(new_shapes) - added_count
                        if skipped_count > 0:
                            print(f"Filtered {skipped_count} duplicate detections, "
                                  f"adding {added_count} new detections")
                    else:
                        filtered_shapes = new_shapes
                        added_count = len(filtered_shapes)
                        print(f"Added {added_count} detections")

                    if filtered_shapes:  # 只有在有新检测时才保存
                        # 添加过滤后的新标注
                        annotation_data["shapes"].extend(filtered_shapes)

                        # 保存文件
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(annotation_data, f, indent=2, ensure_ascii=False)
                    else:
                        print("No new detections to add after filtering")

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