#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Test_DB_Routines:
    Test all database routines using a fake database.
"""

import unittest
import testing.mysqld as sqltest
from datetime import date

import repometer.database.database as db
import repometer.core.entities as entities


######
# Generate the class, which creates the shared generated database
# Speeds up testing - reduces the number of invocations of initdb
######
tempDB = sqltest.MysqldFactory(cache_initialized_db=True)


######
# Clears the DB at the end of the tests
######
def tearDownModule(self):
    tempDB.clear_cache()


class test_TrafficDBAPI_Class(unittest.TestCase):
    """
    Test all public TrafficDBAPI Class routines

    Returns
    -------
    None.

    """
    @classmethod
    def setUpClass(cls):
        cls.mysql = tempDB()
        cls.config = cls.mysql.dsn()
        cls.DB = db.TrafficDBAPI(cls.config)

    @classmethod
    def tearDownClass(cls):
        cls.mysql.stop()

    def setUp(self):
        self.mysql.start()

    def test_A_createTables(self):
        self.DB.execute(
            "CREATE TABLE Customer_Data \
            (customer VARCHAR(40))")
        self.DB.execute(
            "CREATE TABLE Account_Data \
            (customer VARCHAR(40), url VARCHAR(90), username VARCHAR(40), \
             token VARCHAR(60))")
        self.DB.execute(
            "CREATE TABLE Repository_Data (url VARCHAR(90),\
            username VARCHAR(40), owner VARCHAR(40), repository VARCHAR(40))")
        self.DB.execute(
            "CREATE TABLE Traffic_Data (url VARCHAR(90), username VARCHAR(40),\
            owner VARCHAR(40), repository VARCHAR(40), timestamp DATE, \
            tag VARCHAR(20), value VARCHAR(20))")
        self.DB.commit()
        tables = self.DB.query("SHOW TABLES")
        self.assertEqual(
            tables, (('Account_Data',),
                     ('Customer_Data',),
                     ('Repository_Data',),
                     ('Traffic_Data',)))

    def test_B_checkColumns(self):
        columns = self.DB.columns('Customer_Data')
        self.assertEqual(columns, ['customer'])

    def test_C_customerExists(self):
        customerName = "customerName"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        result = self.DB.customerExists(customerEntity)
        self.assertFalse(result)

    def test_D_addCustomer(self):
        customerName = "customerName"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        self.DB.addCustomer(customerEntity)
        customerName = "customerName1"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        self.DB.addCustomer(customerEntity)

    def test_D_addAccount(self):
        customerName = "customerName"
        username = "accountName"
        url = "github.com"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        tokenValue = "ff34885a8624460a855540c6592698d2f1812843"
        tokenEntity = entities.EntityFactory.makeAccessTokenEntity(
            tokenValue=tokenValue)
        self.DB.addAccount(customerEntity, accountEntity, tokenEntity)
        customerName = "customerName"
        username = "accountName1"
        url = "github.com"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        tokenValue = "ff34885a8624460a855540c6592698d2f1812843"
        tokenEntity = entities.EntityFactory.makeAccessTokenEntity(
            tokenValue=tokenValue)
        self.DB.addAccount(customerEntity, accountEntity, tokenEntity)

    def test_E_removeCustomer(self):
        customerName = "customerName1"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        self.DB.removeCustomer(customerEntity)

    def test_E_removeAccount(self):
        customerName = "customerName"
        username = "accountName1"
        url = "github.com"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        self.DB.removeAccount(customerEntity, accountEntity)

    def test_F_getToken(self):
        customerName = "customerName"
        username = "accountName"
        url = "github.com"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        token = self.DB.getToken(customerEntity, accountEntity)
        self.assertEqual(token.getTokenValue(),
                         "ff34885a8624460a855540c6592698d2f1812843")

    def test_G_replaceToken(self):
        customerName = "customerName"
        username = "accountName"
        url = "github.com"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        newTokenEntity = entities.EntityFactory.makeAccessTokenEntity(
            'c00lpwdNEW')
        self.DB.replaceToken(customerEntity, accountEntity, newTokenEntity)

    def test_H_getAllCustomers(self):
        customers = self.DB.getAllCustomers()
        customer = customers[0]
        customer = customer.getCustomerName()
        self.assertEqual(customer, 'customerName')

    def test_H_getCustomerAccounts(self):
        customerName = "customerName"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        customerAccounts = self.DB.getCustomerAccounts(customerEntity)
        self.assertEqual(len(customerAccounts), 1)

    def test_H_getAllAccounts(self):
        accounts = self.DB.getAllAccounts()
        account = accounts[0]
        username = account.getUsername()
        self.assertEqual(username, 'accountName')

    def test_I_repoExists(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_repo', url)
        result = self.DB.repoExists(accountEntity, repoEntity)
        self.assertFalse(result)

    def test_J_addRepo(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity1 = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_repo', url)
        repoEntity2 = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_other_repo', url)
        self.DB.addRepository(accountEntity, repoEntity1)
        self.DB.addRepository(accountEntity, repoEntity2)

    def test_K_removeRepo(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_other_repo', url)
        self.DB.removeRepository(accountEntity, repoEntity)

    def test_L_getAccountRepos(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repos = self.DB.getAccountRepositories(accountEntity)
        repo = repos[0]
        self.assertEqual(repo.getRepositoryName(), 'my_repo')

    def test_M_insertObs(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_repo', url)
        observationEntityList = [
            entities.EntityFactory.makeObservationEntity(
                'forks', date.today(), '25')]
        self.DB.insertObservations(accountEntity, repoEntity,
                                   observationEntityList)

    def test_N_updateObs(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_repo', url)
        observationEntityList = [
            entities.EntityFactory.makeObservationEntity(
                'forks', date.today(), '26')]
        self.DB.insertObservations(accountEntity, repoEntity,
                                   observationEntityList)

    def test_O_getObs(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_repo', url)
        obs = self.DB.getObservations(accountEntity, repoEntity)
        self.assertEqual(len(obs), 1)
        for ob in obs:
            self.assertEqual(ob.getTag(), 'forks')
            self.assertEqual(ob.getValue(), '26')
            self.assertEqual(ob.getTimestamp(), date.today())

    def test_P_removeObs(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_repo', url)
        observationEntity = entities.EntityFactory.makeObservationEntity(
            'forks', date.today(), '26')
        self.DB.removeObservation(accountEntity, repoEntity,
                                  observationEntity)

    def test_Q_accountRepoAssociation(self):
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        repoEntity = entities.EntityFactory.makeRepositoryEntity(
            'owner', 'my_repo', url)
        result = self.DB.accountRepositoryAssociated(accountEntity, repoEntity)
        self.assertTrue(result)

    def test_Q_customerAccountAssociation(self):
        customerName = "customerName"
        customerEntity = entities.EntityFactory.makeCustomerEntity(
            customerName=customerName)
        username = "accountName"
        url = "github.com"
        accountEntity = entities.EntityFactory.makeVCSAccountEntity(
            username=username, domainURL=url)
        result = self.DB.customerAccountAssociated(customerEntity,
                                                   accountEntity)
        self.assertTrue(result)
