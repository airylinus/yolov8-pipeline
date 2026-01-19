@echo off
setlocal

rem check if the parameter is provided 
if "%~1"=="" (
    echo Undefined Labeled Images Directory. 
    exit /b 1
)

rem PrintOutFirstParameter 
echo -------------- start --------------
echo Labeled Images Directory:    %1 

set labeled_images_dir=%1
set output_dir=%labeled_images_dir%\..\yolodata
if not exist "%output_dir%" mkdir "%output_dir%"

rem 检查同级目录下是否存在 labels.txt 文件
set existing_labels_file=%labeled_images_dir%\..\labels.txt
set labels_param=

if exist "%existing_labels_file%" (
    echo -------------- existing labels.txt found, will reuse and append new labels --------------
    set labels_param=%existing_labels_file%
) else (
    echo -------------- no existing labels.txt found, generating new labels --------------
)

echo -------------- split labeled images --------------
python split_dataset.py %labeled_images_dir%

rem python init_labels.py %labeled_images_dir% %output_dir% %labels_param%
python init_labels.py %labeled_images_dir% %output_dir% %labels_param%

echo -------------- new labels generated --------------
python .\label_converter.py --mode custom2yolo --src_path %labeled_images_dir%-train --dst_path %output_dir%\train\labels --classes %output_dir%\labels.txt
python .\label_converter.py --mode custom2yolo --src_path %labeled_images_dir%-test --dst_path %output_dir%\val\labels --classes %output_dir%\labels.txt

echo -------------- move images to yolodata train --------------
if not exist "%output_dir%\train" mkdir "%output_dir%\train"
if not exist "%output_dir%\train\images" mkdir "%output_dir%\train\images"
copy /Y %labeled_images_dir%-train\*.jpg %output_dir%\train\images

echo -------------- move images to yolodata test --------------
if not exist "%output_dir%\val" mkdir "%output_dir%\val"
if not exist "%output_dir%\val\images" mkdir "%output_dir%\val\images"
copy /Y %labeled_images_dir%-test\*.jpg %output_dir%\val\images

echo -------------- generate data yaml --------------
python generate_yaml.py %output_dir%
echo Done!
echo open C:\Users\Mongo\AppData\Roaming\Ultralytics\
echo change path and start trainning
endlocal

