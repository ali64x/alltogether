import argparse
import os
import logging
import colorama
from colorama import Fore, Style
from urllib.parse import urlparse, parse_qs, urlencode
import os
import time
import requests
import random
import json
import logging
import time
import sys



logging.basicConfig(level=logging.INFO)
with open(os.path.abspath("skipped_by_paramspider.txt"), "w",encoding='utf-8') as fp:
        fp.write('')

MAX_RETRIES = 3

def load_user_agents():
    """
    Loads user agents
    """

    return [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/89.0.774.45",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36 Edge/16.16299",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 OPR/45.0.2552.898",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Vivaldi/1.8.770.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/15.15063",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/15.15063",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"
  ]

def fetch_url_content(url,proxy,domain):
    """
    Fetches the content of a URL using a random user agent.
    Retries up to MAX_RETRIES times if the request fails.
    """
    user_agents = load_user_agents()
    if proxy is not None:
        proxy={
            'http':proxy,
            'https':proxy
        }
    for i in range(MAX_RETRIES):
        user_agent = random.choice(user_agents)
        headers = {
            "User-Agent": user_agent
        }

        try:
            response = requests.get(url, proxies=proxy,headers=headers)
            response.raise_for_status()
            return response
        except (requests.exceptions.RequestException, ValueError):
            logging.warning(f"Error fetching URL {url}. Retrying in 1 seconds...")
            time.sleep(1)
        except KeyboardInterrupt:
            logging.warning("Keyboard Interrupt received. Exiting gracefully...")
            sys.exit()
    with open(os.path.abspath("skipped_by_paramspider.txt"), "a+",encoding='utf-8') as fp:
        fp.write(domain+'\n')
    logging.error(f"Failed to fetch URL {url} after {MAX_RETRIES} retries, url skipped")
    
    # sys.exit()


yellow_color_code = "\033[93m"
reset_color_code = "\033[0m"

colorama.init(autoreset=True)  # Initialize colorama for colored terminal output

log_format = '%(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
logging.getLogger('').handlers[0].setFormatter(logging.Formatter(log_format))

HARDCODED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".json",
    ".css", ".js", ".webp", ".woff", ".woff2", ".eot", ".ttf", ".otf", ".mp4", ".txt"
]

