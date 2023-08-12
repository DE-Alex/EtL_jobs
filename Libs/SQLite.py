import sqlite3

def connect(path):
	try:
		db = sqlite3.connect(path)
	except sqlite3.DatabaseError as err:
		print('Error: ', err)
	else:
		return db
	
def Create_Table(table, db):
	try:
		cursor = db.cursor()
		cursor.execute('''
		CREATE TABLE jobs(id INTEGER PRIMARY KEY, )
		''')
	except sqlite3.DatabaseError as err:
		print('Error: ', err)
	else:
		db.commit()
	
	
def Insert(data, db):
	try:
		cursor = db.cursor()
		cursor.execute('''
		INSERT INTO jobs(... )
		VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,)''',
		(data))
	except sqlite3.DatabaseError as err:
		print('Error: ', err)
	else:
		db.commit()

def Delete_Table(table, db):
	try:
		cursor = db.cursor()
		cursor.execute(''' DROP TABLE users
		''')
	except sqlite3.DatabaseError as err:
		print('Error: ', err)
	else:
		db.commit()
	
	
if __name__ == '__main__':
	import PC_or_Mobile 
	CWD = PC_or_Mobile.Check_for_CWD()
	SQLbase = CWD + '\\test_SQLbase'#Upwork jobs
	db = connect(SQLbase)
	db.close()
	print 'SQL base closed successfully'
	

