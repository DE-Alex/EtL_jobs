import sys, shutil

print 'renaming MAIN to main'

print sys.path[0]

if sys.path[0] == '\\storage\\emulated\\0\\qpython':
	CWD = sys.path[0] + '\\projects\\parser'
else:
	CWD = sys.path[0]

	
MAIN = CWD + "/MAIN.PY"
main = CWD + '/main.py'
shutil.move(MAIN, main)

exec(open(main).read())

