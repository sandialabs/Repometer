#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Response:
    Constructs and interprets response models.
"""

from enum import Enum, auto
from repometer.core.entities import EntityVisitor


class EntityConverter(EntityVisitor):
    """
    Converts entity data to a generic representation that can be used
    by delivery systems (e.g. plotting, outputting as JSON, et cetera).
    """
    pass


class DictionaryConverter(EntityConverter):

    def __init__(self):
        # This temporarily holds the output that we pass back to the caller of
        # convert().
        self._result = None

    def _storeResult(self, result):
        self._result = result

    def _getAndClearResult(self):
        output = self._result
        self._result = None
        return output

    def convert(self, entity):
        entity.accept(self)
        result = self._getAndClearResult()
        return result

    def visitCustomer(self, entity):
        customerName = entity.customerName()
        self._storeResult({'type': "customer", 'customerName': customerName})

    def visitVCSAccount(self, entity):
        username = entity.getUsername()
        domainURL = entity.getDomainURL()
        self._storeResult({'type': "account",
                           'username': username,
                           'domainURL': domainURL})

    def visitObservation(self, entity):
        tag = entity.getTag()
        timestamp = entity.getTimestamp()
        value = entity.getValue()
        self._storeResult({'type': "observation", 'tag': tag,
                           'timestamp': timestamp, 'value': value})

    def visitAccessToken(self, entity):
        tokenValue = entity.getTokenValue()
        self._storeResult({'type': "accesstoken", 'value': tokenValue})

    def visitRepository(self, entity):
        ownerName = entity.getOwnerName()
        repositoryName = entity.getRepositoryName()
        self._storeResult({'type': "repository",
                           'ownerName': ownerName,
                           'repositoryName': repositoryName})


class Status(Enum):
    """
    The status flag enum for ResponseModel objects.
    A response can either succeed or fail.
    """
    SUCCESS = auto()
    FAILURE = auto()


class ResponseFactory:
    """
    A factory for churning out response model objects.
    Classes should use this factory to construct responses.
    """

    @staticmethod
    def createSuccessResponse(message=None, attachments=None):
        return ResponseModel(status=Status.SUCCESS,
                             message=message, attachments=attachments)

    @staticmethod
    def createFailureResponse(message=None, attachments=None):
        return ResponseModel(status=Status.FAILURE,
                             message=message, attachments=attachments)


class ResponseModel:
    """
    The base class for all request models. Any outputs that Repometer provides
    must be stored as a response model as opposed to providing entities
    directly. This allows the internal representation of our data to
    vary independently of how that data is presented.
    """

    def __init__(self, status, message=None, attachments=None):
        """
        Parameters
        ----------
        status:
            A Status enum object that describes the outcome of a request.
        message:
            A string describing the outcome of the request.
            By default this is None.
        attachments:
            A field for storing output data that was the result of a request
            (if there is any to deliver).
            By default this is None.
        """
        self._status = status
        self._message = message
        self._attachments = attachments

    def hasMessage(self):
        return self._message is not None

    def getMessage(self):
        return self._message

    def hasAttachments(self):
        return self._attachments is not None

    def getAttachments(self):
        return self._attachments

    def wasSuccessful(self):
        if self._status == Status.SUCCESS:
            return True
        else:
            return False
