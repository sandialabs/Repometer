#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
RepoAPI:
    Requests data from the repositories
"""

from repometer.core.entities import EntityFactory
from abc import ABC, abstractmethod
import github as pygithub
import gitlab
import datetime
import urllib3


class VCSAPISessionFactory:
    @staticmethod
    def createAppropriateAPISessionWithStrategies(token, repository):
        if repository.isGitHubRepository():
                return VCSAPISessionFactory.createGitHubAPISessionWithStrategies(
                    token, repository)
        elif repository.isGitlabRepository():
                return VCSAPISessionFactory.createGitlabAPISessionWithStrategies(
                    token, repository)
        else:
                raise RequestFailureException("Cannot create VCS platform API session \
                because the URL of the repository is unrecognizable or the platform \
                is not currently supported: {url}".format(
                        url=repository.getDomainURL()
                ))
    @staticmethod
    def createGitHubAPISessionWithStrategies(token, repository):
        stargazers = GitHubAPIStargazersStrategy()
        forks = GitHubAPIForksStrategy()
        clones = GitHubAPIClonesStrategy()
        views = GitHubAPIViewsStrategy()
        session = GitHubAPISession(token, repository)
        session.addStrategy(stargazers)
        session.addStrategy(forks)
        session.addStrategy(clones)
        session.addStrategy(views)
        return session

    @staticmethod
    def createGitlabAPISessionWithStrategies(token, repository):
        forks = GitlabAPIForksStrategy()
        fetches = GitlabAPIFetchesStrategy()
        session = GitlabAPISession(token, repository)
        session.addStrategy(forks)
        session.addStrategy(fetches)
        return session


class VCSAPIException(Exception):
    """The base class for API-session-related exceptions."""
    pass


class RequestFailureException(VCSAPIException, ConnectionError):
    """A wrapper exception for when/if we fail to create a request 
    handler object."""
    pass


class StrategyExecutionException(VCSAPIException):
    """An exception to guard against errors relating to 
    VCSAPIServiceStrategy objects."""


class SourceHostAPISession(ABC):
    """
    An abstract base class that operates a connection/session to a online
    version control system API. Currently, we only support GitHub, but this
    is written in a way that other VCS solutions like GitLab can be supported
    in the future.
    """

    def __init__(self, token, repository):
        """
        Parameters
        ----------
        token:
            An AccessToken entity, used to log in to a VCS API server.
        repository:
            A Repository entity, which describes the repo that we want to
            collect data from.
        """
        self._token = token
        self._repository = repository
        try:
            self._requestHandler = self.connect(token, repository)
        except Exception as requestHandlerException:
            raise RequestFailureException(
                "API session failed to spin up a requestHandler object to\
                connect to {repositoryName} due to an exception:\
                {exceptionType}.".format(
                    repositoryName=self._repository.getCanonicalName(),
                    exceptionType=type(requestHandlerException))) \
                from requestHandlerException

        self._strategyContainer = []

    def hasStrategy(self, strategy):
        """
        Parameters
        ----------
        strategy:
            A VCSAPIServiceStrategy object.
        """
        return strategy in self._strategyContainer

    def addStrategy(self, strategy):
        """
        Parameters
        ----------
        strategy:
            A VCSAPIServiceStrategy object.
        """
        self._strategyContainer.append(strategy)

    def removeStrategy(self, strategy):
        """
        Parameters
        ----------
        strategy:
            A VCSAPIServiceStrategy object.
        """
        self._strategyContainer.remove(strategy)

    @abstractmethod
    def connect(self, token, repository):
        """
        An abstract method that establishes a connection to the VCS API server
        and provides a requester object that VCSAPIServices can use to
        communicate with that server. This method is called automatically by
        the constructor.

        Parameters
        ----------
        token:
            An AccessToken entity, used to log in to a VCS API server.
        repository:
            A Repository entity, which describes the repo that we want to
            collect data from.

        Returns
        -------
        requestHandler:
            An object that holds a connection to a VCS API server, and has an
            interface that allows us to talk to that server. This is,
            for now, provided by a TPL like PyGitHub.
        """
        pass

    def executeStrategies(self):
        """
        Have the session execute each strategy that it has, passing the
        requester object so that those strategies can communicate
        with the VCS API server.
        """
        for index in range(len(self._strategyContainer)):
            strategy = self._strategyContainer[index]
            try:
                strategy.execute(self._requestHandler)

            except Exception as exception:
                raise StrategyExecutionException(
                    "Strategy #{index} ({strategyType}) failed to execute \
                    on {repositoryName} due to an exception\
                    ({exceptionType}).".format(
                        index=index,
                        strategyType=type(strategy).__name__,
                        repositoryName=self._repository.getCanonicalName(),
                        exceptionType=type(exception))) from exception

    def collectResults(self):
        """
        Have the session collect any cached result data produced by strategies
        when they were last executed. This will consume any data they hold.
        """
        results = []
        for strategy in self._strategyContainer:
            if strategy.resultIsAvailable():
                results = results + strategy.popResult()
        return results


class GitHubAPISession(SourceHostAPISession):
    """
    Operates a connection to the GitHub API, allowing Repometer to poll GitHub
    about a particular repository in order to get engagement metrics from it.
    """

    def __init__(self, token, repository):
        super().__init__(token, repository)

    def connect(self, token, repository):
        """
        This method establishes a connection to the GitHub API using
        the PyGitHub library.

        Returns a PyGitHub instance (the requester) that understands manages
        all the interactions with the GitHub API.
        """
        status_forcelist = (500, 502, 504)
        # These status codes are caused by random GitHub errors,
        # according to PyGitHub, and we should retry when we get these.
        totalAllowedRetries = 3
        allowedReadErrorRetries = 3
        allowedConnectionErrorRetries = 3
        retryHandler = urllib3.Retry(
            total=totalAllowedRetries,
            read=allowedReadErrorRetries,
            connect=allowedConnectionErrorRetries,
            status_forcelist=status_forcelist)
        requestHandler = pygithub.Github(
            login_or_token=token.getTokenValue(),
            retry=retryHandler).get_repo(
            repository.getCanonicalName())
        return requestHandler


class GitlabAPISession(SourceHostAPISession):
    def __init__(self, token, repository):
        super().__init__(token, repository)

    def connect(self, token, repository):
        """
        This method establishes a connection to the GitLab API using the
        python-gitlab library.

        Returns a GitLab instance (the requester) that understands manages
        all the interactions with the GitLab API.
        """
        session = gitlab.Gitlab(repository.getDomainURL(),
                                private_token=token.getTokenValue())
        requestHandler = session.projects.get(repository.getCanonicalName())
        return requestHandler
            
        


class VCSAPIServiceStrategy(ABC):
    """
    An abstract base class for collecting data from an online version
    control system API service. SourceHostAPISession performs actions
    on a VCS API using VCSAPIServiceStrategy objects which encapsulate
    the logic for requesting data from the server. This is done so that
    we can easily add or remove data collection features over time.
    """

    def __init__(self):
        self._resultCache = None

    def execute(self, requestHandler):
        """
        Perform whatever action that this VCSAPIServiceStrategy object
        encapsulates.

        Parameters
        ----------
        requestHandler:
            An object that holds a connection to a VCS API server.
            The VCSAPIServiceStrategy knows
            how to communicate with this object.

        """

        try:
            self.algorithm(requestHandler)
        except StrategyExecutionException as strategyException:
            raise strategyException

    @abstractmethod
    def algorithm(self, requestHandler):
        """
        The algorithm that the strategy carries out. This must be defined
        by any subclass that inherits from VCSAPIServiceStrategy.

        Parameters
        ----------
        requestHandler:
            An object that holds a connection to a VCS API server.
            The VCSAPIServiceStrategy knows
            how to communicate with this object.
        """
        pass

    def resultIsAvailable(self):
        return self._resultCache is not None

    def storeResult(self, result):
        """
        Places the result data in the cache of the strategy object,
        indicating that the data is available for consumption.
        """
        if self.resultIsAvailable():
            raise StrategyExecutionException(
                "Strategy attempted to store a result, but a result\
                is already in the cache and would be overwritten.")

        try:
            iterator = iter(result)
        except TypeError:
            raise StrategyExecutionException(
                "Results from Strategies must be iterable.")
        else:
            self._resultCache = result

    def popResult(self):
        """
        Returns whatever data is held by this strategy object. Calling
        this method will clear the cache, so it's only possible
        to call this method once for one instance of data.
        """
        if not self.resultIsAvailable():
            raise StrategyExecutionException(
                "Attempted to collect data from a Strategy that had \
                no data ready.")
        else:
            result = self._resultCache
            self._resultCache = None
            return result


class GitHubAPIStargazersStrategy(VCSAPIServiceStrategy):
    """
    Measures the number of stars on a GitHub repo.
    """

    def __init__(self):
        super().__init__()

    def algorithm(self, requestHandler):
        timestamp = datetime.date.today()
        numberOfStargazers = requestHandler.stargazers_count
        observation = EntityFactory.makeObservationEntity(
            tag="stargazers", timestamp=timestamp, value=numberOfStargazers)
        self.storeResult([observation])


class GitHubAPIForksStrategy(VCSAPIServiceStrategy):
    """
    Measures the number of forks made from a GitHub repo.
    """

    def __init__(self):
        super().__init__()

    def algorithm(self, requestHandler):
        timestamp = datetime.date.today()
        numberOfForks = requestHandler.forks
        observation = EntityFactory.makeObservationEntity(
            tag="forks", timestamp=timestamp, value=numberOfForks)
        self.storeResult([observation])


class GitHubAPIClonesStrategy(VCSAPIServiceStrategy):
    """
    Measures the number of clones made of a GitHub repo in the past 14 days.
    """

    def __init__(self):
        super().__init__()

    def algorithm(self, requestHandler):
        cloneCounts = requestHandler.get_clones_traffic()["clones"]
        observations = []
        for record in cloneCounts:
            dateOfMeasurement = record.timestamp
            totalNumberOfClones = record.count
            numberOfUniqueCloners = record.uniques
            observationTotal = EntityFactory.makeObservationEntity(
                tag="clones_total",
                timestamp=dateOfMeasurement,
                value=totalNumberOfClones)
            observationUnique = EntityFactory.makeObservationEntity(
                tag="clones_unique",
                timestamp=dateOfMeasurement,
                value=numberOfUniqueCloners)
            observations.append(observationTotal)
            observations.append(observationUnique)
        self.storeResult(observations)


class GitHubAPIViewsStrategy(VCSAPIServiceStrategy):
    """
    Measures the number of views of a GitHub repo detected in the past 14 days.
    """

    def __init__(self):
        super().__init__()

    def algorithm(self, requestHandler):
        viewCounts = requestHandler.get_views_traffic()["views"]
        observations = []
        for record in viewCounts:
            dateOfMeasurement = record.timestamp
            totalNumberOfViews = record.count
            numberOfUniqueViewers = record.uniques
            observationTotal = EntityFactory.makeObservationEntity(
                tag="views_total",
                timestamp=dateOfMeasurement, value=totalNumberOfViews)
            observationUnique = EntityFactory.makeObservationEntity(
                tag="views_unique",
                timestamp=dateOfMeasurement, value=numberOfUniqueViewers)
            observations.append(observationTotal)
            observations.append(observationUnique)
        self.storeResult(observations)
        
 
class GitlabAPIStargazersStrategy(VCSAPIServiceStrategy):
    """
    Measures the number of stars on a Gitlab repo.
    """

    def __init__(self):
        super().__init__()

    def algorithm(self, requestHandler):
        """
        TODO: The Gitlab API supports getting the number of
        stars for a project, but this capability is not yet
        available via python-gitlab. We will need a workaround
        for this.    
        """
        pass
        
       
class GitlabAPIForksStrategy(VCSAPIServiceStrategy):
    """
    Measures the number of forks made from a GitHub repo.
    """

    def __init__(self):
        super().__init__()

    def algorithm(self, requestHandler):
        timestamp = datetime.date.today()
        numberOfForks = len([fork for fork in requestHandler.forks.list()])
        observation = EntityFactory.makeObservationEntity(
            tag="forks", timestamp=timestamp, value=numberOfForks)
        self.storeResult([observation])

class GitlabAPIFetchesStrategy(VCSAPIServiceStrategy):
    """
    Measures the number of clones made of a Gitlab repo in the past 30 days.
    As of September 13th, 2020, only HTTP fetches statistics are returned. 
    Fetches statistics includes both clones and pulls count and are HTTP only, 
    SSH fetches are not included.
    """

    def __init__(self):
        super().__init__()

    def algorithm(self, requestHandler):
        statistics = requestHandler.additionalstatistics.get()
        fetchCounts = statistics.fetches
        observations = []
        for record in fetchCounts["days"]:
            dateOfMeasurement = record["date"]
            numberOfFetches = record["count"]
            observationTotal = EntityFactory.makeObservationEntity(
                tag="fetch_count",
                timestamp=dateOfMeasurement,
                value=numberOfFetches)
            observations.append(observationTotal)
        self.storeResult(observations)

