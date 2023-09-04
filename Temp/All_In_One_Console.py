import subprocess
import sys
from pathlib import Path

#print('====== 1. start Free Proxy  ======')
#Proxy = subprocess.Popen(r'D:\FreeProxy\FreeProxy.exe -console -CD:\FreeProxy\MyConfig.cfg')
# print('====== 2. start ReloadBrwsr ======')
# Browser = subprocess.Popen(r'D:\Shapovalov\svoe\Python\PY\Parser4\Scripts\python.exe D:\Shapovalov\svoe\Python\PY\Parser5\ReloadBRSR\ReloadBrwsr.py')
print('======   2. start Parser    ======')
MAIN =  subprocess.Popen(r'D:\Shapovalov\svoe\Python\PY\Parser6\Scripts\python.exe D:\Shapovalov\svoe\Python\PY\Parser6\#main.py')
print('======    3. start MTM     ======')

#With FreeProxy
# process = subprocess.run(r'd:\MTM_Proxy\bin\mitmdump.exe -s D:\Shapovalov\svoe\Python\PY\Parser5\MTM\_mtm_setHeaders.py --listen-port 35685 --mode upstream:10.10.10.10:35000', 
						 # stdout=subprocess.PIPE, 
						 # universal_newlines=True)
						 
#With Squid service + Proton VPN
# process = subprocess.run(r'd:\MTM_Proxy\bin\mitmdump.exe -s D:\Shapovalov\svoe\Python\PY\Parser5\MTM\_mtm_setHeaders.py --listen-port 35685 --mode upstream:127.0.0.1:3128', 
						 # stdout=subprocess.PIPE, 
						 # universal_newlines=True)
						 
#With Open VPN


#process = subprocess.run(r'd:\MTM_Proxy\bin\mitmdump.exe -s D:\Shapovalov\svoe\Python\PY\Parser5\MTM\_mtm_setHeaders.py --listen-port 35685', 
headersPath = Path(sys.path[0], 'mitm', 'mitm_setHeaders.py')
process = subprocess.run(r'd:\MTM_Proxy\bin\mitmdump.exe -s headersPath --listen-port 35685', 
						 stdout=subprocess.PIPE, 
						 universal_newlines=True)						 
						 
process
process.stdout
print('======       Finished       ======')
