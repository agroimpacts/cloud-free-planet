import psycopg2

# scenes_data
# PK [provider | scene_id | cell_id | season] | global_col | global_row | url | tms_url
# 
# CREATE TABLE scenes_data (
#   provider VARCHAR(24) NOT NULL,
#   scene_id VARCHAR(128) NOT NULL,
#   cell_id INTEGER NOT NULL,
#   season VARCHAR(2) NOT NULL,
#   global_col INTEGER NULL,
#   global_row INTEGER NULL,
#   url VARCHAR(255) NULL,
#   tms_url VARCHAR(255) NULL,
#   PRIMARY KEY(provider, scene_id, cell_id, season)
# );

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
         # [provider | scene_id | cell_id | season] | global_col | global_row | url | tms_url
         curs.execute(
             """INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""".format(self.scene_data_table), 
             (row['provider'], row['scene_id'], row['cell_id'], row['season'], row.get('global_col'), row.get('global_row'), row.get('url'), row.get('tms_url'))
         )
