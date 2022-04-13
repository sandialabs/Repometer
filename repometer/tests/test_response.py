#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

import pytest
import repometer.core.response as responseapi
from repometer.core.entities import EntityFactory
import datetime


def test_DictionaryConverter_IsDirectlyConstructible():
    converter = responseapi.DictionaryConverter()


def test_DictionaryConverter_CanConvertVCSAccount():
    converter = responseapi.DictionaryConverter()
    account = EntityFactory.makeVCSAccountEntity(username="alice",
                                                 domainURL="github.com")
    result = converter.convert(account)
    assert(isinstance(result, dict))
    assert('type' in result)
    assert(result['type'] == "account")
    assert('username' in result)
    assert(result['username'] == "alice")
    assert('domainURL' in result)
    assert(result['domainURL'] == "github.com")


def test_DictionaryConverter_CanConvertAccessToken():
    converter = responseapi.DictionaryConverter()
    token = EntityFactory.makeAccessTokenEntity("f751a9b")
    result = converter.convert(token)
    assert(isinstance(result, dict))
    assert('type' in result)
    assert(result['type'] == "accesstoken")
    assert('value' in result)
    assert(result['value'] == "f751a9b")


def test_DictionaryConverter_CanConvertRepository():
    converter = responseapi.DictionaryConverter()
    repository = EntityFactory.makeRepositoryEntity(
        ownerName="equine",
        repositoryName="troy",
        domainURL="github.com")
    result = converter.convert(repository)
    assert(isinstance(result, dict))
    assert('type' in result)
    assert(result['type'] == "repository")
    assert('ownerName' in result)
    assert(result['ownerName'] == "equine")
    assert('repositoryName' in result)
    assert(result['repositoryName'] == "troy")


def test_DictionaryConverter_CanConvertObservation():
    converter = responseapi.DictionaryConverter()
    timestamp = datetime.datetime.now().date()
    observation = EntityFactory.makeObservationEntity(
        tag="stargazers", timestamp=timestamp, value=500)
    result = converter.convert(observation)
    assert(isinstance(result, dict))
    assert('type' in result)
    assert(result['type'] == "observation")
    assert('tag' in result)
    assert(result['tag'] == "stargazers")
    assert('timestamp' in result)
    assert(result['timestamp'] == timestamp)
    assert('value' in result)
    assert(result['value'] == 500)


def test_ResponseModel_CanConstructSuccessfulResponseByFactory():
    message = None
    attachments = None
    successfulResponse = responseapi.ResponseFactory.createSuccessResponse(
        message, attachments)
    assert(successfulResponse.wasSuccessful() is True)


def test_ResponseModel_CanConstructFailureResponseByFactory():
    message = None
    attachments = None
    successfulResponse = responseapi.ResponseFactory.createFailureResponse(
        message, attachments)
    assert(successfulResponse.wasSuccessful() is False)


def test_ResponseModel_HasNoMessageByDefault():
    status = None
    response = responseapi.ResponseModel(status)
    assert(response.hasMessage() is False)
    assert(response.getMessage() is None)


def test_ResponseModel_HasNoAttachmentsByDefault():
    status = None
    response = responseapi.ResponseModel(status)
    assert(response.hasAttachments() is False)
    assert(response.getAttachments() is None)


def test_ResponseModel_CanStoreAttachments():
    status = None
    attachments = ["dataA", "dataB"]
    response = responseapi.ResponseModel(
        status, message=None, attachments=attachments)
    assert(response.hasAttachments() is True)
    assert(len(response.getAttachments()) == 2)


def test_ResponseModel_CanStoreMessage():
    status = None
    message = "details listed here"
    response = responseapi.ResponseModel(
        status, message=message, attachments=None)
    assert(response.hasMessage() is True)
    assert(response.getMessage() == message)
