from fixed_thread_pool_executor import FixedThreadPoolExecutor

import psycopg2
import logging
import multiprocessing

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
        imagery_config = config['imagery']
        self.host = db_config['host']
        self.dbname = db_config['dbname']
        self.user = db_config['user']
        self.password = db_config['password']
        self.master_grid_table = db_config['master_grid_table']
        self.scene_data_table = db_config['scene_data_table']
        self.enabled = db_config['enabled']
        self.conn = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # planet has limitation 5 sec per key (search queries)
        threads_number = imagery_config['threads']
        if threads_number == 'default':
            threads_number = multiprocessing.cpu_count() * 2 + 1
        else:
            threads_number = int(threads_number)

        self.query_executor = FixedThreadPoolExecutor(size = threads_number)

    def connect(self):
        if self.enabled:
            self.conn = psycopg2.connect('host={} dbname={} user={} password={}'.format(self.host, self.dbname, self.user, self.password))

    def get_cursor(self):
        return self.conn.cursor()

    def query_by_extent(self, extent, limit = 10):
        curs = self.get_cursor()
        query = ""
 
        if limit == None:
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
        if self.enabled:
            try:
                curs = self.conn.cursor()
                self.insert_row(row, curs)
                self.conn.commit()
            except:
                conn.rollback()

    def insert_row(self, row, curs):
        if self.enabled:
            # [provider | scene_id | cell_id | season] | global_col | global_row | url | tms_url
            curs.execute(
                """INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""".format(self.scene_data_table), 
                (row['provider'], row['scene_id'], row['cell_id'], row['season'], row.get('global_col'), row.get('global_row'), row.get('url'), row.get('tms_url'))
            )

    def insert_rows_by_one(self, rows):
        if self.enabled:
            # [provider | scene_id | cell_id | season] | global_col | global_row | url | tms_url
            try:
                curs = self.conn.cursor()
                
                for row in rows:
                    curs.execute(
                        """INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""".format(self.scene_data_table), 
                        (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    )
                
                self.conn.commit()
            except:
                self.conn.rollback()

    def insert_rows_by_one_async(self, rows):
        if self.enabled:
            self.query_executor.submit(self.insert_rows_by_one, rows)

    def insert_rows(self, rows):
        if self.enabled:
            try:
                curs = self.conn.cursor()
                # [provider | scene_id | cell_id | season] | global_col | global_row | url | tms_url
                args_str = ','.join(curs.mogrify("%s", (row, )).decode('utf8') for row in rows)
                curs.execute("INSERT INTO {} VALUES {}".format(self.scene_data_table, args_str)) #  ON CONFLICT DO NOTHING PSQL 9.5 only
                self.conn.commit()
            except:
                self.conn.rollback()

    def drain(self):
        self.query_executor.drain()

    def close(self):
        self.query_executor.close()
