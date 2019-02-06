import sqlite3

class Database():

	def create_database(self, name):
		self.conn = sqlite3.connect(name+'.db')
		self.c = self.conn.cursor()

		self.c.execute("DROP TABLE IF EXISTS sensor")

		self.c.execute('''CREATE TABLE 
						  sensor(ID INT PRIMARY KEY, time_stamp TIMESTAMP, front_sensor REAL, left_sensor REAL, right_sensor REAL, 
                                                  left_up_sensor REAL, right_up_sensor REAL, speed REAL, direction REAL, forward_back INT)''')
		self.conn.commit()

	def load_database(self, name):
		self.conn = sqlite3.connect(name+'.db')
		self.c = self.conn.cursor()

	def save_to_database(self, id_value, time_stamp_value, front_value, left_value, right_value, left_up_value, right_up_value, speed_value, direction_value, forward_back_value):
		self.c.execute('''INSERT INTO sensor(ID, time_stamp, front_sensor, left_sensor, right_sensor, left_up_sensor, right_up_sensor, speed, direction, forward_back)
					  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
					  (id_value, time_stamp_value, front_value, left_value, right_value, left_up_value, right_up_value, speed_value, direction_value, forward_back_value))
		
	def read_from_database(self):
		result = self.c.execute('''SELECT * FROM 
								(SELECT ID, speed, direction FROM sensor ORDER BY ID DESC LIMIT 30) ORDER BY ID''')
		return result.fetchall()

	def commit_database(self):
		self.conn.commit()

	def close_database(self):
		self.conn.close()


