import requests
from bs4 import BeautifulSoup
import os
import argparse


def download_file(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

def main():
    parser = argparse.ArgumentParser(description="Mining URLs from dark corners of Web Archives ")
    parser.add_argument("-u", "--url", help="enter the domain you want to extract subdomains for .")
    parser.add_argument("-o", "--output", help="provide output file path , default path is 'output.txt' .", default= "output.txt" )
    args = parser.parse_args()

    url = "https://shrewdeye.app/domains/"+str(args.url)+".txt"
    save_path = args.output

    response = requests.get(url)
    if response.status_code == 200:
        print(f"Downloading file from {url}...")
        download_file(url, save_path)
        print(f"File downloaded and saved to {save_path}")
    else:
        print("Failed to retrieve the webpage.")

if __name__ == "__main__":
    main()
