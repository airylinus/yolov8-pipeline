# YOLOv8 模型推理脚本

`yolo_inference.py` 是一个用于对图片进行YOLOv8模型推理的脚本，可以将检测结果保存为标注文件格式。

## 功能特点

- ✅ 加载训练好的YOLOv8模型进行推理
- ✅ 根据labels.txt文件进行标签索引映射
- ✅ 支持批量处理目录中的所有图片
- ✅ 将检测结果转换为指定JSON标注格式
- ✅ 支持追加模式：如果标注文件已存在，会将新检测结果追加到现有标注中
- ✅ 支持多种图片格式（jpg, png, bmp, tiff等）

## 使用方法

### 基本用法

```bash
python yolo_inference.py <model_path> <labels_file> <image_dir> [options]
```

### 参数说明

- `model_path`: YOLO模型文件路径 (.pt文件)
- `labels_file`: 标签文件路径 (labels.txt，每行一个标签名)
- `image_dir`: 包含图片的目录路径

### 可选参数

- `--output_dir, -o`: 输出目录路径（默认为图片目录）
- `--conf, -c`: 置信度阈值（默认: 0.25）
- `--save_images, -s`: 保存推理结果图片（带检测框的图片）

### 示例

```bash
# 基本使用，对images目录中的图片进行推理，结果保存到images目录
python yolo_inference.py model.pt labels.txt images/

# 指定输出目录和置信度阈值
python yolo_inference.py model.pt labels.txt images/ --output_dir results/ --conf 0.5

# 保存推理结果图片
python yolo_inference.py model.pt labels.txt images/ --save_images
```

## 输出格式

脚本会为每张图片生成一个同名的JSON文件，格式如下：

```json
{
  "version": "2.4.4",
  "flags": {},
  "shapes": [
    {
      "label": "标签名",
      "score": 0.95,
      "points": [
        [x1, y1],
        [x2, y1],
        [x2, y2],
        [x1, y2]
      ],
      "group_id": null,
      "description": "",
      "difficult": false,
      "shape_type": "rectangle",
      "flags": {},
      "attributes": {},
      "kie_linking": []
    }
  ],
  "imagePath": "图片文件名.jpg",
  "imageData": null,
  "imageHeight": 图片高度,
  "imageWidth": 图片宽度
}
```

## 标签映射

脚本使用labels.txt文件进行类别索引到标签名的映射：

```
# labels.txt内容示例
apple
banana
orange
grape
```

YOLO模型输出的类别索引0对应"apple"，索引1对应"banana"，以此类推。

## 追加模式

如果目标目录中已经存在同名的JSON标注文件，脚本会：

1. 读取现有文件的内容
2. 将新的检测结果追加到shapes数组中
3. 保存更新后的文件

这对于分批处理或补充标注非常有用。

## 依赖要求

- ultralytics (YOLOv8官方库)
- pillow (PIL)
- numpy

安装依赖：
```bash
pip install ultralytics pillow numpy
```

## 注意事项

1. 确保labels.txt中的标签顺序与训练时使用的标签顺序一致
2. 图片格式支持：jpg, jpeg, png, bmp, tiff, tif
3. 输出JSON文件与输入图片同名，但扩展名为.json
4. 如果检测结果为空，仍会创建JSON文件（shapes数组为空）