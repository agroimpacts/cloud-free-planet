
import os
import sys
import psycopg2
from psycopg2.extensions import adapt



db_sandbox_name = 'SouthAfricaSandbox'
db_user = '***REMOVED***'
db_password = '***REMOVED***'

def cleanKMLs():
    # Initialize connection to sandbox:
    
    dbcon = psycopg2.connect("dbname=%s user=%s password=%s" % (db_sandbox_name, db_user, db_password))
    cur = dbcon.cursor()

    #Get all F and N kmls from kml_data
    cur.execute("select gid, name, kml_type from kml_data where kml_type in ( 'F', 'N');")
    totalRows = cur.rowcount
    print totalRows
    f_n_kmls = cur.fetchall()
    dbcon.commit()
    f_n_names_tuple = zip(*f_n_kmls)[1]
    f_n_names = [(n,) for n in f_n_names_tuple]
    print f_n_names

    # delete dependent assignment_data rows:
    cur.execute("select h.hit_id from hit_data h inner join kml_data k using (name) where k.kml_type in ('F', 'N');")
    hitSelectRowCount =cur.rowcount
    hitIDs = cur.fetchall()
    dbcon.commit()
    
    cur.execute("select a.assignment_id from assignment_data a inner join hit_data h on a.hit_id = h.hit_id inner join kml_data k on k.name = h.name where k.kml_type in ('F','N');")
    assignmentSelectRowCount = cur.rowcount
    assignmentIDs = cur.fetchall()
    dbcon.commit()

    cur.executemany("delete from user_maps where assignment_id =%s;", assignmentIDs)
    dbcon.commit()

    cur.executemany("delete from error_data where assignment_id =%s;", assignmentIDs)
    dbcon.commit()

    cur.executemany("delete from assignment_data where hit_id=%s;", hitIDs)
    dbcon.commit()

    # delete dependent hit_data rows:
    cur.executemany("delete from hit_data where name =%s;", f_n_names)
    hitDataRowCount = cur.rowcount
    if hitDataRowCount == hitSelectRowCount:
        dbcon.commit()
    else:
        print "bad result deleting from hit_data! Too many/few rows."
        dbcon.rollback()
        cur.close()
        dbcon.close()
        return

    print "updating in master_grid"
    # update master_grid rows that match the kmls
    cur.execute("update master_grid set avail = 'T' where name in (select name from kml_data where kml_type in ('F', 'N'));")

    masterRowCount = cur.rowcount
    if masterRowCount <= totalRows:
        dbcon.commit()
        print "updating finished in master_grid"
    else:
        print "bad result updating from master_grid! Too many rows."
        dbcon.rollback()
        cur.close()
        dbcon.close()
        return
    

    #delete unnecessary kml files
    print "starting to remove files\n"
    for name in f_n_names:
        for fp in name:
            fullpath = "../kmls/" + fp.strip() + ".kml"
            if os.path.isfile(fullpath):
                print "removed kml file: " + fullpath
                os.remove(fullpath)
            else:
                print "kml named: " + fp + " had no kml file."

    # decrement master_grid_counter Block number is hardcoded.
    cur.execute("select counter from master_grid_counter where block=1;")
    masterGridCounter = cur.fetchone()[0]
    masterGridCounter-=masterRowCount
    cur.execute("update master_grid_counter set counter=%s where block=1", (masterGridCounter,))

    # Finally delete from kml_data all F and N kmls:
    cur.execute("delete from kml_data where kml_type in ('F', 'N');")
    deletedRowCount = cur.rowcount
    if deletedRowCount == totalRows:
        dbcon.commit()
    else:
        print "Bad result deleting from kml_data!"
        dbcon.rollback()
        cur.close()
        dbcon.close()
        return

     #Close db connection and cursor
    cur.close()
    dbcon.close()

if __name__ == "__main__":
    cleanKMLs()
