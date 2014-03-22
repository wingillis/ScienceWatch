import sqlite3

conn = sqlite3.connect('scienceWatch.db')
cursor = conn.cursor()

tableCode = '''create table users
			(ID integer IDENTITY(1,1) PRIMARY KEY,
				username text,
				password text
				)'''

cursor.execute(tableCode)

conn.commit()

cursor.close()