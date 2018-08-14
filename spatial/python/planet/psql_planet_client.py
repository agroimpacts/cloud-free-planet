import psycopg2

class PSQLPClient():
    def __init__(self, config):
        db_config = config['database']
        self.host = db_config['host']
        self.dbname = db_config['dbname']
        self.user = db_config['user']
        self.password = db_config['password']
        self.master_grid_table = db_config['master_grid_table']
        self.scene_data_table = db_config['scene_data_table']
        self.conn = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def connect(self):
        self.conn = psycopg2.connect('host={} dbname={} user={} password={}'.format(self.host, self.dbname, self.user, self.password))

    def get_cursor(self):
        return self.conn.cursor()

    def query_by_extent(self, extent, limit = 10):
        curs = self.get_cursor()
        query = ""
 
        if limit = None:
            query = """SELECT * FROM %s
                WHERE x >= %s AND x <= %s AND y >= %s AND y <= %s
                ORDER BY gid""" % (self.master_grid_table, extent['xmin'], extent['xmax'], extent['ymin'], extent['ymax'])
         else: 
             query = """SELECT * FROM %s
                WHERE x >= %s AND x <= %s AND y >= %s AND y <= %s
                ORDER BY gid LIMIT %s""" % (self.master_grid_table, extent['xmin'], extent['xmax'], extent['ymin'], extent['ymax'], limit)

        curs.execute(query)
    
        return curs

    def insert_row_with_commit(self, row):
        try:
            curs = conn.cursor()
            self.insert_row(row, curs)
            conn.commit()
        except:     
            conn.rollback()

     def insert_row(self, row, curs):
         curs.execute("""INSERT INTO {} VALUES (%s, %s, %s, %s)""".format(self.scene_data_table), (row[0], row[1], row[2], row[3]))
