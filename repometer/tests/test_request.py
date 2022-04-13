#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

import pytest
import repometer.core.request as requestapi


def test_RequestModel_AlwaysHasCreatedTimestamp():
    requestModel = requestapi.RequestModel()
    assert(requestModel.getCreatedTimestamp() is not None)


def test_RequestModel_InitiallyHasNoErrors():
    requestModel = requestapi.RequestModel()
    assert(requestModel.hasErrors() is False)
    assert(len(requestModel.getErrors()) == 0)


def test_RequestModel_CanStoreErrors():
    requestModel = requestapi.RequestModel()
    requestModel.addError(parameter='parameter', message='message')
    assert(requestModel.hasErrors() is True)
    assert(len(requestModel.getErrors()) == 1)


def test_AddVCSAccountRequest_ConstructibleByFactory():
    handle = "schuler"
    token = "k8675309"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.RequestFactory.createAddVCSAccountRequest(
        username=handle,
        tokenValue=token,
        customerName=customerName,
        domainURL=domainURL)


def test_AddVCSAccountRequest_IsDirectlyConstructible():
    handle = "schuler"
    token = "k8675309"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.AddVCSAccountRequest(username=handle,
                                              tokenValue=token,
                                              customerName=customerName,
                                              domainURL=domainURL)


def test_AddVCSAccountRequest_ValidInputsMakeValidRequest():
    handle = "schuler"
    token = "k8675309"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.AddVCSAccountRequest(username=handle,
                                              tokenValue=token,
                                              customerName=customerName,
                                              domainURL=domainURL)
    assert(request.hasErrors() is False)


def test_AddVCSAccountRequest_InvalidInputsMakeInvalidRequest():
    handle = ""
    token = 502
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.AddVCSAccountRequest(username=handle,
                                              tokenValue=token,
                                              customerName=customerName,
                                              domainURL=domainURL)
    assert(request.hasErrors() is True)


def test_AddVCSAccountRequest_CanAccessParameters():
    handle = "schuler"
    token = "k8675309"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.AddVCSAccountRequest(username=handle,
                                              tokenValue=token,
                                              customerName=customerName,
                                              domainURL=domainURL)
    client = request.getVCSAccount()
    token = request.getAccessToken()


def test_RemoveVCSAccountRequest_ConstructibleByFactory():
    handle = "schuler"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.RequestFactory.createRemoveVCSAccountRequest(
        username=handle, customerName=customerName, domainURL=domainURL)


def test_RemoveVCSAccountRequest_IsDirectlyConstructible():
    handle = "schuler"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.RemoveVCSAccountRequest(username=handle,
                                                 customerName=customerName,
                                                 domainURL=domainURL)


def test_RemoveVCSAccountRequest_ValidInputsMakeValidRequest():
    handle = "schuler"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.RemoveVCSAccountRequest(username=handle,
                                                 customerName=customerName,
                                                 domainURL=domainURL)
    assert(request.hasErrors() is False)


def test_RemoveVCSAccountRequest_InvalidInputsMakeInvalidRequest():
    handle = ""
    customerName = ""
    domainURL = "github.com"
    request = requestapi.RemoveVCSAccountRequest(username=handle,
                                                 customerName=customerName,
                                                 domainURL=domainURL)
    assert(request.hasErrors() is True)


def test_RemoveVCSAccountRequest_CanAccessParameters():
    handle = "schuler"
    customerName = "institute"
    domainURL = "github.com"
    request = requestapi.RemoveVCSAccountRequest(username=handle,
                                                 customerName=customerName,
                                                 domainURL=domainURL)
    account = request.getVCSAccount()
    customer = request.getCustomer()


def test_AddRepositoryRequest_ConstructibleByFactory():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.RequestFactory.createAddRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)


def test_AddRepositoryRequest_IsDirectlyConstructible():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.AddRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)


def test_AddRepositoryRequest_ValidInputsMakeValidRequest():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.AddRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    assert(request.hasErrors() is False)


def test_AddRepositoryRequest_InvalidInputsMakeInvalidRequest():
    handle = ""
    ownerName = ""
    repositoryName = ""
    domainURL = "github.com"
    request = requestapi.AddRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    assert(request.hasErrors() is True)


def test_AddRepositoryRequest_CanAccessParameters():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.AddRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    client = request.getVCSAccount()
    repository = request.getRepository()


def test_RemoveRepositoryRequest_ConstructibleByFactory():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.RequestFactory.createRemoveRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)


def test_RemoveRepositoryRequest_IsDirectlyConstructible():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.RemoveRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)


def test_RemoveRepositoryRequest_ValidInputsMakeValidRequest():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.RemoveRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    assert(request.hasErrors() is False)


def test_GetObservationsForRepositoryRequest_InvalidInputsMakeInvalidRequest():
    handle = ""
    ownerName = ""
    repositoryName = ""
    domainURL = "github.com"
    request = requestapi.GetObservationsForRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    assert(request.hasErrors() is True)


def test_GetObservationsForRepositoryRequest_CanAccessParameters():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.GetObservationsForRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    client = request.getVCSAccount()
    repository = request.getRepository()


def test_GetObservationsForRepositoryRequest_ConstructibleByFactory():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.RequestFactory.createGetObservationsForRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)


def test_GetObservationsForRepositoryRequest_IsDirectlyConstructible():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.GetObservationsForRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)


def test_GetObservationsForRepositoryRequest_ValidInputsMakeValidRequest():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.GetObservationsForRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    assert(request.hasErrors() is False)


def test_GetObservationsForRepositoryRequest_InvalidInputsMakeInvalidRequest():
    handle = ""
    ownerName = ""
    repositoryName = ""
    domainURL = "github.com"
    request = requestapi.GetObservationsForRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    assert(request.hasErrors() is True)


def test_GetObservationsForRepositoryRequest_CanAccessParameters():
    handle = "schuler"
    ownerName = "scipak"
    repositoryName = "vizpak"
    domainURL = "github.com"
    request = requestapi.GetObservationsForRepositoryRequest(
        handle, ownerName, repositoryName, domainURL)
    client = request.getVCSAccount()
    repository = request.getRepository()


def test_CollectObservationsRequest_ConstructibleByFactory():
    request = requestapi.RequestFactory.createCollectObservationsRequest()


def test_CollectObservationsRequest_IsDirectlyConstructible():
    request = requestapi.CollectObservationsRequest()
