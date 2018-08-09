# One-time run script
# load modules
import os
import psycopg2
import random
from datetime import datetime as DT
from MappingCommon import MappingCommon


def main():
    # Hardcoded
    n_f = 100
    pro_hd = 0.5
    pro_hd1 = 0.5

    # Connect to the database
    mapc = MappingCommon()
    log_file_path = mapc.projectRoot + "/log"

    rlog_hdr = "Log of initial f sites start, ids written & times" + \
               os.linesep
    pstart_string = "initial_f_sites: Starting up at " + \
                    str(DT.now()) + os.linesep

    logfname = log_file_path + "/generateSites.log"  # log file name
    k = open(logfname, "a+")
    k.write(rlog_hdr)
    k.write(pstart_string)
    k.close()

    log_hdr = "Error messages from initial_f_sites" + \
              os.linesep

    dberrfname = log_file_path + "/sites_dbase_error.log"
    k = open(dberrfname, "a+")
    k.write(log_hdr)
    k.close()

    # Randomly get n_f F sites of Ghana from f sites pool as initial F sites
    mapc.cur.execute("select setseed(0.5); select name from master_grid where avail = 'F' ORDER BY RANDOM() limit {}".format(n_f))
    names_f = mapc.cur.fetchall()

    # Split all into holdout, validate and train.
    random.seed(10)
    names_f_hd = random.sample(names_f, int(n_f * pro_hd))
    random.seed(11)
    names_f_hd1 = random.sample(names_f_hd, int(n_f * pro_hd * pro_hd1))
    names_f_hd2 = [item for item in names_f_hd if item not in names_f_hd1]

    # Write them into incoming_names table
    try:
        for name in names_f:
            if name in names_f_hd2:
                name_one = name + (0, 0, "validate")
            elif name in names_f_hd1:
                name_one = name + (0, 0, "holdout")
            else:
                name_one = name + (0, 0, "train")
            insert_query = "insert into incoming_names (name, run, iteration, usage) values (%s, %s, %s, %s);"
            mapc.cur.execute(insert_query, name_one)
            mapc.dbcon.commit()
        end_time = str(DT.now())
        names = ', '.join("'{}'".format(row[0]) for row in names_f)
        k = open(logfname, "a+")
        k.write(names + os.linesep)
        k.write("initial_f_sites: Script stopping up at " + end_time + os.linesep)
        k.close()
        return True

    except psycopg2.DatabaseError, err:
        print "Error updating database in initial_f_sites, rollback"
        mapc.cur.execute("ROLLBACK")  # In order to recover the database
        mapc.dbcon.commit()
        error = "initial_f_sites: " + str(DT.now()) + " " + str(err)
        k = open(dberrfname, "a+")
        k.write(error + os.linesep)
        k.close()
        mapc.createAlertIssue("initial_f_sites database error",
                              "Alert: Check the connection and query of database for initialing f sites." +
                              os.linesep + str(err))
        return False
        sys.exit(1)
    finally:
        if mapc.dbcon.closed == 0:
            mapc.close()


if __name__ == "__main__":
    main()
