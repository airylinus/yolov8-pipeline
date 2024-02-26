@echo off
setlocal

rem check if the parameter is provided 
if "%~1"=="" (
    echo Undefined Labeled Images Directory. 
    exit /b 1
)

rem check if the parameter is provided 
if "%~2"=="" (
    echo Undefined Labeled Images Directory. 
    exit /b 1
)

rem PrintOutFirstParameter 
echo -------------- start --------------
echo Labeled Images Directory:    %1 
echo Output Directory:            %2

set labeled_images_dir=%1
set output_dir=%2

python prepare-labels.py %labeled_images_dir% %output_dir% 

echo -------------- new labels generated --------------
CD X-AnyLabeling220-main
python .\tools\label_converter.py --mode custom2yolo --src_path ..\%labeled_images_dir% --dst_path ..\%output_dir%\yolodata --classes ..\%output_dir%\fixed_labels.txt

CD ..\
echo -------------- move images to yolodata --------------
copy /Y .\%labeled_images_dir%\*.jpg .\%output_dir%\yolodata\

echo -------------- split train and test --------------
python split_train.py %output_dir%

echo -------------- generate data yaml --------------
python generate_yaml.py %output_dir%
echo Done!
echo open C:\Users\Mongo\AppData\Roaming\Ultralytics\
echo change path and start trainning
endlocal

