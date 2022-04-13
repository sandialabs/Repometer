#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Database:
    Supplies the generic Database class for standard connections and actions.

    Also supplies the specific sub-class for Repometer actions that
    are frequently utilized by the interactor.

"""


import pymysql
import repometer.core.entities as entities


class DBAPIException(Exception):
    """Catch all exceptions for DB errors."""
    pass


try:
    from repometer.database.config import config as db_config
except ModuleNotFoundError:
    raise DBAPIException("""
    🛑 ERROR 🛑: Configuration file is required.
        `repometer/database/config.py` with a dictionary called `config`""")


class DatabaseAPIFactory:
    """
    This class contains methods to churn out instances the database API.
    Interactors should construct API instances via this factory.
    """

    @staticmethod
    def createDefaultDBAPI():
        return DatabaseAPIFactory.createTrafficDBAPI()

    @staticmethod
    def createTrafficDBAPI():
        return TrafficDBAPI(db_config)


class Database:
    """
    Supplies general database connection and actions.

    """

    def __init__(self, config):
        """
        Instantiate the database connection

        Parameters
        ----------
        config : dict
            Access information to connect to database.

        Raises
        ------
        DBAPIException
            Raises exception should a database connect occur.

        Returns
        -------
        None.

        """
        self._config = config
        try:
            self._conn = pymysql.connect(**self._config)
            self._cursor = self._conn.cursor()
        except Exception as exception:       # errno, sqlstate, msg values
            raise DBAPIException(
                "Database connection failed \
                    ({exceptionType}): {message}.".format(
                    exceptionType=type(exception),
                    message=exception)) from exception

# OVERRIDDEN
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

# FINAL
    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


class TrafficDBAPI(Database):
    """
    Specific Database instance with Traffic-interactor actions
    """

    def __init__(self, config):
        """
        Initiate the Database

        Parameters
        ----------
        config : dict
            Access information to connect to database.

        Values
        ------
        self._customer_data  : DB Table name for customer information
        self._account_data   : DB Table name for account information
        self._repo_data      : DB Table name for repository information
        self._data_table     : DB Table name for traffic data
        self._customer       : Customer's name
        self._url            : URL for VCS server
        self._username       : VCS username for account (with push access)
        self._token          : VCS OAuth token
        self._owner          : Owning organization or Github account
        self._repo           : Name of repository
        self._time           : Timestamp that data was collected
        self._tag            : Name of data collected (e.g., forks, stars)
        self._value          : Value for tag received from Github

        Returns
        -------
        None.

        """
        super().__init__(config)
        self._customer_data  = 'Customer_Data'
        self._account_data   = 'Account_Data'
        self._repo_data      = 'Repository_Data'
        self._data_table     = 'Traffic_Data'
        self._customer       = 'customer'
        self._url            = 'url'
        self._username       = 'username'
        self._token          = 'token'
        self._owner          = 'owner'
        self._repo           = 'repository'
        self._time           = 'timestamp'
        self._tag            = 'tag'
        self._value          = 'value'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    def columns(self, table):
        self.cursor.execute("SHOW columns FROM %s" % table)
        names = [column[0] for column in self.cursor.fetchall()]
        return names

### Querying Customer Entries
    def customerExists(self, customerEntity):
        """
        Check if a customer exists in the table

        Returns
        -------
        bool
            True : Yes, customer exists

        """
        customer = customerEntity.getCustomerName()
        sql = "SELECT * FROM {} WHERE {}='{}'".format(
            self._customer_data, self._customer, customer)
        result = super().query(sql)
        if not result:
            return False
        else:
            return True

    def getAllCustomers(self):
        """
        Get list of customers in DB

        Returns
        -------
        allCustomers : CustomerEntity
            List of customers

        """
        query = "SELECT {} FROM {}".format(self._customer, self._customer_data)
        customers = super().query(query)
        allCustomers = []
        for customer in customers:
            customer = list(customer)
            allCustomers.append(entities.EntityFactory.makeCustomerEntity(
                customerName=customer[0]))
        return allCustomers

### Querying Account Entries
    def accountExists(self, vcsEntity):
        """
        Check if an account exists in the table

        Returns
        -------
        bool
            True : Yes, account exists

        """
        username = vcsEntity.getUsername()
        url = vcsEntity.getDomainURL()
        sql = "SELECT * FROM {} WHERE {}='{}' AND {}='{}'".format(
            self._account_data, self._username,
            username, self._url, url)
        result = super().query(sql)
        if not result:
            return False
        else:
            return True

    def getAllAccounts(self):
        """
        Get the full list of accounts from the DB

        Returns
        -------
        allAccounts : VCSAccountEntity
            List of accounts

        """
        query = "SELECT {}, {} FROM {}".format(self._username,
                                               self._url,
                                               self._account_data)
        accounts = super().query(query)
        allAccounts = []
        for account in accounts:
            account = list(account)
            allAccounts.append(
                entities.EntityFactory.makeVCSAccountEntity(
                    username=account[0], domainURL=account[1]))
        return allAccounts

    def getCustomerAccounts(self, customerEntity):
        """
        Get the list of accounts by customer from the DB

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer name

        Returns
        -------
        customerAccounts : List
            List of account entities associated to the customer.

        """
        customer = customerEntity.getCustomerName()
        query = "SELECT {}, {} FROM {} WHERE {}='{}'".format(self._username,
                                                             self._url,
                                                             self._account_data,
                                                             self._customer,
                                                             customer)
        accounts = super().query(query)
        customerAccounts = []
        for account in accounts:
            account = list(account)
            customerAccounts.append(
                entities.EntityFactory.makeVCSAccountEntity(
                username=account[0], domainURL=account[1]))
        return customerAccounts

    def getToken(self, customerEntity, accountEntity):
        """
        Queries the DB for an account/owner's OAuth token

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer name
        accountEntity  : VCSAccountEntity
            Entity with VCS account information, created by entities factory

        Returns
        -------
        token : AccessTokenEntity
            Account's OAuth token, in AccessTokenEntity format

        """
        customer = customerEntity.getCustomerName()
        username = accountEntity.getUsername()
        url = accountEntity.getDomainURL()
        query = "SELECT {} FROM {} WHERE {}='{}' AND {}='{}' AND {}='{}'".format(
            self._token, self._account_data, self._customer, customer,
            self._username, username, self._url, url)
        tToken = super().query(query)
        lToken = list(tToken[0])
        token = entities.EntityFactory.makeAccessTokenEntity(lToken[0])
        return token

    def replaceToken(self, customerEntity, accountEntity, tokenEntity):
        """
        Replace an account/owner's OAuth token in the DB

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer name
        accountEntity  : VCSAccountEntity
            Entity with VCS account information, created by entities factory
        tokenEntity    : AccessTokenEntity
            Entity with account/owner's token, created by entities factory

        Returns
        -------
        None.

        """
        customer = customerEntity.getCustomerName()
        username = accountEntity.getUsername()
        url = accountEntity.getDomainURL()
        access_token = tokenEntity.getTokenValue()
        update = "UPDATE {} SET {}='{}' WHERE {}='{}' AND {}='{}' \
            AND {}='{}'".format(
            self._account_data, self._token, access_token,
            self._customer, customer, self._username, username,
            self._url, url)
        super().cursor.execute(update)
        super().connection.commit()

######

### Modifying Customer Entities
    def addCustomer(self, customerEntity):
        """
        Add a customer to the DB

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer information, created by entities factory

        Returns
        -------
        None.

        """
        customer = customerEntity.getCustomerName()
        columns = self.columns(self._customer_data)
        columns = ','.join(columns)
        statement = "INSERT INTO {} ({}) VALUES (%s)".format(
            self._customer_data, columns)
        super().cursor.execute(statement, customer)
        super().connection.commit()
        pass

    def removeCustomer(self, customerEntity):
        """
        Remove a customer from DB

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer information, created by entities factory

        Returns
        -------
        None.

        """
        customer = customerEntity.getCustomerName()
        sql_delete = "DELETE FROM {} WHERE {} = '{}'".format(
            self._customer_data, self._customer, customer)
        super().cursor.execute(sql_delete)
        super().connection.commit()
        pass

### Modifying Account Entries
    def addAccount(self, customerEntity, accountEntity, tokenEntity):
        """
        Add an account to the DB

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer name
        accountEntity  : VCSAccountEntity
            Entity with VCS account information, created by entities factory
        tokenEntity    : AccessTokenEntity
            Entity with account/owner's token, created by entities factory

        Returns
        -------
        None.

        """
        customer = customerEntity.getCustomerName()
        username = accountEntity.getUsername()
        url = accountEntity.getDomainURL()
        access_token = tokenEntity.getTokenValue()
        account_info = (customer, url, username, access_token)
        columns = self.columns(self._account_data)
        columns = ','.join(columns)
        sstr = ','.join('s' * len(account_info))
        sstr = sstr.replace('s', '%s')
        statement = "INSERT INTO {} ({}) VALUES ({})".format(
            self._account_data, columns, sstr)
        super().cursor.execute(statement, account_info)
        super().connection.commit()

    def removeAccount(self, customerEntity, accountEntity):
        """
        Remove an account from DB

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer name
        accountEntity  : VCSAccountEntity
            Entity with VCS account information, created by entities factory

        Returns
        -------
        None.

        """
        customer = customerEntity.getCustomerName()
        username = accountEntity.getUsername()
        url = accountEntity.getDomainURL()
        sql_delete = "DELETE FROM {} WHERE {}='{}' AND {}='{}' \
            AND {}='{}'".format(
            self._account_data, self._customer, customer, self._username,
            username, self._url, url)
        super().cursor.execute(sql_delete)
        super().connection.commit()
######

### Querying Repository Entries
    def getAccountRepositories(self, accountEntity):
        """
        Get all Repositories assigned to an account

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer information
        accountEntity  : VCSAccountEntity
            Entity with account information, created by entities factory

        Returns
        -------
        repos : RepositoryEntity
            List of repositories

        """
        username = accountEntity.getUsername()
        url = accountEntity.getDomainURL()
        query = "SELECT * FROM {} WHERE {}='{}' AND {}='{}'".format(
            self._repo_data, self._username, username, self._url, url)
        results = super().query(query)
        repos = []
        for repo in results:
            repo = list(repo)
            repos.append(
                entities.EntityFactory.makeRepositoryEntity(
                    repo[2], repo[3], repo[0]))
        return repos

    def repoExists(self, accountEntity, repoEntity):
        """
        Check if a repository exists for an account

        Parameters
        ----------
        accountEntity : VCSAccountEntity
            Entity with account information, created by entities factory
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory

        Returns
        -------
        bool
            True : Yes, repository exists

        """
        username = accountEntity.getUsername()
        url = accountEntity.getDomainURL()
        owner = repoEntity.getOwnerName()
        repo = repoEntity.getRepositoryName()
        sql = "SELECT * FROM {} WHERE {}='{}' AND {}='{}' AND {}='{}' \
            AND {}='{}'".format(
            self._repo_data, self._username, username, self._url, url,
            self._owner, owner, self._repo, repo)
        result = super().query(sql)
        if not result:
            return False
        else:
            return True
######

### Modifying Repository Entries
    def addRepository(self, accountEntity, repoEntity):
        """
        Add a repository for a account to the DB

        Parameters
        ----------
        accountEntity : VCSAccountEntity
            Entity with account information, created by entities factory
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory

        Returns
        -------
        None.

        """
        columns = self.columns(self._repo_data)
        sstr = ','.join('s' * len(columns))
        sstr = sstr.replace('s', '%s')
        columns = ','.join(columns)
        data = (
            accountEntity.getDomainURL(),
            accountEntity.getUsername(),
            repoEntity.getOwnerName(),
            repoEntity.getRepositoryName())
        statement = "INSERT INTO {} ({}) VALUES ({})".format(
            self._repo_data, columns, sstr)
        super().cursor.execute(statement, data)
        super().connection.commit()

    def removeRepository(self, accountEntity, repoEntity):
        """
        Remove a repository for a account from the DB

        Parameters
        ----------
        accountEntity : VCSAccountEntity
            Entity with account information, created by entities factory
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory

        Returns
        -------
        None.

        """
        username = accountEntity.getUsername()
        url = repoEntity.getDomainURL()
        owner = repoEntity.getOwnerName()
        repo = repoEntity.getRepositoryName()
        sql_delete = "DELETE FROM {} WHERE {}='{}' AND {}='{}' AND {}='{}' \
            AND {}='{}'".format(
            self._repo_data, self._username, username, self._url, url,
            self._owner, owner, self._repo, repo)
        super().cursor.execute(sql_delete)
        super().connection.commit()
######

### Querying Traffic Data
    def _observationExists(self, accountEntity, repoEntity, observationEntity):
        """
        Check if a set of observations already exists in the DB.
        Only checks the url, username, owner, repo, tag, and timestamp.
        Don't care if the value matches - it will be updated with
        the newest value if the values don't match.

        Parameters
        ----------
        accountEntity : VCSAccountEntity
            Entity with account information, created by entities factory
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory
        observationEntity : ObservationEntity
            Entity with observation data, created by entities factory

        Returns
        -------
        bool
            True : Yes, observation exists.

        """
        username = accountEntity.getUsername()
        url = repoEntity.getDomainURL()
        owner = repoEntity.getOwnerName()
        repo = repoEntity.getRepositoryName()
        tag = observationEntity.getTag()
        timestamp = observationEntity.getTimestamp()
        sql = "SELECT * FROM {} WHERE {}='{}' AND {}='{}' AND {}='{}' \
            AND {}='{}' AND {}='{}' AND {}='{}'".format(
            self._data_table, self._username, username, self._url, url,
            self._owner, owner, self._repo, repo, self._tag, tag,
            self._time, timestamp)
        result = super().query(sql)
        if result:
            return True
        else:
            return False

    def getObservations(self, accountEntity, repoEntity):
        """
        Get all observations that currently exist in the
        DB for a chosen repository

        Parameters
        ----------
        accountEntity : VCSAccountEntity
            Entity with account information, created by entities factory
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory

        Returns
        -------
        observations : ObservationEntity
            List of all observations currently in the DB

        """
        username = accountEntity.getUsername()
        url = repoEntity.getDomainURL()
        owner = repoEntity.getOwnerName()
        repo = repoEntity.getRepositoryName()
        sql = "SELECT * FROM {} WHERE {}='{}' AND {}='{}' \
            AND {}='{}' AND {}='{}'".format(
            self._data_table, self._username, username, self._url, url,
            self._owner, owner, self._repo, repo)
        results = super().query(sql)
        observations = []
        for result in results:
            result = list(result)
            timestamp = result[4]
            tag = result[5]
            value = result[6]
            observations.append(
                entities.EntityFactory.makeObservationEntity(
                    tag, timestamp, value))
        return observations
######

### Modifying Traffic Data
    def insertObservations(self, accountEntity, repoEntity,
                           observationEntityList):
        """
        Insert gathered observations for a repository into the DB

        Parameters
        ----------
        accountEntity : VCSAccountEntity
            Entity with account information, created by entities factory
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory
        observationEntityList : ObservationEntity
            Entity with observation data, created by entities factory

        Returns
        -------
        None.

        """
        columns = self.columns(self._data_table)
        sstr = ','.join('s' * len(columns))
        sstr = sstr.replace('s', '%s')
        columns = ','.join(columns)
        username = accountEntity.getUsername()
        url = repoEntity.getDomainURL()
        owner = repoEntity.getOwnerName()
        repo = repoEntity.getRepositoryName()
        for obsv in observationEntityList:
            if self._observationExists(accountEntity, repoEntity, obsv) is True:
                tag = obsv.getTag()
                timestamp = obsv.getTimestamp()
                nValue = obsv.getValue()
                nValue = int(nValue)
                sql = "SELECT {} FROM {} WHERE {}='{}' AND {}='{}' AND {}='{}' \
                    AND {}='{}' AND {}='{}' AND {}='{}'".format(
                    self._value, self._data_table,
                    self._username, username,
                    self._url, url,
                    self._owner, owner,
                    self._repo, repo,
                    self._tag, tag,
                    self._time, timestamp)
                oValue = super().query(sql)
                oValue = list(oValue[0])
                oValue = int(oValue[0])
                if nValue > oValue:
                    update = "UPDATE {} SET {}='{}' WHERE {}='{}' AND {}='{}' \
                        AND {}='{}' AND {}='{}' AND {}='{}' AND {}='{}'".format(
                        self._data_table,
                        self._value, nValue,
                        self._username, username,
                        self._url, url,
                        self._owner, owner,
                        self._repo, repo,
                        self._tag, tag,
                        self._time, timestamp)
                    super().cursor.execute(update)
                    super().connection.commit()
                else:
                    pass
                    # TODO: raise DBAPIException("Tag {} with timestamp {} exists for {}/{}; will
                    # not add to avoid duplication.".format(tag, timestamp, owner, repo))  <--
                    # Turn into a logged message
            else:
                tag = obsv.getTag()
                timestamp = obsv.getTimestamp()
                value = obsv.getValue()
                data = (url, username, owner, repo, timestamp, tag, value)
                sql = "INSERT INTO {} ({}) VALUES ({})".format(
                    self._data_table, columns, sstr)
                super().cursor.execute(sql, data)
                super().connection.commit()

    def removeObservation(self, accountEntity, repoEntity, observationEntity):
        """
        Remove an observation for a repository from the DB

        Parameters
        ----------
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory
        observationEntity : ObservationEntity
            Entity with observation data, created by entities factory

        Raises
        ------
        DBAPIException
            Raises an error if user tries to
            remove an observation that doesn't exist.

        Returns
        -------
        None.

        """
        username = accountEntity.getUsername()
        url = repoEntity.getDomainURL()
        owner = repoEntity.getOwnerName()
        repo = repoEntity.getRepositoryName()
        tag = observationEntity.getTag()
        timestamp = observationEntity.getTimestamp()
        if self._observationExists(accountEntity,
                                   repoEntity,
                                   observationEntity) is False:
            raise DBAPIException(
                "Tag {} with timestamp {} does not exist \
                    for {}/{} and cannot be deleted.".format(
                    tag, timestamp, owner, repo))
        else:
            sql_delete = "DELETE FROM {} WHERE {}='{}' AND {}='{}' AND {}='{}' \
                AND {}='{}' AND {}='{}' AND {}='{}'".format(
                self._data_table, self._username, username, self._url, url,
                self._owner, owner, self._repo, repo, self._tag, tag,
                self._time, timestamp)
            super().cursor.execute(sql_delete)
            super().connection.commit()
######

### Other Functions
    def customerAccountAssociated(self, customerEntity, accountEntity):
        """
        Check if a customer is associated to an account.

        Parameters
        ----------
        customerEntity : CustomerEntity
            Entity with customer name
        accountEntity  : VCSAccountEntity
            Entity with VCS account information, created by entities factory

        Returns
        -------
        bool
            True : Yes, customer and account are associated

        """
        customer = customerEntity.getCustomerName()
        username = accountEntity.getUsername()
        url = accountEntity.getDomainURL()
        sql = "SELECT * FROM {} WHERE {}='{}' AND {}='{}' AND {}='{}'".format(
            self._account_data, self._customer, customer,
            self._username, username, self._url, url)
        result = super().query(sql)
        if result:
            return True
        else:
            return False

    def accountRepositoryAssociated(self, accountEntity, repoEntity):
        """
        Check if a repository is associated with an account

        Parameters
        ----------
        accountEntity : VCSAccountEntity
            Entity with account information, created by entities factory
        repoEntity : RepositoryEntity
            Entity with repository information, created by entities factory

        Returns
        -------
        bool
            True : Yes, account and repository are associated

        """
        username = accountEntity.getUsername()
        url = repoEntity.getDomainURL()
        owner = repoEntity.getOwnerName()
        repo = repoEntity.getRepositoryName()
        sql = "SELECT * FROM {} WHERE {}='{}' AND {}='{}' \
            AND {}='{}' AND {}='{}'".format(
            self._repo_data, self._username, username, self._url, url,
            self._owner, owner, self._repo, repo)
        result = super().query(sql)
        if result:
            return True
        else:
            return False
