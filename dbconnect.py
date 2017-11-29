import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           password = "426480ua",
                           db = "tweetwoot")
    c = conn.cursor()

    return c, conn
		