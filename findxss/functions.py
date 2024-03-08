import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from concurrent.futures import ThreadPoolExecutor, wait,as_completed
import time
import threading
from termcolor import colored
import sys
import os
import colorama
# from prompt_toolkit import Application, ProgressBar, Text

colorama.init()

output_lock = threading.Lock() # krmel l threads ma yiktbo ma3 ba3d w y5arrbo l dinya
lock=threading.Lock()
found_lock=threading.Lock()
progress_lock = threading.Lock()
exception_lock = threading.Lock()


def appendPara(original_string, append_string): # la n3abbi l payload
    return original_string[:-1] + append_string

def send_email(to_address, subject, body):# wad7a la nib3at email
    try:
        sender_email = 'auto83851@gmail.com'
        sender_password = 'zmiu chxr kfiq sftr'
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587  # Use 465 for SSL

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_address
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_address, msg.as_string())
    except Exception as e:
        pass

def check_response(url,payload,stat,outputfile,Email,tries=0,time=30):# l ossa killa 
    try:
        newURL= appendPara(url,payload)
        response=requests.get(newURL,timeout=time)
        html_content = response.text  # Use response.content for binary content
        with output_lock:
            print (stat.strip(),end='\r',flush=True)
        if html_content:
            if payload in html_content:
                if "<" in payload :
                    short_payload = "<>"
                elif '"'  in payload :
                    short_payload = '""'
                with output_lock:
                    print(
                          colored(f"\rFound ",'light_green')+" [ "+
                          colored(f"{short_payload}",'red') + 
                          colored(" ] in this webpage: ",'white')+ 
                          colored(f"{newURL}\n",'light_blue')
                          )
                with found_lock:
                    try:
                        with open(outputfile,'a+',encoding='utf-8') as xss:
                            xss.seek(0)
                            con = xss.readlines()
                            if url not in con :
                                xss.write(url)
                                if Email :
                                    send_email(Email,"XSS Finder Tool",f"Found possible XSS in this URL : {url}")
                    except FileNotFoundError as fe:
                        print(fe)
                        sys.exit()
                
                
    except RuntimeError :
        if tries < 3:
                check_response(url,payload,Email,stat,tries+1)
                time.sleep(5)
                
        with exception_lock:
           exceptions_file = os.path.join('findxss', 'exceptions.txt')
           exceptions_file=os.path.abspath(exceptions_file)
           with open(exceptions_file,'r+') as e:
              filelines=e.readlines().strip()
              if url not in filelines: 
                  e.write(url)
            
def measure_elapsed_time(flag):# la ni3rif addeh akal w2t l program
    start_time = time.time()
    while not flag.is_set():
        elapsed_time = time.time() - start_time
        with output_lock:
            print(
                colored(f"\r\rElapsed time: ",'light_grey')+
                colored(f"{elapsed_time:.2f}",'red')+
                colored(" seconds, under process url number: ",'light_grey'), 
                end='', 
                flush=True
                )
        # time.sleep(1)
        
def check_if_list_is_empty(futures,event,num_of_threads):# krmel ma nfout b race condition
    while True:
            if len(futures) <= num_of_threads*num_of_threads:
                event.set()
            else:
                event.clear()                   
                new_futures = []
                for f in futures:                        # krmel nim7i mn l list le 5olso
                    if not f.done():
                        new_futures.append(f)
                futures = new_futures
                
def search_and_extract(key, file_path):
    try:
        with lock:
          with open(file_path, 'r') as file:
            for line in file:
                index = line.find(key)
                if index != -1:
                    result=(line[index + len(key):].strip())
                    return result
    except FileNotFoundError:
        with output_lock:
            print(f"\rFile not found: {file_path}")
        sys.exit()
    return None
    
def progress (key, string):
    index = string.find(key)
    if index != -1:
        result=(string[:index].strip())
        return result
    
def total (key, string):
    index = string.find(key)
    if index != -1:
        result=(string[index+1:].strip())
        return result
    
def logo():
    logo=colorama.Fore.LIGHTMAGENTA_EX + '''
    _____           __              
   / __(_)___  ____/ /  ____________
  / /_/ / __ \\/ __  / |/_/ ___/ ___/
 / __/ / / / / /_/ />  <(__  |__  ) 
/_/ /_/_/ /_/\\__,_/_/|_/____/____/ 
                            by P.AA'''+ colorama.Style.RESET_ALL
    # print("\n"+colored(logo,"light_magenta")+"\n",flush=True)
    print("\n"+logo+"\n",flush=True)