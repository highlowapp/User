import pymysql
import bleach
import requests
import Helpers

services = Helpers.read_json_from_file("config/services.json")
auth_service = services["auth"]

class User:

    #Define initialization function
    def __init__(self, uid, host, username, password, database):
        self.uid = bleach.clean(uid)
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        

        ## Get the user's data from MySQL ##

        #Connect to MySQL
        conn = pymysql.connect(host, username, password, database, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        #Select the row with the user from the database
        cursor.execute("SELECT * FROM users WHERE uid='" + self.uid + "';")

        user = cursor.fetchone()

        #Commit and close the connection
        conn.commit()
        conn.close()

        #Make sure the user existed in the first place
        if user == None:
            raise ValueError("user-no-exist")

        #Otherwise, get all the data and store it
        self.firstname = user["firstname"]
        self.lastname = user["lastname"]
        self.password = user["password"]
        self.email = user["email"]
        self.profileimage = user["profileimage"]
    
    ## Setters ##

    #Any column
    def set_column(self, column, value):

        #Connect to MySQL
        conn = pymysql.connect(self.host, self.username, self.password, self.database)
        cursor = conn.cursor()

        #Clean the values
        column = bleach.clean(column)
        value = bleach.clean(value)

        #Attempt to set the column
        cursor.execute("UPDATE users SET " + column + "'" + value + "' WHERE uid='" + self.uid + "';")

        #Commit and close the connection
        conn.commit()
        conn.close()

    def set_firstname(self, value):
        self.set_column("firstname", value)

    def set_lastname(self, value):
        self.set_column("lastname", value)

    def set_email(self, value):
        self.set_column("email", value)

    def set_profileimage(self, value):
        self.set_column("profileimage", value)

    def set_password(self, value):
        print("WARNING: Setting the password can be dangerous!")
        self.set_column("password", value)

    def request_friend(self, uid):
        conn = pymysql.connect(self.host, self.username, self.password, self.database)
        cursor = conn.cursor()

        uid = bleach.clean(uid)

        cursor.execute("INSERT INTO friends(initiator, acceptor, status) VALUES(" + self.uid + ", " + uid + ", 1)")

        conn.commit()
        conn.close()

    def reject_friend(self, uid):
        conn = pymysql.connect(self.host, self.username, self.password, self.database)
        cursor = conn.cursor()

        uid = bleach.clean(uid)

        cursor.execute("UPDATE friends SET status=0 WHERE initiator=" + self.uid + " AND acceptor=" + uid + "")

        conn.commit()
        conn.close()

    def accept_friend(self, uid):
        conn = pymysql.connect(self.host, self.username, self.password, self.database)        
        cursor = conn.cursor()

        uid = bleach.clean(uid)

        cursor.execute("UPDATE friends SET status=2 WHERE initiator=" + self.uid + " AND acceptor=" + uid + "")

        conn.commit()
        conn.close()
        
    def init_test(self):
        try:
            user = User(self.uid, self.host, self.username, self.password, self.database)

            print("init_test was a success")
        except ValueError:
            print("init_test was not a success")

   
    def set_column_tests(self):
        conn = pymysql.connect(self.host, self.username, self.password, self.database, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
       
        self.set_firstname("Firstname")
        self.set_lastname("Lastname")
        self.set_email("test@example.com")
        self.set_profileimage("MyImage")
        self.set_password("test")
        
        cursor.execute(
            "SELECT * FROM " + self.database +  "WHERE firstname = 'Firstname'" 
            "AND lastname = 'Lastname'" 
            "AND email = 'test@gmail.com'" 
            "AND profileimage = 'MyImage';"
        )

        row_count = cursor.rowcount
        print("number of affected rows: {}".format(row_count))

        if row_count == 0:
            print("Setting columns was not a success")
        else:
            print("Setting columns was a success")

       
    def accept_friend_test(self):
        data = {
                
            "firstname":"Firstname2",
            "lastname":"Lastname2",
            "email":"test2@example.com",
            "password":"longpassword2",
            "confirmpassword":"longpassword2",
            "profileimage":"MyImage2"

            }
        r = requests.post("https://" + auth_service + "/sign_up", data=data)
        token = r.text
        verification = Helpers.verify_token(token)
        if "error" in verification:
            print("couldn't verify token")
            return False
        uid = verification["uid"]          

        user1 = self.uid

        user2 = uid 

        self.request_friend(user2)

        user2 = User(uid, self.host, self.username, self.password, self.database)

        user2.accept_friend(user1)

        conn = pymysql.connect(self.host, self.username, self.password, self.database)        
        cursor = conn.cursor()
            
        cursor.execute(
            "SELECT FROM friends WHERE initiator=" + user1 + 
            "AND acceptor=" + user2 + 
            "AND status=2"
            )
        row = cursor.fetchone

        if row == None:
            print("There was an error in accept_friend_test")
            return False
        else:
            print("Everything went fine in accept_friend_test")

        cursor.execute(
            "DELETE FROM friends WHERE email='test@example.com';"
            "DELETE FROM friends WHERE email='test2@example.com';"
            )   
        conn.commit()
        conn.close() 


    def reject_friend_test(self):
        data = {
                
            "firstname":"Firstname2",
            "lastname":"Lastname2",
            "email":"test2@example.com",
            "password":"longpassword2",
            "confirmpassword":"longpassword2",
            "profileimage":"MyImage2"

            }
        r = requests.post("https://" + auth_service + "/sign_up", data=data)
        token = r.text
        verification = Helpers.verify_token(token)
        if "error" in verification:
            print("couldn't verify token")
            return False
        uid = verification["uid"]          

        user1 = self.uid

        user2 = uid 

        self.request_friend(user2)

        user2 = User(uid, self.host, self.username, self.password, self.database)

        user2.reject_friend(user1)

        conn = pymysql.connect(self.host, self.username, self.password, self.database)        
        cursor = conn.cursor()
            
        cursor.execute(
            "SELECT FROM friends WHERE initiator=" + user1 + 
            "AND acceptor=" + user2 + 
            "AND status=0"
            )
        row = cursor.fetchone

        if row == None:
            print("There was an error in reject_friend_test")
            return False
        else:
            print("Everything went fine in reject_friend_test")

        cursor.execute(
            "DELETE FROM friends WHERE email='test@example.com';"
            "DELETE FROM friends WHERE email='test2@example.com';"
            )   
        conn.commit()
        conn.close()       


    def run_tests(self):
        self.init_test()
        self.set_column_tests()
        self.accept_friend_test()
        self.reject_friend_test()
