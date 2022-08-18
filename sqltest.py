import pymysql.cursors
 
# Connect to the database
"""
host = '127.0.0.1'
user = 'root'
password = ''
db = 'apr01'
charset = 'utf8mb4'
"""
connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='',
                             db='apr01',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
 
try:
    with connection.cursor() as cursor:
        # Create a new record
        sql_1 = "INSERT INTO `Calendar_table` VALUES('2022-05-09', 1)"
        cursor.execute(sql_1)



        """
        sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
        cursor.execute(sql, ('webmaster@python.org', 'very-secret'))


    # connection is not autocommit by default. 
    # So you must commit to save your changes.
        """    
    connection.commit()
    """ 
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
        cursor.execute(sql, ('webmaster@python.org',))
        result = cursor.fetchone()
        print(result)
    """

except:
    print('error')

finally:
    connection.close()
