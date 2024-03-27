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


set "destination_dir_train=%labeled_images_dir%_train"
set "destination_dir_test=%labeled_images_dir%_test"

echo %destination_dir_train%
echo %destination_dir_test%

rem create output directories
if not exist "%destination_dir_train%" mkdir "%destination_dir_train%"
if not exist "%destination_dir_test%" mkdir "%destination_dir_test%"


rem 获取源文件夹中所有的 JSON 文件列表
set "file_count=0"
for %%F in ("%labeled_images_dir%\*.json") do (
    set /a "file_count+=1"
    set "json_files[!file_count!]=%%~nF"
)

rem 对每个 JSON 文件进行随机判断并拷贝
for /l %%i in (1, 1, %file_count%) do (
    set /a "random_num=!random! %% 10 + 1"
    if !random_num! LEQ 2 (
        set "destination_dir=!destination_dir_test!"
    ) else (
        set "destination_dir=!destination_dir_train!"
    )
    rem 拷贝 JSON 文件
    copy "%source_dir%\!json_files[%%i]!.json" "!destination_dir!\"
    rem 拷贝同名的 JPG 文件
    copy "%source_dir%\!json_files[%%i]!.jpg" "!destination_dir!\"
)

echo Done.
