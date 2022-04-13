#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

import pytest
import repometer.core.repoapi as repoapi
import repometer.core.entities as entities


def test_repoapi_VCSAPIServiceStrategy_ResultInitiallyUnavailable(mocker):
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())
    strategy = repoapi.VCSAPIServiceStrategy()
    assert(strategy.resultIsAvailable() is False)


def test_repoapi_VCSAPIServiceStrategy_StoringAResultMeansAvailability(mocker):
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())
    strategy = repoapi.VCSAPIServiceStrategy()
    observation = entities.EntityFactory.makeObservationEntity(
        "fake", "2014-02-27T15:05:06", 500)
    strategy.storeResult([observation])
    assert(strategy.resultIsAvailable() is True)


def test_repoapi_VCSAPIServiceStrategy_PoppingAResultMeansUnavailability(
        mocker):
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())
    strategy = repoapi.VCSAPIServiceStrategy()
    observation = entities.EntityFactory.makeObservationEntity(
        "fake", "2014-02-27T15:05:06", 500)
    strategy.storeResult([observation])
    strategy.popResult()
    assert(strategy.resultIsAvailable() is False)


def test_repoapi_VCSAPIServiceStrategy_PopReturnsStoredValue(mocker):
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())
    strategy = repoapi.VCSAPIServiceStrategy()
    observation = entities.EntityFactory.makeObservationEntity(
        "fake", "2014-02-27T15:05:06", 500)
    strategy.storeResult([observation])
    result = strategy.popResult()
    assert(result[0] is observation)


def test_repoapi_VCSAPIServiceStrategy_RepeatedStoresAreAnError(mocker):
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())
    strategy = repoapi.VCSAPIServiceStrategy()
    firstObservation = entities.EntityFactory.makeObservationEntity(
        "fake", "2014-02-27T15:05:06", 500)
    secondObservation = entities.EntityFactory.makeObservationEntity(
        "fake", "2014-02-28T15:05:06", 521)

    with pytest.raises(repoapi.StrategyExecutionException) as e_info:
        strategy.storeResult([firstObservation])
        strategy.storeResult([secondObservation])


def test_repoapi_VCSAPIServiceStrategy_StoredResultMustBeIterable(mocker):
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())
    strategy = repoapi.VCSAPIServiceStrategy()
    observation = entities.EntityFactory.makeObservationEntity(
        "fake", "2014-02-27T15:05:06", 500)
    with pytest.raises(repoapi.StrategyExecutionException) as e_info:
        strategy.storeResult(observation)


