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
                                        Clash_tag text NOT NULL,
                                        Clash_name text NOT NULL,
                                        Clash_lvl integer NOT NULL,
                                        Clash_league text,
                                        Clash_icon text,

                                        Disc_ID integer NOT NULL,
                                        Disc_joinedDate date NOT NULL,

                                        in_PlanningServer text NOT NULL,
                                        is_Active text NOT NULL,
                                        kick_Note text,
                                        PRIMARY KEY(Clash_tag)
                                    ); """
        try:
            print("Creating Users table")                                    
            self.conn.cursor().execute(sql_create_users_table)
            self.conn.commit()
            print("Success.")

        except sqlite3.OperationalError as e:
            print(f"Failed to create with {e}")
            return e

        sql_create_update_table = """ CREATE TABLE IF NOT EXISTS dailyupdate (
                                        increment_date date NOT NULL,
                                        Clash_tag text NOT NULL,
                                        Current_Donation integer NOT NULL,
                                        in_Zulu text NOT NULL,
                                        PRIMARY KEY (increment_date, Clash_tag),
                                        CONSTRAINT coc_tag_constraint FOREIGN KEY (Clash_tag) REFERENCES users(Clash_tag)    
                                    ); """
        try:  
            print("Creating DailyUpdate table")                                    
            self.conn.cursor().execute(sql_create_update_table)
            self.conn.commit()
            print("Success")
            return None
        except sqlite3.OperationalError as e:
            print(f"OperationalError: {e}")
            return e

    def insert_userdata(self, tupe):
        """ Insert user data into the users table
        :param conn: Connection object
        :param tupe: tupe of data
        :return:
        """
        sql_update = """INSERT INTO users(
                    Clash_tag,
                    Clash_name,
                    Clash_lvl,
                    Clash_league,
                    Clash_icon,
                    Disc_ID,
                    Disc_joinedDate,
                    in_PlanningServer,
                    is_Active,
                    kick_Note) 
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                        """  
        try:
            self.conn.cursor().execute(sql_update, tupe)
            self.conn.commit()
            return None

        except sqlite3.IntegrityError as e:
            print(e)
            return e
    
    def update_donations(self, tupe):
        """ Insert updated user donation data 
        :param conn: Connection object
        :param tupe: tupe of data
        :return:
        """
        
        sql_update = """INSERT INTO dailyupdate(
                    increment_date,
                    Clash_tag,
                    Current_Donation,
                    in_Zulu)
                    VALUES(?,?,?,?)
                        """ 
        try:
            #Breaks here
            self.conn.cursor().execute(sql_update, tupe)
            self.conn.commit()
            return None

        except sqlite3.IntegrityError as e:
            print(e)
            print("Error with {}".format(tupe))
            return e
        except sqlite3.OperationalError as e:
            print(e)
            print("Error with this data {}".format(tupe))
            return e

    

# tupe = ( "#TAG123", "SgtMajorDoobie", 123123123123, 10, "Crystal", "https:\\", 123123123 )
# shit1 = ("2018-11-22 03:06:33.154148","#TAG123", 151, "TRUE" )
# shit2 = ("2018-11-22 03:06:33.154147","#TAG134", 300, "TRUE" )
# shit3 = ("2018-11-22 03:06:33.154149", "#TAG123", 350, "TRUE")
# dbb = ZuluDB()
# dbb.insert_userdata(tupe)
# dbb.update_donations(shit1)
# dbb.update_donations(shit2)
# dbb.update_donations(shit3)
# dbb.update_donations(shit3)
# tupe = (datetime.datetime.utc(), "#123123", 1000, "TRUE")








           

