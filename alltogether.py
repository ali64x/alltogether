import subprocess
import argparse
import colorama
import os
import queue
import threading
import time

colorama.init()

output_lock = threading.Lock()

# intializing script's paths
shrewdeye_path = os.path.join(os.path.dirname(__file__),"shrewdeye","shrewdeye.py")
paramspider_path = os.path.join(os.path.dirname(__file__),"paramspider","paramspider.py")
httpx_exe_file = os.path.join(os.path.dirname(__file__),"httpx", "httpx.exe")
does_file= os.path.join(os.path.dirname(__file__),"DOES","does.cpp")
does_executable = os.path.join(os.path.dirname(__file__),"DOES","does.exe")
findxss_path = os.path.join(os.path.dirname(__file__),"findxss", "findxss.py")

# initializing file paths
paramspider_out = os.path.join(os.path.dirname(__file__),"result_files","paramspider_out.txt")
does_out = os.path.join(os.path.dirname(__file__),"result_files","does_out.txt")
httpx_out = os.path.join(os.path.dirname(__file__),"result_files","httpx_out.txt")
shrewdeye_out = os.path.join(os.path.dirname(__file__),"result_files","shrewdeye_out.txt")
findxss_out = os.path.join(os.path.dirname(__file__),"result_files","findxss_out.txt")
progress_file = os.path.join(os.path.dirname(__file__),"findxss","progress.txt")
process_number = os.path.join(os.path.dirname(__file__),"process_num.txt")
skipped = os.path.join(os.path.dirname(__file__),"skipped_by_paramspider.txt")
# process_details = os.path.join(os.path.dirname(__file__),"last_.txt")

def continue_extraction(process_num):
    if process_num == 1:
        return 1
    elif process_num == 2:
        print("running httpx ...\n")
        httpx(shrewdeye_out , httpx_out, resume=True)
        
        print("passing to the paramspider tool ...")
        paramspider_mod(httpx_out,paramspider_out)
        
        # # Pass the generated file to does tool to get as much urls as possible without duplicates
        print("passing to the does tool...")
        does(paramspider_out,does_out)

    elif  process_num == 3:
        
        print("passing to the paramspider tool ...")
        paramspider_mod(httpx_out,paramspider_out)
        
        # # Pass the generated file to does tool to get as much urls as possible without duplicates
        print("passing to the does tool...")
        does(paramspider_out,does_out)
        
    elif  process_num == 4:
        print("passing to the does tool...")
        does(paramspider_out,does_out)
        
    elif process_num == 5 :
        return 5

