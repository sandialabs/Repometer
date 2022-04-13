#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Test_Backup:
    Test database backup and its subroutines.
"""

import unittest
import pytest
import os
import socket
import repometer.database.backup as backup


class TestBackup(unittest.TestCase):
    def testNonExistentDirectoryPath(self):
        """
        Test to ensure a failure if a nonexistent directory path is specified.

        Returns
        -------
        None.

        """
        path = '/nonsense/path/that/does/not/exist'
        with pytest.raises(backup.DBBackupException):
            backup.dir_path(path)

    def testExistentDirectoryPath(self):
        """
        Test to ensure that an existing path is returned correctly.

        Returns
        -------
        None.

        """
        path = os.getcwd()
        self.assertEqual(os.getcwd(), backup.dir_path(path))

    def testRestrictHost(self):
        """
        Test to ensure that a host restriction is properly identified.

        Returns
        -------
        None.

        """
        hostname = socket.gethostname()
        backup.restrictHost(hostname)
