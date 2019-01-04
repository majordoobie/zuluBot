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
                                        trophies integer NOT NULL,
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
                    Disc_ID,
                    Disc_joinedDate,
                    in_PlanningServer,
                    is_Active,
                    kick_Note) 
                    VALUES(?,?,?,?,?,?,?,?,?)
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
                    in_Zulu,
                    trophies)
                    VALUES(?,?,?,?,?)
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

    def set_inPlanning(self, str_bool, coc_tag):
        sql_query = ("UPDATE users SET in_PlanningServer = ? WHERE Clash_tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (str_bool, coc_tag,))
        sql_query = ("SELECT * FROM users WHERE clash_tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (coc_tag,))
        row = cur.fetchall()
        return row
        

    def update_users(self, clash_tag, clash_lvl, clash_league):
        sql_query = ("UPDATE users SET Clash_lvl = ?, Clash_league = ? WHERE Clash_tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (clash_lvl, clash_league, clash_tag,))
        row = cur.fetchall()
        return row

    def get_allUsers(self):
        """ Get all rows from users table
        :param conn: Connection object
        :return: All rows in users
        """
        sql_query = ("SELECT * FROM users")
        cur = self.conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        return rows

    def get_allDonations(self, coc_tag, sunday):
        """ Get all rows from dailydonations table
        :param conn: Connection object
        :return: All rows in users
        """
        # sql_query = ("SELECT * FROM dailyupdate WHERE clash_tag = ? ")
        # cur = self.conn.cursor()
        # cur.execute(sql_query, (coc_tag,))
        # rows = cur.fetchall()

        sql_query = ("SELECT * FROM dailyupdate WHERE clash_tag = ? AND increment_date BETWEEN ? AND ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (coc_tag, sunday, datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        rows = cur.fetchall()
        return rows

        

