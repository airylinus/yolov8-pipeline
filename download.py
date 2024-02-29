import requests
import os

base_url = "https://static.gzsle.com/"

# 读取文件中的每一行 URL
def download_images_from_urls(file_path, output_directory):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for idx, line in enumerate(lines):
            url = base_url + line.strip()
            print(url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # 获取文件名
                    file_name = os.path.join(output_directory, f"image_{idx}.jpg")
                    # 保存图片到本地
                    with open(file_name, 'wb') as img_file:
                        img_file.write(response.content)
                        print(f"下载图片 {file_name} 成功")
                else:
                    print(f"无法下载图片 {url}")
            except Exception as e:
                print(f"下载图片 {url} 时出错: {e}")


def download_images(file_path, output_directory):

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
                    file_name = os.path.join(output_directory, f"image_{idx}.jpg")
                    # 保存图片到本地
                    with open(file_name, 'wb') as img_file:
                        img_file.write(response.content)
                        print(f"下载图片 {file_name} 成功")
                else:
                    print(f"无法下载图片 {url}")
            except Exception as e:
                print(f"下载图片 {url} 时出错: {e}")


# 用法示例
file_path = 'xcx_images.log'  # 替换为你的文件路径
output_directory = 'downloaded_images'  # 替换为你想要保存图片的目录路径

# 如果输出目录不存在，则创建目录
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# download_images_from_urls(file_path, output_directory)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("error parameters : len(sys.argv) != 4", len(sys.argv))
        print("Usage: python download.py <file_path> <output_directory>")
        print("Example: python download.py image-urls.txt app_with_marked")
        exit(1)
    url_file = sys.argv[1]
    output_directory = sys.argv[2]
    # download_images("images-withmark.txt", "app_with_marked")
    download_images(url_file, output_directory)
