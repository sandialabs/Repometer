#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

import repometer.core.interactor as interactorapi
import repometer.core.repoapi as repoapi
import repometer.database.database as dbapi
from repometer.core.request import RequestFactory
from repometer.core.entities import EntityFactory
import pytest


def test_Orchestrator_ConstructibleByFactory():
    orchestrator = interactorapi.InteractorFactory.createOrchestrator()
    assert(isinstance(orchestrator, interactorapi.Orchestrator))


def test_Orchestrator_InitiallyHasNoChildren():
    orchestrator = interactorapi.Orchestrator()
    assert(orchestrator.getNumberOfChildren() == 0)


def test_Orchestrator_CantFulfillRequestsWithoutChildren():
    orchestrator = interactorapi.Orchestrator()
    request = RequestFactory.createCollectObservationsRequest()
    assert(orchestrator.canHandleRequest(request) is False)


def test_Orchestrator_CanStoreChildren(mocker):
    mocker.patch.multiple(
        interactorapi.TrafficInteractor,
        __abstractmethods__=set())
    genericInteractor = interactorapi.TrafficInteractor()
    orchestrator = interactorapi.Orchestrator()
    orchestrator.addChild(genericInteractor)
    assert(orchestrator.hasChild(genericInteractor))
    assert(orchestrator.getNumberOfChildren() == 1)


def test_Orchestrator_CanRemoveChildren(mocker):
    mocker.patch.multiple(
        interactorapi.TrafficInteractor,
        __abstractmethods__=set())
    genericInteractor = interactorapi.TrafficInteractor()
    orchestrator = interactorapi.Orchestrator()
    orchestrator.addChild(genericInteractor)
    orchestrator.removeChild(genericInteractor)
    assert(orchestrator.hasChild(genericInteractor) is False)
    assert(orchestrator.getNumberOfChildren() == 0)


def test_Orchestrator_CanFulfillRequestIfChildCan(mocker):
    mocker.patch.multiple(
        interactorapi.TrafficInteractor,
        __abstractmethods__=set())

    def canAlwaysHandleRequest(self, request):
        return True
    interactorapi.TrafficInteractor.canHandleRequest = canAlwaysHandleRequest
    genericInteractor = interactorapi.TrafficInteractor()
    orchestrator = interactorapi.Orchestrator()
    orchestrator.addChild(genericInteractor)
    request = RequestFactory.createCollectObservationsRequest()
    assert(orchestrator.canHandleRequest(request) is True)


def test_Orchestrator_CantFulfillRequestIfChildCant(mocker):
    mocker.patch.multiple(
        interactorapi.TrafficInteractor,
        __abstractmethods__=set())

    def canNeverHandleRequest(self, request):
        return False
    interactorapi.TrafficInteractor.canHandleRequest = canNeverHandleRequest
    genericInteractor = interactorapi.TrafficInteractor()

    orchestrator = interactorapi.Orchestrator()
    orchestrator.addChild(genericInteractor)
    request = RequestFactory.createCollectObservationsRequest()
    assert(orchestrator.canHandleRequest(request) is False)


def test_Orchestrator_GeneratesAFailedResponseOnExecuteIfUnable():
    orchestrator = interactorapi.Orchestrator()
    request = RequestFactory.createCollectObservationsRequest()
    response = orchestrator.execute(request)
    assert(response.wasSuccessful() is False)


def test_AddVCSAccountInteractor_IsConstructibleByFactory():
    interactor = interactorapi.InteractorFactory.createAddVCSAccountInteractor()
    assert(isinstance(interactor, interactorapi.AddVCSAccountInteractor))


def test_AddVCSAccountInteractor_CanHandleRequest():
    handle = "schuler"
    token = "k8675309"
    customerName = "institute"
    domainURL = "github.com"
    request = RequestFactory.createAddVCSAccountRequest(
        username=handle,
        tokenValue=token,
        customerName=customerName,
        domainURL=domainURL)
    interactor = interactorapi.AddVCSAccountInteractor()
    assert(interactor.canHandleRequest(request))


def test_AddVCSAccountInteractor_RequestsWithErrorsResultInFailedResponse():
    handle = ""
    token = ""
    customerName = ""
    domainURL = ""
    request = RequestFactory.createAddVCSAccountRequest(
        username=handle,
        tokenValue=token,
        customerName=customerName,
        domainURL=domainURL)
    interactor = interactorapi.AddVCSAccountInteractor()
    response = interactor.execute(request)
    assert(response.wasSuccessful() is False)


def test_CollectObservationsInteractor_canHandleRelevantRequest():
    """
    This test confirms that the CollectObservationsInteractor recognizes
    that it can handle CollectObservationsRequest
    objects.
    """
    collectorInteractor = interactorapi.InteractorFactory.createCollectObservationsInteractor()
    request = RequestFactory.createCollectObservationsRequest()
    assert(collectorInteractor.canHandleRequest(request) is True)


def test_CollectObservationsInteractor_RequestsWithErrorsResultInFailedResponse():
    """
    Given that the CollectObservationsRequest takes no parameters, it should
    be impossible for a request to have errors in it. Regardless, the
    CollectObservationsInteractor must check the status
    of the incoming request.
    """
    collectorInteractor = interactorapi.InteractorFactory.createCollectObservationsInteractor()
    request = RequestFactory.createCollectObservationsRequest()
    request.addError(parameter="spurious", message="garbage")
    response = collectorInteractor.execute(request)
    assert(response.wasSuccessful() is False)


