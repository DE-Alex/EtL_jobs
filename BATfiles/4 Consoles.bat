@echo on
start D:\MTM_Proxy\bin\mitmdump.exe -s D:\Shapovalov\svoe\Python\PY\Parser5\MTM\_mtm_setHeaders.py --showhost --listen-port 35685 --mode upstream:10.10.10.10:35000
start D:\FreeProxy\FreeProxy.exe -console -CD:\FreeProxy\MyConfig.cfg
start D:\Shapovalov\svoe\Python\PY\Parser4\Scripts\python.exe D:\Shapovalov\svoe\Python\PY\Parser5\#main.py


