import sqlite3
import datetime

class ZuluDB():
    def __init__(self):
        try:
            self.conn = sqlite3.connect("zuluDB.db")
            self.conn.cursor().execute("PRAGMA foreign_keys = 1")  
        except IOError as e:
            print(e)

        self.initiate_db()

    def initiate_db(self):
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        CoC_tag text NOT NULL,
                                        CoC_name text NOT NULL,
                                        Disc_ID integer NOT NULL,
                                        CoC_thLvl integer NOT NULL,
                                        CoC_league text,
                                        CoC_icon text,
                                        joined_date integer NOT NULL,
                                        PRIMARY KEY(CoC_tag)
                                    ); """
        try:                                    
            self.conn.cursor().execute(sql_create_users_table)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)
        
        sql_create_update_table = """CREATE TABLE IF NOT EXISTS dailyupdate (
                                        date REAL NOT NULL,
                                        CoC_tag text NOT NULL,
                                        Current_Donation integer NOT NULL,
                                        isPresent text NOT NULL,
                                        PRIMARY KEY (date, CoC_tag),
                                        CONSTRAINT coc_tag_constraint FOREIGN KEY (CoC_tag) REFERENCES users(CoC_tag)    
                                    );"""
        try:                                    
            self.conn.cursor().execute(sql_create_update_table)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(e)

    def insert_userdata(self, tupe):
        """ Insert user data into the users table
        :param conn: Connection object
        :param tupe: tupe of data
        :return:
        """
        sql_update = """INSERT INTO users(
                    CoC_tag,
                    CoC_name,
                    Disc_ID,
                    CoC_thLvl,
                    CoC_league,
                    CoC_icon,
                    joined_date)
                    VALUES(?,?,?,?,?,?,?)
                        """  
        try:
            self.conn.cursor().execute(sql_update, tupe)
            self.conn.commit()

        except sqlite3.IntegrityError as e:
            print(e)
    
    def update_donations(self, tupe):
        """ Insert updated user donation data 
        :param conn: Connection object
        :param tupe: tupe of data
        :return:
        """
        sql_update = """INSERT INTO dailyupdate(
                    date,
                    CoC_Tag,
                    Current_Donation,
                    isPresent)
                    VALUES(?,?,?,?)
                        """ 
        try:
            self.conn.cursor().execute(sql_update, tupe)
            self.conn.commit()

        except sqlite3.IntegrityError as e:
            print(e)
            print("Error with {}".format(tupe))
        except sqlite3.OperationalError as e:
            print(e)
            print("Error with {}".format(tupe))

    

# tupe = ( "#TAG123", "SgtMajorDoobie", 123123123123, 10, "Crystal", "https:\\", 123123123 )
# shit1 = ("2018-11-22 03:06:33.154148","#TAG123", 151, "TRUE" )
# shit2 = ("2018-11-22 03:06:33.154147","#TAG134", 300, "TRUE" )
shit3 = ("2018-11-22 03:06:33.154149", "#TAG123", 350, "TRUE")
dbb = ZuluDB()
# dbb.insert_userdata(tupe)
# dbb.update_donations(shit1)
# dbb.update_donations(shit2)
# dbb.update_donations(shit3)
dbb.update_donations(shit3)








           

