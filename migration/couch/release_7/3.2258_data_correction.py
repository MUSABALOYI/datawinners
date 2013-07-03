import logging
import traceback
import sys
import requests

from datawinners.project.models import Project
from mangrove.datastore.database import DatabaseManager
from migration.couch.utils import DWThreadPool, init_migrations, mark_start_of_migration, should_not_skip

NUMBER_OF_THREADS = 12

init_migrations('/var/log/datawinners/3.2258_data_correction_7_0_3.csv')
logging.basicConfig(filename='/var/log/datawinners/3.2258_data_correction_7_0_3.log', level=logging.DEBUG,
                    format="%(asctime)s;%(levelname)s;%(message)s")


def all_db_names():
    all_dbs = requests.get("http://localhost:5984/_all_dbs", auth=('admin', 'admin'))
    return filter(lambda x: x.startswith('hni_'), all_dbs.json())


def is_void(d, ds):
    rows = d.view("entity_by_short_code/entity_by_short_code", key=[["reporter"], ds], include_docs=True)
    return rows.rows[0]["doc"]["void"]


def get_all_active_data_senders(dbm):
    return [row.key[1] for row in
            dbm.view.by_short_codes(reduce=False, start_key=[["reporter"]], end_key=[["reporter"], {}])]


def fix_db(db_name):
    dbm = DatabaseManager(('admin', 'admin'), "http://localhost:5984/", db_name)
    d = dbm.database
    logging.info("starting data fix for " + db_name)
    all_data_senders = set(get_all_active_data_senders(dbm))
    for project_doc in d.view("project_names/project_names", include_docs=True):
        try:
            invalid_ds = []
            project_data_senders = set(project_doc["doc"]["data_senders"])

            invalid_ds = project_data_senders.difference(all_data_senders)

            project_doc = Project._wrap_row(project_doc)
            for ds in invalid_ds:
                logging.info("Found invalid data senders in project : " + str(project_doc) + " " + str(invalid_ds))
                project_doc.delete_datasender(dbm, ds)

        except Exception as e:
            print "Error : " + db_name + " : " + str(project_doc) + e.message
            traceback.print_exc(file=sys.stdout)
    logging.info("done:" + db_name)
    mark_start_of_migration(db_name)


def run():
    pool = DWThreadPool(NUMBER_OF_THREADS, NUMBER_OF_THREADS)
    for db_name in all_db_names():
        if should_not_skip(db_name):
            pool.submit(fix_db, db_name)

    pool.wait_for_completion()
    print "Completed!"


run()