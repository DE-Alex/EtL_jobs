import sys, shutil
import Libs.PC_or_Mobile 

print 'renaming MAIN to main'


CWD = Libs.PC_or_Mobile.Check_for_CWD() #checking work directory

	
MAIN = CWD + "/MAIN.PY"
main = CWD + '/main.py'
shutil.move(MAIN, main)

exec(open(main).read())

