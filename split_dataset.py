import os
import random
import shutil
import sys

def split_dataset(dataset_dir: str):

    # 创建目标文件夹
    os.makedirs(dataset_dir + '-train', exist_ok=True)
    os.makedirs(dataset_dir + '-test', exist_ok=True)

    # 获取源文件夹中所有的 JSON 文件列表
    json_files = [filename[:-5] for filename in os.listdir(dataset_dir) if filename.endswith('.json')]

    # 对每个 JSON 文件进行随机判断并拷贝
    for filename in json_files:
        random_num = random.randint(1, 10)
        if random_num <= 2:
            destination_dir = dataset_dir + '-test'
        else:
            destination_dir = dataset_dir + '-train'
        
        if not os.path.exists(os.path.join(dataset_dir, filename + '.jpg')):
            continue
        # 拷贝 JSON 文件
        shutil.copy(os.path.join(dataset_dir, filename + '.json'), destination_dir)
        # 拷贝同名的 JPG 文件
        shutil.copy(os.path.join(dataset_dir, filename + '.jpg'), destination_dir)

    print("Done.")

if __name__ == "__main__":
    dataset_dir = sys.argv[1]
    split_dataset(dataset_dir)






