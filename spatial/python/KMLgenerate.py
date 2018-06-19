# load modules
import time
import pickle
import psycopg2
import getpass
import sys
import os
from datetime import datetime as DT
import pandas as pd
import numpy as np

# save the user and password for database
'''
pgupw = {"user": "***REMOVED***", "password": "***REMOVED***"}
f = open("pgupw.data", 'wb')
pickle.dump(pgupw, f)
f.close()
'''


# Essential functions
# Function of getting database name
def getDBName(db_sandbox_name="AfricaSandbox", db_product_name="Africa",
              db_tester_name=None, alt_root=None):
    euser = getpass.getuser()
    uname = None
    sandbox = False
    if euser == "sandbox":
        sandbox = True
        uname = "sandbox"
    elif euser == "mapper":
        sandbox = False
        uname = "mapper"
    elif db_tester_name is not None:
        if euser == db_tester_name:
            sandbox = True
            uname = "sandbox"
    else:
        sys.exit("Any script must run under sandbox or mapper user!")

    # project root path
    if alt_root is not None:
        project_root = alt_root
    else:
        project_root = "/home/" + uname + "/afmap"

    # DB Names
    if sandbox:
        db_name = db_sandbox_name
    else:
        db_name = db_product_name

    return {"db_name": db_name, "project_root": project_root}


# Function of connecting database
def mapper_connect(user, password, host=None, db_tester_name=None, alt_root=None):
    # Pull working environment
    dinfo = getDBName(db_tester_name=db_tester_name, alt_root=alt_root)

    # Paths and connections
    con = psycopg2.connect(host=host, database=dinfo["db_name"], user=user, password=password)

    return {"con": con, "dinfo": dinfo}


# Function of generating regular KMLs
def RegKML_gen(fname=None, kml_type=None, alt_root=None,
               host=None, db_tester_name=None, pgupw=None):
    fname = fname
    kml_type = kml_type
    alt_root = alt_root
    host = host
    db_tester_name = db_tester_name
    pgupw = pgupw

    # Connect to the database
    coninfo = mapper_connect(user=pgupw["user"], password=pgupw["password"],
                             db_tester_name=db_tester_name,
                             alt_root=alt_root, host=host)

    # File paths
    log_file_path = coninfo["dinfo"]["project_root"] + "/log/"

    # Record daemon start time
    pstart_string = pd.DataFrame(["KMLgenerate: Daemon starting up at " + str(DT.now())])

    # Initialize csv to log database error message
    log_hdr = pd.DataFrame(["Error messages from KMLgenerate.py", "Time errcode errmessage",
                            "#####################################################"])

    # Possible conflict
    dberrfname = log_file_path + "KMLgenerate_dbase_error.log"
    if not os.path.isfile(dberrfname):
        log_hdr.to_csv(dberrfname, index=False, index_label=False, header=False)

    np.set_printoptions(precision=4)  # Display milliseconds for time stamps

    # Initialize Rlog file to record daemon start time, which kml ids written & when
    rlog_hdr = pd.DataFrame(["Log of KMLgenerate.py start, KML ids written & times",
                             "#####################################################"])
    logfname = log_file_path + fname + ".log"  # log file name
    if not os.path.isfile(logfname):
        rlog_hdr.to_csv(logfname, index=False, index_label=False, header=False)

    # Write out daemon start stamp
    pstart_string.to_csv(logfname, mode="a", index=False, index_label=False, header=False)

    while True:
        curs = coninfo["con"].cursor()

        # Query polling interval
        curs.execute("select value from configuration where key = 'KMLPollingInterval';")
        kml_polling_interval = int(curs.fetchone()[0])

        # Target batch size: should be at least 500
        curs.execute("select value from configuration where key = 'NKMLBatchSize';")
        kml_batch_size = int(curs.fetchone()[0])

        # how many unmapped kmls should there be, at a minimum
        curs.execute("select value from configuration where key = 'MinAvailNKMLTarget';")
        min_avail_kml = int(curs.fetchone()[0])

        # how many unmapped kmls are there?
        curs.execute(
            "select count(*) from kml_data k where not exists (select true from hit_data h where h.name = k.name "
            "and delete_time is null) and kml_type = 'N' and mapped_count = 0")
        avail_kml_count = int(curs.fetchone()[0])

        # Get the anchor of loading data
        curs.execute("select value from system_data where key = 'firstAvailLine';")
        first_avail_line = int(curs.fetchone()[0])

        # Select new grid cells for conversion to kmls if N unmapped < min_avail_kml
        if avail_kml_count < min_avail_kml:

            start_time = str(DT.now())

            # Step 1. Poll the database to see which grid IDs are still available
            curs.execute("select id, name from master_grid where avail = 'T' and gid >= " +
                         str(first_avail_line) + " and gid <= " +
                         str(first_avail_line + kml_batch_size - 1))
            xy_tabs = curs.fetchall()

            try:
                # Step 2. Update database tables
                # Update kml_data to show new names added and their kml_type
                # Update master to show grid is no longer available for selecting/writing
                for row in xy_tabs:
                    xy_tab = row + (kml_type, 0)
                    insert_query = "insert into kml_data (gid, name, kml_type, mapped_count) values (%s, %s, %s, %s);"
                    curs.execute(insert_query, xy_tab)
                    curs.execute("update master_grid set avail='F' where name = '%s'" % row[1])
                coninfo["con"].commit()

                # Update the first_avail_line in configuration
                new_line = first_avail_line + kml_batch_size
                curs.execute("update system_data set value='%s' where key='firstAvailLine'" % new_line)
                coninfo["con"].commit()

            except psycopg2.DatabaseError, err:
                print "Error updating database"
                error = str(DT.now()) + " " + str(err)
                file(dberrfname, "a").write(error + os.linesep)
                sys.exit(1)
            finally:
                if coninfo["con"]:
                    coninfo["con"].close()

            end_time = str(DT.now())

            # Write out kmlID log
            file(logfname, "a").write(start_time + os.linesep)
            names = pd.DataFrame(xy_tabs, columns=["id", "name"])["name"]
            names = zip(*[iter(names)] * 8)
            for i, row in enumerate(names):
                file(logfname, "a").write(str(row) + os.linesep)
            file(logfname, "a").write(end_time + os.linesep)

        time.sleep(kml_polling_interval)


# Function of listening to cvml and generating KMLs
def cvmlKML_gen(fname=None, kml_type=None, alt_root=None,
                host=None, db_tester_name=None, pgupw=None):
    pass


# Main function
def main(fname=None, kml_type=None, alt_root=None,
         host=None, db_tester_name=None, pgupw=None):
    if True:
        RegKML_gen(fname, kml_type, alt_root,
                   host, db_tester_name, pgupw)
    else:
        cvmlKML_gen(fname, kml_type, alt_root,
                    host, db_tester_name, pgupw)


if __name__ == "__main__":
    # Hardcoded
    file_name = "KMLgenerate"  # KMLgenerate
    ktype = "N"  # Type of KML (N for non-QAQC)
    alter_root = None
    db_host = None
    db_user_name = "lsong"
    f = open("pgupw.data", "rb")  # Read user name and password for DB
    pg_pw = pickle.load(f)
    f.close()

    main(fname=file_name, kml_type=ktype, alt_root=alter_root,
         host=db_host, db_tester_name=db_user_name, pgupw=pg_pw)
