import sqlite3
import os
import sync_rest
import subprocess
import configparser
import app_log
import logging


DB_FILE_NAME = 'last_cs.db'

if __name__ == "__main__":
    '''
        check if file exists
    '''

    app_log.setup()
    bCanBeOpened = False
    bExists = os.path.exists(DB_FILE_NAME)
    if bExists:
        try:
            fl = open(DB_FILE_NAME,'ab')
            bCanBeOpened = True
        except IOError as e:
            if bExists:
                logging.error("Error: cannot open file %s due to %s,%s" % (DB_FILE_NAME, e.errno, e.strerror))
                exit(1)
        finally:
            if (fl):
                fl.close()

    file_mode = "file:{0}?mode={1}"
    path_str = ""
    if not bExists:
        path_str = file_mode.format(DB_FILE_NAME, "rwc")
    else:
        path_str = file_mode.format(DB_FILE_NAME, "rw")

    con = None
    try:
        con = sqlite3.connect(path_str, uri=True)
        curs = con.cursor()
        logging.info("Successfully connected to SQLite with option %s " % path_str)
    except sqlite3.Error as error:
        logging.error("Error while connecting to sqlite", error)
        exit(1)

    max_cs_id = None
    if not bExists:
        try:
            curs.execute("create table last_changeset (cs_num numeric, dt timestamp default current_timestamp)")
            cmdCsList = sync_rest.CmdCsList()
            cs_list = cmdCsList.exec()
            #print(" max_id = %s , type id  %s" % (max_id,type(max_id)) )
            if len(cs_list) > 0:
                max_cs_id = cs_list[-1]
                curs.execute("insert into last_changeset (cs_num) values (?)", (max_cs_id,) )
                con.commit()
            else:
                logging.error("Error: cannot init changeset number!")
                exit(1)
        except Exception as e:
            logging.error("SQLError: %s" % str(e))
            con.close()
            exit(1)
        #'curl 192.168.4.127:3000/api/0.6/changesets? - получить список всех изменений'
        #"osmosis --read-apidb-change host="{0}" database="{1}"  user="{2}" password="{3}" intervalBegin=$DAY_AGO intervalEnd=$NOW validateSchemaVersion="no" --write-xml-change file="out.osc""
        # curs.
    else:
        try:
            query = "select cs_num,strftime('%d.%m.%Y %H:%M:%S',dt) from last_changeset"
            curs.execute(query)
            record = curs.fetchone()
            if record is None:
                logging.error("Error: no data found in \"last_changeset\" ")
                con.close()
                exit(1)

            max_cs_id = record[0]
            dt = record[1]
            logging.info("Info: found last update #%s at '%s' " % (max_cs_id,dt ))

        except Exception as e:
            logging.error("Error: %s" % str(e))
            con.close()
            exit(1)

        cmdCsList = sync_rest.CmdCsList()
        cs_list = cmdCsList.exec()
        #print(" cs_list= %s " % (cs_list) )
        new_cs = []
        if len(cs_list) > 0:
            new_cs = [id for id in cs_list if (id > max_cs_id)]
            new_cs.sort()
            #print ("new cs list is %s " % new_cs)
        else:
            logging.error("Error: cannot init changeset number!")
            exit(1)

        config = configparser.ConfigParser()
        try:
            config.read('sync_db.ini')
            start_cmd = config['OVERPASS'].get('start_svc_cmd')
            stop_cmd = config['OVERPASS'].get('stop_svc_cmd')
            upd_cmd = config['OVERPASS'].get('update_db_cmd')
        except:
            logging.error("Error: cannot get 'start_svc_cmd,stop_svc_cmd' from config")
            exit(1)

        if len(new_cs) > 0:
            #print("stopping OVERPASS dispatcher")
            p = subprocess.run(stop_cmd,shell=True,\
                                stdout=subprocess.PIPE,\
                                stderr=subprocess.STDOUT)
            out = p.stdout
            logging.info("CMD: stop_cmd: - %s" % out)
            logging.info("CMD: stop_cmd return code is \'%s\' " % p.returncode)
            last_upd_num = max_cs_id

            for cs_id in new_cs:
                #print("getting cs %s" % cs_id)
                cmdGet = sync_rest.CmdGetChangeset()
                txt = cmdGet.exec(cs_id)
                if not (txt is None):
                    #print("updating OVERPASS database")
                    p = subprocess.run("{0} {1}.osc".format(upd_cmd, cs_id),shell=True,\
                                        stdout=subprocess.PIPE,\
                                        stderr=subprocess.STDOUT)
                    out = p.stdout
                    logging.info("CMD: update - %s" % out)
                    logging.info ("CMD: update_cmd return code is \'%s\' " % p.returncode)
                    if last_upd_num == cs_id - 1 and p.returncode == 0:
                        last_upd_num = cs_id

            #print("starting OVERPASS dispatcher...")
            p = subprocess.run(start_cmd, shell=True)
            logging.info("CMD: start_cmd return code is \'%s\' " % p.returncode)

            if last_upd_num > max_cs_id:
                try:
                    logging.info("last cs is %s " % last_upd_num)
                    query = "update last_changeset set cs_num=?, dt=current_timestamp"
                    curs.execute(query, (last_upd_num,))
                    con.commit()
                except Exception as e:
                    logging.error("SQLError: %s" % str(e))
                    con.close()
                    exit(1)

    curs.close()
    con.close()

    exit(0)
