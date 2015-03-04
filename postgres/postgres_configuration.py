__author__ = 'snownettle'

import psycopg2

# Try to connect

try:
    conn = psycopg2.connect("dbname='dialogue_acts' user='postgres' password='postgres'")
    print "DB exists"
except:
    print "I am unable to connect to the database."

    # cur = conn.cursor()
    # try:
    # cur.execute("""DROP DATABASE foo_test""")
    # except:
    #     print "I can't drop our test database!"