def has_extension(url, extensions):
    """
    Check if the URL has a file extension matching any of the provided extensions.

    Args:
        url (str): The URL to check.
        extensions (list): List of file extensions to match against.

    Returns:
        bool: True if the URL has a matching extension, False otherwise.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    extension = os.path.splitext(path)[1].lower()

    return extension in extensions

def clean_url(url):
    """
    Clean the URL by removing redundant port information for HTTP and HTTPS URLs.

    Args:
        url (str): The URL to clean.

    Returns:
        str: Cleaned URL.
    """
    parsed_url = urlparse(url)
    
    if (parsed_url.port == 80 and parsed_url.scheme == "http") or (parsed_url.port == 443 and parsed_url.scheme == "https"):
        parsed_url = parsed_url._replace(netloc=parsed_url.netloc.rsplit(":", 1)[0])

    return parsed_url.geturl()

def clean_urls(urls, extensions, placeholder):
    """
    Clean a list of URLs by removing unnecessary parameters and query strings.

    Args:
        urls (list): List of URLs to clean.
        extensions (list): List of file extensions to check against.

    Returns:
        list: List of cleaned URLs.
    """
    cleaned_urls = set()
    for url in urls:
        cleaned_url = clean_url(url)
        if not has_extension(cleaned_url, extensions):
            parsed_url = urlparse(cleaned_url)
            query_params = parse_qs(parsed_url.query)
            cleaned_params = {key: placeholder for key in query_params}
            cleaned_query = urlencode(cleaned_params, doseq=True)
            cleaned_url = parsed_url._replace(query=cleaned_query).geturl()
            cleaned_urls.add(cleaned_url)
    return list(cleaned_urls)

def fetch_and_clean_urls(domain, extensions, stream_output,proxy, placeholder, output):
    """
    Fetch and clean URLs related to a specific domain from the Wayback Machine.

    Args:
        domain (str): The domain name to fetch URLs for.
        extensions (list): List of file extensions to check against.
        stream_output (bool): True to stream URLs to the terminal.

    Returns:
        None
    """
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Fetching URLs for {Fore.CYAN + domain + Style.RESET_ALL}")
    wayback_uri = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=txt&collapse=urlkey&fl=original&page=/"
    response = fetch_url_content(wayback_uri,proxy,domain)
    if response :
        urls = response.text.split()
        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Found {Fore.GREEN + str(len(urls)) + Style.RESET_ALL} URLs for {Fore.CYAN + domain + Style.RESET_ALL}")
        
        cleaned_urls = clean_urls(urls, extensions, placeholder)
        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Cleaning URLs for {Fore.CYAN + domain + Style.RESET_ALL}")
        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Found {Fore.GREEN + str(len(cleaned_urls)) + Style.RESET_ALL} URLs after cleaning")
        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Extracting URLs with parameters")
        
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        if output is None :
            result_file = os.path.join(results_dir, f"{domain}.txt")
            try:
                with open(result_file, "w",encoding='utf-8') as f:
                    for url in cleaned_urls:
                        if "?" in url:
                            f.write(url + "\n")
                            if stream_output:
                                logging.info(url)
                                
            except FileNotFoundError :
                logging.error(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Unable to create/open results file.")
        else:
            result_file = f"{os.path.abspath(output)}"
            try:
                with open(result_file, "a",encoding='utf-8') as f:
                    for url in cleaned_urls:
                        if "?" in url:
                            f.write(url + "\n")
                            if stream_output:
                                logging.info(url)
            except FileNotFoundError :
                logging.error(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Unable to create/open results file.")
        
        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Saved cleaned URLs to {Fore.CYAN + result_file + Style.RESET_ALL}")
    
def main():
    """
    Main function to handle command-line arguments and start URL mining process.
    """
    log_text = """
           
                                      _    __       
   ___  ___ ________ ___ _  ___ ___  (_)__/ /__ ____
  / _ \\/ _ `/ __/ _ `/  ' \\(_-</ _ \\/ / _  / -_) __/
 / .__/\\_,_/_/  \\_,_/_/_/_/___/ .__/_/\\_,_/\\__/_/   
/_/                          /_/                    

                              with <3 by @0xasm0d3us           
    """
    colored_log_text = f"{yellow_color_code}{log_text}{reset_color_code}"
    logging.info(colored_log_text)
    parser = argparse.ArgumentParser(description="Mining URLs from dark corners of Web Archives ")
    parser.add_argument("-d", "--domain", help="Domain name to fetch related URLs for.")
    parser.add_argument("-l", "--list", help="File containing a list of domain names.")
    parser.add_argument("-s", "--stream", action="store_true", help="Stream URLs on the terminal.")
    parser.add_argument("--proxy", help="Set the proxy address for web requests.",default=None)
    parser.add_argument("-p", "--placeholder", help="placeholder for parameter values", default="FUZZ")
    parser.add_argument("-o", "--output", help="output file path.")
    args = parser.parse_args()

    if not args.domain and not args.list:
        parser.error("Please provide either the -d option or the -l option.")

    if args.domain and args.list:
        parser.error("Please provide either the -d option or the -l option, not both.")

    if args.list:
        with open(args.list, "r") as f:
            domains = [line.strip().lower().replace('https://', '').replace('http://', '') for line in f.readlines()]
            domains = [domain for domain in domains if domain]  # Remove empty lines
            domains = list(set(domains))  # Remove duplicates
    else:
        domain = args.domain

    extensions = HARDCODED_EXTENSIONS

    if args.domain:
        fetch_and_clean_urls(domain, extensions, args.stream, args.proxy, args.placeholder, args.output)

    if args.list:
        for domain in domains:
            fetch_and_clean_urls(domain, extensions, args.stream,args.proxy, args.placeholder,args.output)
            time.sleep(0.5)
            
if __name__ == "__main__":
    main()