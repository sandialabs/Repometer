#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Test_DB_Access:
    Test database access using both real and fake config dictionaries.
"""

import pymysql
from config import *

def connectDB(config):
    """
    Connects to the database.

    Parameters
    ----------
    config : dict
        Access configuration information.

    Returns
    -------
    bool
        True  : Connected to database successfully.
        False : Failed to connect.

    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()
        if results:
            return True
        else:
            return False
    except Exception as e:
        print('ERROR: {}'.format(e))
        return False


def test_incorrectDBName():
    """
    Test to ensure we cannot connect to the DB if name is wrong.

    Returns
    -------
    None.

    """
    result = connectDB(incorrect_DBname_config)
    assert(result is False)


def test_incorrectHostName():
    """
    Test to ensure we cannot connect to the DB if the hostname is wrong.

    Returns
    -------
    None.

    """
    result = connectDB(incorrect_Hostname_config)
    assert(result is False)


def test_incorrectUser():
    """
    Test to ensure we cannot connect to the DB if the username is wrong.

    Returns
    -------
    None.

    """
    result = connectDB(incorrect_Username_config)
    assert(result is False)


def test_incorrectPwd():
    """
    Test to ensure we cannot connect to the DB if the password is wrong.

    Returns
    -------
    None.

    """
    result = connectDB(incorrect_Password_config)
    assert(result is False)


def test_ConnectToDB():
    """
    Test to ensure we can connect to the database.

    Returns
    -------
    None.

    """
    result = connectDB(correct_config)
    assert(result is True)