def compile_c_file(filename, outputpath):
    
        compile_process = subprocess.Popen(['g++', filename , '-o', outputpath], 
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
        
        compile_error = compile_process.communicate()

        if compile_process.returncode != 0:
            print("Compilation failed:", compile_error.decode('utf-8'))
            return None
        
def write_output(stdout_pipe, stderr_pipe):
    
    flag1 = threading.Event()
    flag2= threading.Event()
    flag1.set()
    flag2.set()
    
    def readoutput(pipe, queue,flag_event):
        try:    
            while flag_event.is_set():
                data = pipe.read()
                if not data:
                    break
                queue.put(data)
            flag_event.clear()
            
        except Exception as e:
            print("An error occurred:", e)
    
    q = queue.Queue()
    o = threading.Thread(target=readoutput, args=(stdout_pipe, q,flag1))
    e = threading.Thread(target=readoutput, args=(stderr_pipe, q,flag2))
    
    o.start()
    e.start()
    
    while flag1.is_set() or flag2.is_set():
        with output_lock:
            if not q.empty() :
                output_line = q.get()
                print(output_line,end='')
    
    if not q.empty():
        print(q.get(),end='') # Print the remaining content in the Queue

    o.join()
    e.join()

def shrewdeye(url,outputfile):
    # empty the output file before start 
    with open(shrewdeye_out,'w',encoding='utf-8') as f:
        f.write("")
    with open(process_number,'w') as pn :
        pn.write("1")
    try:
        process = subprocess.Popen(['python3', shrewdeye_path , '-u', url, '-o', outputfile], 
                                   stdin=subprocess.PIPE, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, 
                                   universal_newlines=True)
        
        write_output(process.stdout,process.stderr)
        
        print("shrewdeye completed successfully.")
    except Exception as e:
        print("Error:", e)

def httpx(list_of_urls, output_file,resume=False):
    
    with open(process_number,'w') as pn :
        pn.write("2")
        
    try:
        
        if resume :
            subprocess.run([httpx_exe_file, '-l', list_of_urls, '-o', output_file,'-resume'])
        else:
            # empty the output file before start 
            with open(httpx_out,'w',encoding='utf-8') as f:
                f.write("")
                
            subprocess.run([httpx_exe_file, '-l', list_of_urls, '-o', output_file])
        
        # write_output(process.stdout,process.stderr)
        
        print(f"httpx completed successfully,check {output_file} for result.")

    except Exception as e:
        print("Error:", e)

def paramspider_mod(lista, outputfile):
    with open(paramspider_out,'w',encoding='utf-8') as f:
        f.write("")
    with open(process_number,'w') as pn :
        pn.write("3")
    try:
        subprocess.run(["python3", paramspider_path, '-l', lista, '-o', outputfile])

        # write_output(process.stdout,process.stderr)
            
            
    except Exception as e:
        print("Error:", e)
        
def does(input_file_path,output_file_path):
    with open(does_out,'w',encoding='utf-8') as f:
        f.write("")
    with open(process_number,'w') as pn :
        pn.write("4")
    try:
        if not os.path.exists(does_executable) or os.path.getmtime(does_file) > os.path.getmtime(does_executable):
            print("Compiling...")
            compile_c_file(does_file, does_executable)
            print("Compilation successful!")
        else :
            print("exe is uptodate , skipping compilation ...")    
        print("Running the program...")

        process = subprocess.Popen([does_executable],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        
        process.stdin.write(input_file_path + '\n')
        process.stdin.flush()
        process.stdin.write(output_file_path + '\n')
        process.stdin.flush()

        while process.poll() is None :
            print("formatting , please wait ../", end='\r', flush=True) 
            time.sleep(0.5)
            print("formatting , please wait ..\\", end='\r', flush=True)  
            time.sleep(0.5)
        process.wait()
        print(f"process has been completed ,check {output_file_path} for results .")
        
    except Exception as e:
        print("Error:", e)

def findxss(input_file_path,output_file_path,email=None,c=False):
    with open(process_number,'w') as pn :
        pn.write("5")
    try:
        with open(progress_file,'r',encoding='utf-8') as pro :
            check = pro.readline()
            
        if c:
            if check:
                print(colorama.Fore.CYAN + "A previous run of this script was found." + colorama.Style.RESET_ALL)
                x = input(colorama.Fore.RED + 'Do you want to continue ? (y/N) : ' + colorama.Style.RESET_ALL).lower().strip()
                
                if x == "y":
                    subprocess.run(['python3', findxss_path , '-c', 'y'])
                    
                elif x == "n":
                    print(colorama.Fore.GREEN + "starting new run ..." + colorama.Style.RESET_ALL)
                    with open(findxss_out,'w',encoding='utf-8') as f:
                        f.write("")
                        
                    if email:
                        subprocess.run(['python3', findxss_path , '-l', input_file_path, '-o', output_file_path , '-e', email ])
                    else:
                        subprocess.run(['python3', findxss_path , '-l', input_file_path, '-o', output_file_path ])
                        
        else:
            
            # empty the output file before start 
            with open(findxss_out,'w',encoding='utf-8') as f:
                f.write("")
                
            if email:
                subprocess.run(['python3', findxss_path , '-l', input_file_path, '-o', output_file_path , '-e', email ])
            else:
                subprocess.run(['python3', findxss_path , '-l', input_file_path, '-o', output_file_path ])
                    
        print(colorama.Fore.LIGHTGREEN_EX + "Findxss completed its run successfully." + colorama.Style.RESET_ALL)
        
    except Exception as e:
        with open(process_number,'w') as pn :
            pn.write("5")
        print("Error:", e)

def main():
    
    parser = argparse.ArgumentParser(description="Mining URLs from dark corners of Web Archives ")
    parser.add_argument("-u", "--url", help="enter the domain you want to extract subdomains for .")
    parser.add_argument("-o", "--output", help="provide output file path , default path is 'output.txt' .", default = findxss_out )
    parser.add_argument("-e", "--email", help="provide email if you want to recieve updates about the progress .", default = None)
    parser.add_argument("-c", "--continues", help="continue previouse work of the last file (True To Enable) .", default = False)
    args = parser.parse_args()
    
    if args.continues :
        
        with open (process_number,'r') as p:
            pn=int(p.read().strip())
            
        if  pn == 1:
            print(colorama.Fore.LIGHTRED_EX +'No previous runs available , please enter the URL or use -h for more information '+ colorama.Style.RESET_ALL)
        elif pn > 1 and pn < 5 :
            continue_extraction(pn)
            findxss(does_out , args.output ,args.continues)
        elif pn == 5 :
            findxss(does_out , args.output ,args.continues)
        else :
            print('please use -c flag after an incomplete run ' )
            
    else:
       
        # # Run the first script to generate output
        print("Running Shrewdeye...")
        shrewdeye(args.url,shrewdeye_out)
        
        # # Pass the generated file to httpx to filter non live domains
        print("passing to the httpx tool...\n")
        httpx(shrewdeye_out , httpx_out)
        
        # # Pass the generated file to paramspider to generate urls for each subdomain
        print("passing to the paramspider tool ...")
        paramspider_mod(httpx_out,paramspider_out)
        
        # # Pass the generated file to does tool to get as much urls as possible without duplicates
        print("passing to the does tool...")
        does(paramspider_out,does_out)
        
        # # Pass the generated file to does tool to get as much urls as possible without duplicates
        print("passing to the findxss tool...")
        findxss(does_out , args.output ,args.email,args.continues)

if __name__ == "__main__":
    main()