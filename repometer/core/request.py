#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Request:
    Instantiates request models.
"""

import datetime
from repometer.core.entities import EntityFactory


class RequestFactory:
    """
    A factory for churning out request model objects.
    Classes should use this factory to construct requests.
    """

    @staticmethod
    def createAddCustomerRequest(customerName):
        return AddCustomerRequest(customerName)

    @staticmethod
    def createRemoveCustomerRequest(customerName):
        return RemoveCustomerRequest(customerName)

    @staticmethod
    def createAddVCSAccountRequest(username, tokenValue,
                                   customerName, domainURL):
        return AddVCSAccountRequest(username, tokenValue,
                                    customerName, domainURL)

    @staticmethod
    def createRemoveVCSAccountRequest(username, customerName, domainURL):
        return RemoveVCSAccountRequest(username,
                                       customerName, domainURL)

    @staticmethod
    def createAddRepositoryRequest(username, ownerName,
                                   repositoryName, domainURL):
        return AddRepositoryRequest(username, ownerName,
                                    repositoryName, domainURL)

    @staticmethod
    def createRemoveRepositoryRequest(username, ownerName,
                                      repositoryName, domainURL):
        return RemoveRepositoryRequest(username, ownerName,
                                       repositoryName, domainURL)

    @staticmethod
    def createGetObservationsForRepositoryRequest(
            username, ownerName, repositoryName, domainURL):
        return GetObservationsForRepositoryRequest(
            username, ownerName, repositoryName, domainURL)

    @staticmethod
    def createCollectObservationsRequest():
        return CollectObservationsRequest()

    @staticmethod
    def createStatusRequest():
        return StatusRequest()


class RequestModel:
    """
    The base class for all request models. The frontend is responsible
    for phrasing their requests in the form of a request model which
    the interactor understands.
    """

    def __init__(self):
        # This timestamp is automatically created on construction,
        # and is used for logging purposes to track
        # when a particular request was created.
        self._createdTimestamp = datetime.datetime.now()

        self._errors = []

    def getCreatedTimestamp(self):
        return self._createdTimestamp

    def addError(self, parameter, message):
        self._errors.append({'parameter': parameter, 'message': message})

    def hasErrors(self):
        return len(self._errors) > 0

    def getErrors(self):
        return self._errors


class StatusRequest(RequestModel):
    def __init__(self):
        super().__init__()


class AddCustomerRequest(RequestModel):
    def __init__(self, customerName):
        super().__init__()
        self._customer = None
        try:
            self._customer = EntityFactory.makeCustomerEntity(customerName)
        except Exception as exception:
            self.addError('customerName', str(exception))

    def getCustomer(self):
        return self._customer


class RemoveCustomerRequest(RequestModel):
    def __init__(self, customerName):
        super().__init__()
        self._customer = None
        try:
            self._customer = EntityFactory.makeCustomerEntity(customerName)
        except Exception as exception:
            self.addError('customerName', str(exception))

    def getCustomer(self):
        return self._customer


class AddVCSAccountRequest(RequestModel):
    def __init__(self, username, tokenValue, customerName, domainURL):
        super().__init__()
        self._account = None
        self._token = None
        self._customer = None
        try:
            self._account = EntityFactory.makeVCSAccountEntity(username,
                                                               domainURL)
        except Exception as exception:
            self.addError('username/domainURL', str(exception))

        try:
            self._token = EntityFactory.makeAccessTokenEntity(tokenValue)
        except Exception as exception:
            self.addError('tokenValue', str(exception))

        try:
            self._customer = EntityFactory.makeCustomerEntity(customerName)
        except Exception as exception:
            self.addError('customerName', str(exception))

    def getVCSAccount(self):
        return self._account

    def getAccessToken(self):
        return self._token

    def getCustomer(self):
        return self._customer


class RemoveVCSAccountRequest(RequestModel):
    def __init__(self, username, customerName, domainURL):
        super().__init__()
        self._account = None
        self._customer = None
        try:
            self._account = EntityFactory.makeVCSAccountEntity(username,
                                                               domainURL)
        except Exception as exception:
            self.addError('username/domainURL', str(exception))

        try:
            self._customer = EntityFactory.makeCustomerEntity(customerName)
        except Exception as exception:
            self.addError('customerName', str(exception))

    def getVCSAccount(self):
        return self._account

    def getCustomer(self):
        return self._customer


class AddRepositoryRequest(RequestModel):
    def __init__(self, username, ownerName, repositoryName, domainURL):
        super().__init__()
        self._account = None
        self._repository = None

        try:
            self._account = EntityFactory.makeVCSAccountEntity(username,
                                                               domainURL)
        except Exception as exception:
            self.addError('username/domainURL', str(exception))

        try:
            self._repository = EntityFactory.makeRepositoryEntity(
                ownerName, repositoryName, domainURL)
        except Exception as exception:
            self.addError('ownerName/repositoryName', str(exception))

    def getVCSAccount(self):
        return self._account

    def getRepository(self):
        return self._repository


class RemoveRepositoryRequest(RequestModel):
    def __init__(self, username, ownerName, repositoryName, domainURL):
        super().__init__()
        self._account = None
        self._repository = None

        try:
            self._account = EntityFactory.makeVCSAccountEntity(username,
                                                               domainURL)
        except Exception as exception:
            self.addError('username', str(exception))

        try:
            self._repository = EntityFactory.makeRepositoryEntity(
                ownerName, repositoryName, domainURL)
        except Exception as exception:
            self.addError('ownerName/repositoryName', str(exception))

    def getVCSAccount(self):
        return self._account

    def getRepository(self):
        return self._repository


class GetObservationsForRepositoryRequest(RequestModel):
    def __init__(self, username, ownerName, repositoryName, domainURL):
        super().__init__()
        self._account = None
        self._repository = None
        try:
            self._account = EntityFactory.makeVCSAccountEntity(username,
                                                               domainURL)
        except Exception as exception:
            self.addError('username/domainURL', str(exception))

        try:
            self._repository = EntityFactory.makeRepositoryEntity(
                ownerName, repositoryName, domainURL)
        except Exception as exception:
            self.addError('ownerName/repositoryName/domainURL', str(exception))

    def getVCSAccount(self):
        return self._account

    def getRepository(self):
        return self._repository


class CollectObservationsRequest(RequestModel):
    def __init__(self):
        super().__init__()
