import os
import zipfile
import requests

def download_and_extract_movielens():
    url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
    output_dir = "../data/"
    zip_path = os.path.join(output_dir, "ml-100k.zip")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Downloading MovieLens 100k dataset...")
    response = requests.get(url)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    print("Extracting...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    print("Done!")

if __name__ == "__main__":
    download_and_extract_movielens()
