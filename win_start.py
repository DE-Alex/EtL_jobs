#In case of faults:
#0) clear browser's cookies (status code 502)
#1) check user_agent in browser (may be it changes after browser update)
#2) function that generates requests (Upwork changes it frequently)
#3) check Headers in requests_upwork and browsers Header 

import subprocess
import sys, time
import traceback
import configparser
from datetime import datetime, timedelta
from pathlib import Path
from dateutil.tz import tzlocal
tzlocal = tzlocal()

import main_1_check
import main_2_download

config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))
logs_folder = Path(sys.path[0], config['parser_paths']['logs_folder'])
err_path = Path(logs_folder, config['parser_paths']['errors_file'])

def main():
    errors = 0
    checkpoint = datetime.now(tzlocal)
    try:
        while True:
            now = datetime.now(tzlocal)
            if now >= checkpoint:
                time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()
                print(now.replace(microsecond = 0).isoformat())
                print('======   Script 1. start to check    ======')
                main_1_check.check_new_jobs()
                print('======   Script 2. start to download    ======')                
                main_2_download.download_jobs()
                checkpoint = datetime.now(tzlocal) + timedelta(minutes = 10)
            else:
                delta = checkpoint - now
                print(f'Sleeping for {delta.seconds} seconds')
                time.sleep(60)
    except SystemExit as e:
        print('Exit.')
    except Exception as e:
        print(e)
        e = traceback.format_exc()
        print(e)
        errors += 1
        time_now = datetime.now(tzlocal).replace(microsecond = 0).isoformat()#datetime to str in isoformat 
        with open(err_path, 'a') as file: 
            file.write(time_now + '\n' + str(e) + '\n')
    finally:
        if errors > 10:
            input('Paused. Press any key.')
            errors = 0
            
main()
	
		
if __name__ == '__main__':
    main()

