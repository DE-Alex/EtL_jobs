import MyLibs.SQLite
import MyLibs.Scan_DirsFiles
					
Renames = {
'Content & Copywriting':'Content Writing'#,
# 'Technical Support': 'Tech Support & Content Moderation',
# 'Personal/Virtual Assistant': 'Personal/Virtual Assistance',
# 531770282605834245:	531770282605834246, 
# 531770282605834244: 1484275156546932736,
# 531770282597445633:	531770282584862726,
}



('531770282580668423', '531770282601639938', 'Other - Writing', '531770282580668423', '531770282601639938', 'Content Writing'),
('531770282580668422', '531770282593251343', 'Marketing & Brand Strategy', '531770282580668422', '531770282593251343', 'Marketing, PR & Brand Strategy'),
('-', '-', '-', '531770282580668423', '1534904462131675136', 'Sales & Marketing Copywriting'),
('531770282580668422', '531770282597445639', 'Social Media & PR Services', '531770282580668422', '531770282597445639', 'Social Media Marketing & Strategy'),
('-', '-', '-', '531770282580668423', '1534904461833879552', 'Personal & Professional Coaching'),
('-', '-', '-', '531770282584862721', '1534904461833879552', 'Personal & Professional Coaching'),
('531770282580668423', '531770282601639936', 'Grant & Proposal Writing', '531770282580668423', '531770282601639936', 'Professional & Business Writing'),
('531770282584862721', '531770282601639946', 'Human Resources', '531770282584862721', '531770282601639946', 'Recruiting & Human Resources'),
('531770282580668423', '531770282597445645', 'Creative Writing Services', '531770282580668423', '531770282597445645', 'Content Writing'),
('531770282584862720', '531770282601639939', 'Translation & Localization', '531770282584862720', '531770282601639939', 'Translation & Localization Services'),
('-', '-', '-', '531770282584862720', '1534904461842268160', 'Language Tutoring & Interpretation'),
('531770282584862722', '531770282601639949', 'Buildings & Landscape Architecture', '531770282584862722', '531770282601639949', 'Building & Landscape Architecture'),
('531770282580668423', '531770282597445646', 'Technical Writing', '531770282580668423', '531770282597445646', 'Professional & Business Writing'),
('531770282584862720', '531770282601639940', 'Legal, Medical & Technical Translation', '531770282584862720', '531770282601639940', 'Translation & Localization Services'),
('531770282580668423', '531770282601639937', 'Resumes & Cover Letters', '531770282580668423', '531770282601639937', 'Professional & Business Writing'),



if __name__ == '__main__':
	DB_Folder = rf'D:\DB_Upwork'
	table_name = 'Jobs'

	FilePaths, _ = MyLibs.Scan_DirsFiles.SubdirScanPaths(DB_Folder)
	DB_files = [i for i in FilePaths if ('.sqlite3' in i) and ('_Empty' not in i)]
	columns = ['ID', 'occupations_category', 'occupations_subcategories', 'category2_uid', 'subcategory2_uid']
	for file in DB_files:
		try:
			print(file, '...', end='')

			db = MyLibs.SQLite.connect(file)
			data = MyLibs.SQLite.Select(table_name, db, select_col = columns)
			db.close()
			NewData = []
			for row in data:
				id, catLabel, subCatLabel, catUid, subCatUid = row
				if subCatLabel in Renames:  subCatLabel = Renames[subCatLabel]
				if subCatUid in Renames:  subCatUid = Renames[subCatUid]
				if catLabel in Renames:  catLabel = Renames[catLabel]
				if catUid in Renames:  catUid = Renames[catUid]
				
				newrow = [id, catLabel, subCatLabel, catUid, subCatUid]
				NewData.append({key:value for key, value in zip(columns, newrow)})
			db = MyLibs.SQLite.connect(file)
			MyLibs.SQLite.UpdateManyByID(table_name, NewData, db)
			db.close()
			print('OK')
		except Exception as e:
			print(e)
			input()
	