def test_CollectObservationsInteractor_capturesDatabaseConnectionFailure(mocker):
    """
    It is possible for the database to be down when the interactor tries to
    open a connection to it, and the interactorshould return a failed response.
    """
    mocker.patch('repometer.database.database.DatabaseAPIFactory.createDefaultDBAPI',
                 side_effect=dbapi.DBAPIException)
    collectorInteractor = interactorapi.InteractorFactory.createCollectObservationsInteractor()
    request = RequestFactory.createCollectObservationsRequest()
    response = collectorInteractor.execute(request)
    assert(response.wasSuccessful() is False)
    assert(response.hasAttachments() is True)
    assert(type(response.getAttachments()[0]) == dbapi.DBAPIException)


def test_CollectObservationsInteractor_succeedsIfThereAreNoCustomers(mocker):
    """
    If the interactor has no clients to collect data for, that's not an error.
    This test confirms that the interactor marks the response
    as (trivally) successful.
    """
    mockDB = mocker.Mock()
    mockDB.getAllCustomers.return_value = []
    mocker.patch('repometer.database.database.DatabaseAPIFactory.createDefaultDBAPI',
                 return_value=mockDB)
    collectorInteractor = interactorapi.InteractorFactory.createCollectObservationsInteractor()
    request = RequestFactory.createCollectObservationsRequest()
    response = collectorInteractor.execute(request)
    assert(response.wasSuccessful() is True)


def test_CollectObservationsInteractor_succeedsIfCustomerHasNoRepositories(mocker):
    """
    It is possible for a client to have no repositories associated with it
    (e.g. the client's repo is removed from the database but the client is
     still listed), and the interactor should skip over it with no errors.
    """
    mockDB = mocker.Mock()
    mockDB.getCustomerAccounts.return_value = [
        EntityFactory.makeVCSAccountEntity("FakeClient","github.com")]
    mockDB.getAllCustomers.return_value = [
        EntityFactory.makeCustomerEntity("Alice Customer")]
    mockDB.getAccountRepositories.return_value = []
    mocker.patch('repometer.database.database.DatabaseAPIFactory.createDefaultDBAPI'
                 , return_value=mockDB)
    collectorInteractor = interactorapi.InteractorFactory.createCollectObservationsInteractor()
    request = RequestFactory.createCollectObservationsRequest()
    response = collectorInteractor.execute(request)
    assert(response.wasSuccessful() is True)


@pytest.mark.disable_socket
def test_CollectObservationsInteractor_capturesGitHubAPIConnectionFailure(mocker):
    """
    For this test, we disable the network connection, which will cause the
    PyGitHub instance to fail on construction. We mock the database
    connection so we can exercise the GitHubAPISession error-handling behavior.
    """
    mockDB = mocker.Mock()
    mockDB.getCustomerAccounts.return_value = [
        EntityFactory.makeVCSAccountEntity(username="FakeClient",
                                           domainURL="github.com")]
    mockDB.getAccountRepositories.return_value = [
        EntityFactory.makeRepositoryEntity(ownerName="illiad",
                                           repositoryName="equine",
                                           domainURL="github.com")]
    mockDB.getToken.return_value = EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    mockDB.getAllCustomers.return_value = [EntityFactory.makeCustomerEntity("Alice")]
    
    mocker.patch('repometer.database.database.DatabaseAPIFactory.createDefaultDBAPI',
                 return_value=mockDB)
    collectorInteractor = interactorapi.InteractorFactory.createCollectObservationsInteractor()
    request = RequestFactory.createCollectObservationsRequest()
    response = collectorInteractor.execute(request)
    assert(response.wasSuccessful() is False)
    assert(response.hasAttachments() is True)
    assert(len(response.getAttachments()[0]) == 1)
    for k in response.getAttachments()[0]:
            print(k)
    assert(type(response.getAttachments()[0]["Alice:FakeClient:illiad/equine"])
           == repoapi.RequestFailureException)


def test_CollectObservationsInteractor_capturesUnexpectedExceptions(mocker):
    """
    We expect the interactor to deliver a response even if it encounters an
    unusual exception. Here we deliberately inject a divide-by-zero exception
    into the GitHubAPISession factory routine, and this should cause the
    interactor to halt execution immediately.
    """
    mockDB = mocker.Mock()
    mockDB.getAllCustomers.return_value = [
        EntityFactory.makeCustomerEntity("Alice Customer")]
    mockDB.getCustomerAccounts.return_value = [
        EntityFactory.makeVCSAccountEntity(username="FakeClient",
                                           domainURL="github.com")]
    mockDB.getAccountRepositories.return_value = [
        EntityFactory.makeRepositoryEntity(ownerName="illiad",
                                           repositoryName="equine",
                                           domainURL="github.com")]
    mockDB.getToken.return_value = EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")

    mocker.patch('repometer.database.database.DatabaseAPIFactory.createDefaultDBAPI',
                 return_value=mockDB)
    mocker.patch('repometer.core.repoapi.VCSAPISessionFactory.createGitHubAPISessionWithStrategies',
                 side_effect=ZeroDivisionError)
    collectorInteractor = interactorapi.InteractorFactory.createCollectObservationsInteractor()
    request = RequestFactory.createCollectObservationsRequest()
    response = collectorInteractor.execute(request)

    assert(response.wasSuccessful() is False)
    assert(response.hasAttachments() is True)
    assert(len(response.getAttachments()) == 1)
    assert(type(response.getAttachments()[0]) == ZeroDivisionError)
