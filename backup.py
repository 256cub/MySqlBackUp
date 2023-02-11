from __future__ import print_function

import datetime
import os
import pipes
import time
import socket
import config

from colorama import Fore

from Main.Email import Email
from Main.GoogleDrive import GoogleDrive
from Main.MySQL import MySQL

hostname = socket.gethostname()
location_folder_id = GoogleDrive().create_folder(config.GOOGLE_DRIVE_ROOT_ID, hostname)

databases = MySQL().get_databases()

total_databases = len(databases)

for cycle, database in enumerate(databases):
    database = database['Database']

    print()
    print(Fore.YELLOW + '[{} from {}]'.format(cycle + 1, total_databases), Fore.GREEN + 'Processing', Fore.MAGENTA + '{}'.format(database), Fore.BLUE + '{}'.format(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S")))

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    BACKUP_DIR_PATH = config.APP_PATH + '/BackUp/MySQL/' + database
    if not os.path.exists(BACKUP_DIR_PATH):
        os.makedirs(BACKUP_DIR_PATH)

    FILENAME = database + "_" + hostname + "_" + current_datetime + '.sql'

    backup_mysql_path = BACKUP_DIR_PATH + '/' + FILENAME
    backup_archive_path = backup_mysql_path + '.gz'

    # Code for checking if you want to take single database backup or assigned multiple backups in database.
    if os.path.exists(database):
        file1 = open(database)
        multi = 1
    else:
        multi = 0

    # Starting actual database backup process.
    if multi:
        in_file = open(database, "r")
        f_length = len(in_file.readlines())
        in_file.close()
        p = 1
        db_file = open(database, "r")

        while p <= f_length:
            db = db_file.readline()  # reading database name from file
            db = db[:-1]  # deletes extra line
            dump_cmd = "/usr/bin/mysqldump -h " + config.DB_HOST + " -u " + config.DB_USER + " -p" + config.DB_PASSWORD + " " + db + " > " + pipes.quote(backup_mysql_path)
            os.system(dump_cmd)
            gzip_cmd = "gzip " + pipes.quote(backup_mysql_path)
            os.system(gzip_cmd)
            p = p + 1
        db_file.close()
    else:
        db = database
        dump_cmd = "/usr/bin/mysqldump -h " + config.DB_HOST + " -u " + config.DB_USER + " -p" + config.DB_PASSWORD + " " + db + " > " + pipes.quote(backup_mysql_path)
        os.system(dump_cmd)
        gzip_cmd = "gzip " + pipes.quote(backup_mysql_path)
        os.system(gzip_cmd)

    database_folder_id = GoogleDrive().create_folder(location_folder_id, database)
    file = GoogleDrive().upload(backup_archive_path, database_folder_id)

    size_zip = os.path.getsize(backup_archive_path)

    email_subject = 'MySQL ' + database + ' ' + hostname + ' BackUp ' + current_date
    email_message = '<strong>MySQL ' + database + ' BackUp ' + current_date + '</strong> <hr>' + backup_archive_path + ' <br><strong>Size: <br></strong>' + str(size_zip / (1024 * 1024)) + ' Mb <br>Google Drive Link => https://drive.google.com/file/d/' + file.get('id') + '/view'                                                            ''

    Email().send_message(email_subject, email_message)

    os.remove(backup_archive_path)

    print(Fore.YELLOW + '[+]', Fore.GREEN + 'Local BackUp Archive Deleted', Fore.MAGENTA + '{}'.format(backup_archive_path), Fore.BLUE + '{}'.format(datetime.datetime.now().strftime("%Y %m %d %H:%M:%S")))

    time.sleep(1)
