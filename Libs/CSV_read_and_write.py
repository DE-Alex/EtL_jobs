import sys
import csv


def CSV_write(path, row_to_write): 
	csvFile = open(path, 'wb')
	writer = csv.writer(csvFile, delimiter = ';')
	writer.writerow(row_to_write)
	#writer.writerow(('2','2','2','2','2'))
	#writer.writerow(('3','3','3','3','3'))
	csvFile.close()
	print 'Write OK'
	
def CSV_add(path, row_to_write): 
	csvFile = open(path, 'ab')
	writer = csv.writer(csvFile, delimiter = ';')
	writer.writerow(row_to_write)
	#writer.writerow(('2','2','2','2','2'))
	#writer.writerow(('3','3','3','3','3'))
	csvFile.close()
	print 'Add OK'
		
def CSV_Read(path): 
	csvFile = open(path)
	reader = csv.reader(csvFile, delimiter = ';')
	Data = list(reader)
	csvFile.close()
	print 'Read OK'
	return Data
	
	
	
if __name__ == '__main__':
	import PC_or_Mobile 
	CWD = PC_or_Mobile.Check_for_CWD() #checking work directory
	path = CWD + '\\' + 'testDB.csv'
	
	row_to_write = ('1','1','1','1','1')
	CSV_write(path, row_to_write)
	
	CSV_add(path, row_to_write)
	CSV_add(path, row_to_write)
	
	print 'Reading from:', path
	DBraw = CSV_Read(path) #Data in lists
	
	for site in DBraw:
		print site