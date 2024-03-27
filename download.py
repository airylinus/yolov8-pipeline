import requests
import os


def download_images(file_path, output_directory, file_prefix):

    # 如果输出目录不存在，则创建目录
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)


    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for idx, line in enumerate(lines):
            url = line.strip()
            print(url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # 获取文件名
                    file_name = os.path.join(output_directory, f"image_{file_prefix}_{idx}.jpg")
                    # 保存图片到本地
                    with open(file_name, 'wb') as img_file:
                        img_file.write(response.content)
                        print(f"下载图片 {file_name} 成功")
                else:
                    print(f"无法下载图片 {url}")
            except Exception as e:
                print(f"下载图片 {url} 时出错: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("error parameters : len(sys.argv) != 4", len(sys.argv))
        print("Usage: python download.py <file_path> <output_directory> <file_prefix>")
        print("Example: python download.py image-urls.txt app_with_marked")
        exit(1)
    url_file = sys.argv[1]
    output_directory = sys.argv[2]
    file_prefix = sys.argv[3]
    # download_images("images-withmark.txt", "app_with_marked")
    download_images(url_file, output_directory, file_prefix)
