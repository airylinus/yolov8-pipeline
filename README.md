# yolov8-pipeline

This repository implements a tool which can be used to generate a YOLOv8 dataset from a set of images and annotations created by X-AnyLabeling ( https://github.com/CVHub520/X-AnyLabeling ).



## Usage

> .\data-prepare.bat D:\dataset\apple-orange-banana-detection

You'll get a folder named `yolodata` in the directory `D:\dataset\apple-orange-banana-detection\yolodata`, which contains the all files needed for training YOLOv8.

## New Features

### 1. Label Reuse Logic (标签复用逻辑)

#### Feature Description
The `data-prepare.bat` script now automatically detects and reuses existing `labels.txt` files from the parent directory. This ensures that when processing new datasets for model fine-tuning, the original label indices remain unchanged, maintaining compatibility with existing trained models.

#### How It Works
- When running `data-prepare.bat`, the script checks if `../labels.txt` exists relative to the input directory
- If found, it reuses the existing labels as the base and appends any new labels discovered in the current dataset
- Existing labels maintain their original order and indices
- New labels are added to the end of the label list

#### Usage Examples

```bash
# Basic usage (automatically detects and reuses existing labels.txt)
.\data-prepare.bat D:\dataset\new-fruits-detection

# The script will:
# 1. Check if D:\dataset\labels.txt exists
# 2. If found, load existing labels (e.g., ["apple", "banana", "orange"])
# 3. Process new dataset and discover new labels (e.g., ["grape", "pear"])
# 4. Generate final labels.txt: ["apple", "banana", "orange", "grape", "pear"]
# 5. Indices 0-2 remain unchanged, new labels get indices 3-4
```

#### Benefits
- **Model Compatibility**: Existing model weights remain valid for old labels
- **Fine-tuning Ready**: Perfect for incremental learning and model fine-tuning
- **Automatic Detection**: No manual configuration needed
- **Index Stability**: Prevents label index shifts that could break trained models

### 2. YOLOv8 Model Inference Script (YOLOv8模型推理脚本)

#### Feature Description
The `yolo_inference.py` script allows you to run inference on trained YOLOv8 models and save detection results in annotation file format. This is useful for automated labeling, validation, and generating ground truth data.

#### Prerequisites
```bash
pip install ultralytics pillow numpy
```

#### Basic Usage
```bash
python yolo_inference.py <model_path> <labels_file> <image_dir> [options]
```

#### Parameters
- `model_path`: Path to the trained YOLOv8 model file (.pt)
- `labels_file`: Path to the labels.txt file containing class names
- `image_dir`: Directory containing images to process

#### Optional Parameters
- `--output_dir, -o`: Output directory for annotation files (default: same as image_dir)
- `--conf, -c`: Confidence threshold for detections (default: 0.25)
- `--save_images, -s`: Save inference result images with bounding boxes

#### Usage Examples

```bash
# Basic inference on a directory of images
python yolo_inference.py yolov8n.pt labels.txt images/

# Specify output directory and confidence threshold
python yolo_inference.py yolov8n.pt labels.txt images/ --output_dir results/ --conf 0.5

# Save both annotation files and result images
python yolo_inference.py yolov8n.pt labels.txt images/ --save_images

# Process images in subdirectories
python yolo_inference.py model.pt labels.txt dataset/train/images/
```

#### Output Format
The script generates JSON annotation files with the same name as input images but with `.json` extension. The format matches the annotation standard used in X-AnyLabeling:

```json
{
  "version": "2.4.4",
  "flags": {},
  "shapes": [
    {
      "label": "apple",
      "score": 0.95,
      "points": [
        [107.01, 160.69],
        [204.71, 160.69],
        [204.71, 427.36],
        [107.01, 427.36]
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
  "imagePath": "image.jpg",
  "imageData": null,
  "imageHeight": 1280,
  "imageWidth": 960
}
```

#### Append Mode
If an annotation JSON file already exists for an image, the script will append new detections to the existing file instead of overwriting it. This is useful for:
- Incremental annotation
- Combining results from multiple models
- Adding annotations to partially labeled datasets

#### Supported Image Formats
- JPG/JPEG
- PNG
- BMP
- TIFF/TIF

#### Label Mapping
The script uses the `labels.txt` file to map model output class indices to human-readable label names:

```
# labels.txt example
apple
banana
orange
grape
```

Model predictions with class index 0 will be labeled as "apple", index 1 as "banana", etc.

#### Performance Tips
- Use higher confidence thresholds (`--conf 0.5`) for cleaner results
- Process images in batches by organizing them in subdirectories
- Use GPU-enabled models for faster inference on large datasets

#### Duplicate Detection (重复检测)
The script includes intelligent duplicate detection to prevent the same object from being detected multiple times when appending to existing annotation files.

**How it works:**
- When appending to existing annotation files, the script compares new detections with existing annotations
- If two bounding boxes of the same label have an IOU (Intersection over Union) greater than 85%, the new detection is considered a duplicate
- Duplicate detections are filtered out, preserving the original annotations
- A log message is printed for each filtered duplicate detection

**Benefits:**
- Prevents annotation file pollution with redundant detections
- Maintains data quality when re-running inference on the same images
- Useful for iterative annotation workflows

**IOU Threshold:**
- Default threshold: 85% (configurable via code modification)
- Only compares detections with the same label
- Preserves the original annotation's position and attributes

#### Error Handling
The script includes comprehensive error handling for:
- Missing model files
- Invalid label files
- Corrupted images
- Permission issues
- Model loading failures

Each error is reported with detailed messages to help troubleshoot issues.
