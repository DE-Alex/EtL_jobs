import sys
import csv

if sys.path[0] == '\\storage\\emulated\\0\\qpython':
	CWD = sys.path[0] + '\\projects\\parser'
else:
	CWD = sys.path[0]	

def DBsave(CWD): 
	csvFile = open(CWD + '\\Templates\\DB.csv', 'wb')
	writer = csv.writer(csvFile)
	writer.writerow(('1','1','1','1','1'))
	writer.writerow(('2','2','2','2','2'))
	writer.writerow(('3','3','3','3','3'))
	writer.writerow(('3','3','3','3','3'))
	csvFile.close()
	print 'Write OK'
	csvFile.close()
	
def DBload(CWD): 
	csvFile = open(CWD + '\\Templates\\DB.csv')
	reader = csv.reader(csvFile)
	Data = list(reader)
	print Data
	# print 'Read OK'
	# for row in reader:
		# print (str(row))
	print 'By rows OK'
	csvFile.close()
	return Data
	
	
	
if __name__ == '__main__':
	import sys
	if sys.path[0] == '\\storage\\emulated\\0\\qpython':
		CWD = sys.path[0] + '\\projects\\parser'
	else:
		CWD = sys.path[0]	
	
	DBsave(CWD)
	Data = DBload(CWD)
	
	