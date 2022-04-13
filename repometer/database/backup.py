#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Backup:
    Script to backup and zip a database for portability.
    
    Location to save backup can be specified.
    
    Can restrict host on which backup can be run.
"""

import os
import time
import socket
import argparse
import subprocess

class DBBackupException(Exception):
    """Catch all exceptions for DB backup errors."""
    pass


try:
    from repometer.database.backup_config import config
except ModuleNotFoundError:
    raise DBBackupException("""
    🛑 ERROR 🛑: Configuration file is required.
        `repometer/database/backup_config.py` with a dictionary called `config`""")

def dir_path(path):
    """
    Check if a specified path is valid.

    Parameters
    ----------
    path : string
        The path to check.

    Raises
    ------
    DBBackupException
        Raises an exception if the path is not valid.

    Returns
    -------
    path : string
        Returns path if path is valid.

    """

    if os.path.isdir(path):
        return path
    else:
        raise DBBackupException('%s is not a valid path.' % path)

def buildParser():
    """
    The backup routine parser.

    Values
    -------
    directory        : Directory in which the backup should be stored. 
                       Defaults to current directory.
    hostname         : Hostname of the machine on which the backup is allowed to run.
                       Default: None.
    delete           : Delete backups from previous two years in specified directory.
                       Default: False.

    """
    parser = argparse.ArgumentParser(description='Backup a database into a portable format.')
    parser.add_argument('-d', '--directory',
                        type=dir_path,
                        action='store',
                        default=os.getcwd(),
                        dest='path',
                        help='Specify the directory in which to save the backup. Default: Current directory.')
    parser.add_argument('-n', '--hostname',  
                        action='store',
                        default=None,
                        dest='hostname',
                        help='Restrict ability to run to a certain hostname. Default: None.')
    parser.add_argument('--delete',
                        action='store_true',
                        default=False,
                        dest='delete',
                        help="Delete previous backups from last two years (if they exist) from specified directory.")
    
    return parser

def restrictHost(hostname):
    """
    Check current host against the specified restriction.

    Parameters
    ----------
    hostname : string
        Host on which backup is allowed to run.

    Raises
    ------
    DBBackupException
        Raises exception if current host and specified host are not the same.

    Returns
    -------
    None.

    """
    currentHost = socket.gethostname()
    if hostname != currentHost:
        raise DBBackupException('Current host %s is not the same as specified host %s.' % (currentHost, hostname))

def main():
    """
    Main function to create portable database backup.

    Raises
    ------
    DBBackupException
        Raises appropriate error(s) if the backup fails. 

    """
    parser = buildParser()
    arguments = parser.parse_args()
    path = arguments.path
    host = arguments.hostname
    delete = arguments.delete
    if host == None:
        host = socket.gethostname()
    restrictHost(host)
    date = time.strftime('%Y%m%d')
    today_path = path + '/' + date
    
    if delete is True:
        currentYear = time.strftime('%Y')
        lastYear = str(int(currentYear) - 1)
        deleteCurrent = path + '/' + currentYear + '* '
        deleteLast = path + '/' + lastYear + '* '
        os.system('rm -rf ' + deleteCurrent + deleteLast)
        
    try:
        os.stat(today_path)
    except:
        os.mkdir(today_path)

    try:
        backupcmd = "/usr/bin/mysqldump --host=" + config['host'] + " --user=" + config['user'] + " --password=" + config['password'] + " --databases " + config['database'] + " > " + today_path + "/" + config['database'] + ".sql"
        backup = subprocess.Popen(backupcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        backup.stdout.close() 
        output = str(backup.stderr.read())
        if 'error' in output:
            os.system('rm -rf ' + today_path)
            raise DBBackupException('FAILURE: There was an error in the mysqldump command:\n %s' % output)
        gzipcmd = "/usr/bin/gzip " + today_path + "/" + config['database'] + ".sql"
        os.system(gzipcmd)
 
        print("SUCCESS: Database was backed up to %s." % today_path)
    except Exception as exception:
        raise DBBackupException("FAILURE: Database backup failed - ({exceptionType}): {message}.".format(
                    exceptionType=type(exception),
                    message=exception)) from exception
    

if __name__ == "__main__":
    main()