def test_repoapi_SourceHostAPISession_CallsConnectOnConstruction(mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    repoapi.SourceHostAPISession.connect = mockConnect
    mocker.spy(repoapi.SourceHostAPISession, 'connect')

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    session = repoapi.SourceHostAPISession(token, repository)

    assert(session.connect.call_count == 1)


def test_repoapi_SourceHostAPISession_ConnectionFailureTriggersException(
        mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        raise ConnectionError
    repoapi.SourceHostAPISession.connect = mockConnect

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    with pytest.raises(repoapi.RequestFailureException) as e_info:
        session = repoapi.SourceHostAPISession(token, repository)


def test_repoapi_SourceHostAPISession_executeWithNoStrategiesDoesNothing(
        mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    repoapi.SourceHostAPISession.connect = mockConnect

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    session = repoapi.SourceHostAPISession(token, repository)
    session.executeStrategies()
    results = session.collectResults()
    assert(len(results) == 0)


def test_repoapi_SourceHostAPISession_CanAddStrategy(mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())

    def mockAlgorithm(self, requestHandler):
        pass
    repoapi.VCSAPIServiceStrategy.algorithm = mockAlgorithm

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")
    strategy = repoapi.VCSAPIServiceStrategy()
    session = repoapi.SourceHostAPISession(token, repository)

    assert(session.hasStrategy(strategy) is False)
    session.addStrategy(strategy)
    assert(session.hasStrategy(strategy) is True)


def test_repoapi_SourceHostAPISession_CanRemoveStrategy(mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())

    def mockAlgorithm(self, requestHandler):
        pass
    repoapi.VCSAPIServiceStrategy.algorithm = mockAlgorithm

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")
    strategy = repoapi.VCSAPIServiceStrategy()
    session = repoapi.SourceHostAPISession(token, repository)

    session.addStrategy(strategy)
    session.removeStrategy(strategy)
    assert(session.hasStrategy(strategy) is False)


def test_repoapi_SourceHostAPISession_CallsExecuteOnStrategy(mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    repoapi.SourceHostAPISession.connect = mockConnect

    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())

    def mockAlgorithm(self, requestHandler):
        observation = entities.EntityFactory.makeObservationEntity(
            "fake", "2014-02-27T15:05:06", 500)
        self.storeResult([observation])
    repoapi.VCSAPIServiceStrategy.algorithm = mockAlgorithm
    mocker.spy(repoapi.VCSAPIServiceStrategy, 'algorithm')

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    strategy = repoapi.VCSAPIServiceStrategy()
    session = repoapi.SourceHostAPISession(token, repository)
    session.addStrategy(strategy)
    session.executeStrategies()
    assert(strategy.algorithm.call_count == 1)


def test_repoapi_SourceHostAPISession_CanCollectResultsFromSingleStrategy(
        mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    repoapi.SourceHostAPISession.connect = mockConnect

    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())

    def mockAlgorithm(self, requestHandler):
        observation = entities.EntityFactory.makeObservationEntity(
            "fake", "2014-02-27T15:05:06", 500)
        self.storeResult([observation])
    repoapi.VCSAPIServiceStrategy.algorithm = mockAlgorithm

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    strategy = repoapi.VCSAPIServiceStrategy()
    session = repoapi.SourceHostAPISession(token, repository)
    session.addStrategy(strategy)
    session.executeStrategies()
    results = session.collectResults()
    assert(len(results) == 1)


def test_repoapi_SourceHostAPISession_StrategyErrorPropagatesToSession(mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    repoapi.SourceHostAPISession.connect = mockConnect

    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())

    def mockAlgorithm(self, requestHandler):
        raise RuntimeError
    repoapi.VCSAPIServiceStrategy.algorithm = mockAlgorithm

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    strategy = repoapi.VCSAPIServiceStrategy()
    session = repoapi.SourceHostAPISession(token, repository)
    session.addStrategy(strategy)
    with pytest.raises(repoapi.StrategyExecutionException) as e_info:
        session.executeStrategies()


def test_repoapi_SourceHostAPISession_SupportsMultipleStrategies(mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        pass
    repoapi.SourceHostAPISession.connect = mockConnect

    mocker.patch.multiple(
        repoapi.VCSAPIServiceStrategy,
        __abstractmethods__=set())

    def mockAlgorithm(self, requestHandler):
        observation = entities.EntityFactory.makeObservationEntity(
            "fake", "2014-02-27T15:05:06", 500)
        self.storeResult([observation])
    repoapi.VCSAPIServiceStrategy.algorithm = mockAlgorithm

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    strategyA = repoapi.VCSAPIServiceStrategy()
    mocker.spy(strategyA, 'algorithm')
    strategyB = repoapi.VCSAPIServiceStrategy()
    mocker.spy(strategyB, 'algorithm')
    strategyC = repoapi.VCSAPIServiceStrategy()
    mocker.spy(strategyC, 'algorithm')

    session = repoapi.SourceHostAPISession(token, repository)
    session.addStrategy(strategyA)
    session.addStrategy(strategyB)
    session.addStrategy(strategyC)
    session.executeStrategies()

    assert(strategyA.algorithm.call_count == 1)
    assert(strategyB.algorithm.call_count == 1)
    assert(strategyC.algorithm.call_count == 1)

    results = session.collectResults()
    assert(len(results) == 3)


def test_repoapi_GitHubAPIStargazersStrategy_CanReadStars(mocker):
    mocker.patch.multiple(
        repoapi.SourceHostAPISession,
        __abstractmethods__=set())

    def mockConnect(self, token, repository):
        requestHandler = mocker.Mock()
        requestHandler.stargazers_count = 500
        return requestHandler
    repoapi.SourceHostAPISession.connect = mockConnect

    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")

    stargazersStrategy = repoapi.GitHubAPIStargazersStrategy()
    session = repoapi.SourceHostAPISession(token, repository)
    session.addStrategy(stargazersStrategy)
    session.executeStrategies()
    assert(stargazersStrategy.resultIsAvailable())

    result = stargazersStrategy.popResult()

    assert(result[0].getValue() == 500)
    
def test_repoapi_VCSAPISessionFactory_WillCreateGitHubSessionForGitHubRepository(mocker):
    def mockConnect(self, token, repository):
        pass
    repoapi.GitHubAPISession.connect = mockConnect
    token = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue="ff34885a8624460a855540c6592698d2f1812843")
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="illiad", repositoryName="equine", domainURL="github.com")
    session = repoapi.VCSAPISessionFactory.createAppropriateAPISessionWithStrategies(
        token, repository)
    assert(type(session) == repoapi.GitHubAPISession)
        
