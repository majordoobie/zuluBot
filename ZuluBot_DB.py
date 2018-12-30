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

        except sqlite3.OperationalError as e:
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

    def is_Active(self, coc_tag):
        """ Check to see if user has the is_Active flag set to true meaning that they
            are part of the clan still but just not present.
        :param conn: Connection object
        :param coc_tag: User CoC Tag
        :return: True or False and kick_note
        """
        sql_query = ("SELECT * FROM users WHERE clash_tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (coc_tag,))
        row = cur.fetchall()

        if len(row) == 1:
            return row[0]
        else:
            print("Could not find the tag error.. do something here")


    def set_Active(self, str_bool, coc_tag):
        """ Change users active state to True or False. This will dictate if they are 
        currently enrolled into the clan.
        :param conn: Connection object
        :param str_bool: String boolean to change the value to
        :param coc_tag: User CoC Tag
        :return: True or False and kick_note
        """
        sql_query = ("UPDATE users SET is_Active = ? WHERE Clash_tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (str_bool, coc_tag))

        sql_query = ("SELECT * FROM users WHERE clash_tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (coc_tag,))
        row = cur.fetchall()
        
        if len(row) == 1:
            return row[0]
        else:
            print("Could not find the tag error.. do something here")

    def get_all(self, coc_tag):
        sql_query = ("SELECT * FROM users")
        self.conn.cursor().execute(sql_query)
        rows = self.conn.cursor().fetchall()
        for row in rows:
            print(row)



           

