#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Entities:
    The entities and the factory that creates them.
"""
import datetime
from abc import ABC, abstractmethod
from enum import Enum, auto
import re


class Entity(ABC):
    """
    This is the base class for all entities, which encapsulate data
    handled by Repometer components,and some of the business
    logic involved with reading and writing that data to/from the database.
    """

    def __init__(self):
        """
        Parameters
        ----------
        expired:
            This is a flag that an entity subclass can set to
            indicate that the entity is 'expired' and should not be used again.
        """
        self._expired = False

    def isExpired(self):
        return self._expired

    def markAsExpired(self):
        """Set the expired flag to True."""
        self._expired = True

    @abstractmethod
    def accept(self, visitor):
        """
        Used by EntityVisitors. When an entity 'accepts' an EntityVisitor,
        it is expected to make a request back to the EntityVisitor
        that encodes the class of the Entity.
        """
        pass


class EntityVisitor(ABC):
    """
    The abstract base class for entity visitors, which can perform operations
    on and collect data from Entities in a uniform, type-safe way.
    This is primarily used by the response layers, which has to send
    visitors to entities to convert them to a generic representation
    for use by delivery systems.
    """

    @abstractmethod
    def visitCustomer(self, entity):
        pass

    @abstractmethod
    def visitVCSAccount(self, entity):
        pass

    @abstractmethod
    def visitObservation(self, entity):
        pass

    @abstractmethod
    def visitAccessToken(self, entity):
        pass

    @abstractmethod
    def visitRepository(self, entity):
        pass


class EntityFactory:
    """
    An EntityFactory provides an interface for Repometer components to
    construct Entity objects without having to explicitly name or
    import Entity classes.
    """

    @staticmethod
    def makeCustomerEntity(customerName):
        return Customer(customerName=customerName)

    @staticmethod
    def makeVCSAccountEntity(username, domainURL):
        return VCSAccount(username=username, domainURL=domainURL)

    @staticmethod
    def makeObservationEntity(tag, timestamp, value):
        return Observation(tag=tag, timestamp=timestamp, value=value)

    @staticmethod
    def makeAccessTokenEntity(tokenValue):
        return AccessToken(tokenValue=tokenValue)

    @staticmethod
    def makeRepositoryEntity(ownerName, repositoryName, domainURL):
        return Repository(ownerName=ownerName,
                          repositoryName=repositoryName,
                          domainURL=domainURL)


class EntityException(Exception):
    """The base class for entity-related exceptions that protect
    against invalid data and misuse."""
    pass


class EntityDataTypeException(EntityException, TypeError):
    """Raised when an Entity constructor receives inputs of an invalid type."""


class EntityDataValueException(EntityException, ValueError):
    """Raised when an Entity constructor receives inputs of
    the correct type but invalid value."""


class EntityExpiredException(EntityException, ValueError):
    """Raised when an Entity that is considered 'expired'
    is accessed in a way that the Entity does not allow."""


class Customer(Entity):
    """
    Customer represents a repometer user (an individual or team) for
    whom we are tracking one or more repositories. Having an entity
    that represents a customer makes it easier to group together
    accounts across different platforms (like GitHub or GitLab).
    """

    def __init__(self, customerName):
        """
        Parameters
        ----------
        customerName: A unique string identifier indicating the
        name of the individual or team.
        """
        super().__init__()
        if not isinstance(customerName, str):
            raise EntityDataTypeException("Customer expects <customerName>\
                                          to be a string. Received\
                                          {customerNameType}.".format(
                                          customerNameType=type(customerName)))
        elif len(customerName) == 0:
            raise EntityDataValueException("Customer expects <customerName>\
                                           to have non-zero length.")
        else:
            self._customerName = customerName

    def getCustomerName(self):
        return self._customerName

    def accept(self, visitor):
        visitor.visitCustomer(self)


class VCSAccount(Entity):
    """
    An entity that represents the version control platform account
    of a customer for whom we are collecting repository data.

    """

    def __init__(self, username, domainURL):
        """
        Parameters
        ----------
        username:
            A string indicating the name of the customer account.

        domainURL:
            The URL of the domain of the version control
            platform host (e.g. github.com, gitlab.com)
        """
        super().__init__()
        self._username = None
        self._domainURL = None
        if not isinstance(username, str):
            raise EntityDataTypeException(
                "VCSAccount expects <username> to be a string. \
                    Received {usernametype}.".format(
                    usernametype=type(username)))
        elif len(username) == 0:
            raise EntityDataValueException(
                "VCSAccount expects <username> to have non-zero length.")
        else:
            self._username = username

        if not isinstance(domainURL, str):
            raise EntityDataTypeException(
                "VCSAccount expects <domainURL> to be a string. \
                    Received {urltype}.".format(
                    urltype=type(domainURL)))
        elif len(domainURL) == 0:
            raise EntityDataValueException(
                "VCSAccount expects <domainURL> to have non-zero length.")
        else:
            self._domainURL = RepositoryLocation(domainURL)

    def getUsername(self):
        return self._username

    def getDomainURL(self):
        return self._domainURL.getURL()

    def accept(self, visitor):
        visitor.visitVCSAccount(self)


class Repository(Entity):
    """
    An entity that represents a repository owned by a customer's
    account (either directly or as part of an organization).

    """

    def __init__(self, ownerName, repositoryName, domainURL):
        """
        Parameters
        ----------
        ownerName:
            The name of the repository owner, which is either the handle of a
            personal user account or an organization.
        repositoryName:
            The name of the repository itself.
        domainURL:
            The URL of the version control platform
            (e.g. "gitlab.com", "https://bitbucket.org")
        """
        self._ownerName = None
        self._repository = None
        self._domainURL = None
        if not isinstance(ownerName, str):
            raise EntityDataTypeException(
                "Repository expects <ownerName> to be a string. \
                    Received {ownertype}.".format(
                    ownertype=type(ownerName)))
        elif len(ownerName) == 0:
            raise EntityDataValueException(
                "Repository expects <ownerName> to have non-zero length.")
        else:
            self._ownerName = ownerName

        # Maybe change the if statements to try-expect statements -
        # conditional PBD breakpoints
        if not isinstance(repositoryName, str):
            raise EntityDataTypeException(
                "Repository expects <repositoryName> to be a string. \
                    Received {repotype}.".format(
                    repotype=type(repositoryName)))
        elif len(repositoryName) == 0:
            raise EntityDataValueException(
                "Repository expects <repositoryName> to have non-zero length.")
        else:
            self._repositoryName = repositoryName

        # Maybe change the if statements to try-expect statements -
        # conditional PBD breakpoints
        if not isinstance(domainURL, str):
            raise EntityDataTypeException(
                "Repository expects <repositoryName> to be a string. \
                    Received {repotype}.".format(
                    repotype=type(domainURL)))
        elif len(domainURL) == 0:
            raise EntityDataValueException(
                "Repository expects <repositoryName> to have non-zero length.")
        else:
            self._domainURL = RepositoryLocation(domainURL)

    def getOwnerName(self):
        return self._ownerName

    def getRepositoryName(self):
        return self._repositoryName

    def getDomainURL(self):
        return self._domainURL.getURL()

    def isGitHubRepository(self):
        return self._domainURL.getVersionControlPlatform() == RepositoryLocation.VersionControlPlatform.GITHUB

    def isGitlabRepository(self):
        return self._domainURL.getVersionControlPlatform() == RepositoryLocation.VersionControlPlatform.GITLAB
    
    def getCanonicalName(self):
        return "{owner}/{repo}".format(owner=self._ownerName,
                                       repo=self._repositoryName)

    def accept(self, visitor):
        visitor.visitRepository(self)


class AccessToken(Entity):
    """
    An entity responsible for handling a login credential token.
    Credentials can only be accessed once, then the object is considered
    expired. This is done to make sure we don't hold onto users' credentials
    any longer than necessary or reuse them by accident.
    """

    def __init__(self, tokenValue):
        """
        Parameters
        ----------
        tokenValue:
            A string that holds an access token
            (e.g. 'ff34885a8624460a855540c6592698d2f1812843').
        """
        super().__init__()
        if not isinstance(tokenValue, str):
            raise EntityDataTypeException(
                "AccessToken expects <tokenValue> to be a string. \
                    Received {tokentype}.".format(
                    tokentype=type(tokenValue)))
        else:
            self._tokenValue = tokenValue

    def getTokenValue(self):
        return self._tokenValue

    def accept(self, visitor):
        visitor.visitAccessToken(self)


class Observation(Entity):
    """
    A generic entity that captures a unit of data that was collected
    from a repository.
    """

    def __init__(self, tag, timestamp, value):
        """
        Parameters
        ----------
        tag:
            A string that defines the 'kind' of the observation
            (e.g. 'stars', 'forks', 'visitors').
        timestamp:
            Either a datetime object or a timestamp string in ISO 8601 format
            (YYYY-MM-DDTHH:MM:SSZ) that indicates when the data was collected.
            If the timestamp is not a datetime object, it will be converted
            to one by the constructor.
        value:
            The value associated with the observation (e.g. 500).
        """
        super().__init__()
        if not isinstance(tag, str):
            raise EntityDataTypeException(
                "Observation expects <tag> to be a string. \
                    Received {tagtype}.".format(
                    tagtype=type(tag)))
        elif len(tag) == 0:
            raise EntityDataValueException(
                "Observation expects <tag> to have non-zero length.")
        else:
            self._tag = tag
        if isinstance(timestamp, datetime.date):
            self._timestamp = timestamp
        elif isinstance(timestamp, datetime.datetime):
            self._timestamp = timestamp.date()
        elif isinstance(timestamp, str):
            try:
                if "T" in timestamp:
                    # Discard the hours, minutes, seconds, and (optional)
                    # timezone information.
                    timestamp = timestamp.split("T")[0]
                self._timestamp = datetime.datetime.strptime(
                    timestamp, "%Y-%m-%d").date()

            except Exception as datetimeException:
                raise EntityDataValueException(
                    "Observation constructor failed to convert timestamp\
                        ({timestamptext}) into a datetime object.".format(
                        timestamptext=timestamp)) from datetimeException
        else:
            raise EntityDataTypeException(
                "Observation expects <timestamp> to be a datetime object \
                    or a string. Received {timestamptype}.".format(
                    timestamptype=type(timestamp)))
        self._value = value

    def getTag(self):
        return self._tag

    def getTimestamp(self):
        return self._timestamp

    def getValue(self):
        return self._value

    def accept(self, visitor):
        visitor.visitObservation(self)


class RepositoryLocation:
        """
        A convenience object that holds information about a repository
        on which we want to perform our analyses.
        """
        
        class VersionControlPlatform(Enum):
                GITHUB = auto()
                GITLAB = auto()
                BITBUCKET = auto()
                UNKNOWN = auto()
                
        class HostType(Enum):
                OFFICIAL = auto()
                SELFHOSTED = auto()
                UNKNOWN = auto()
        
        def _guessPlatformFromURL(self):
                """
                If the user does not explicitly state the expected platform (or type of platform)
                where the repository is located, we attempt to deduce this based on the URL. 
                """
                regexes = {
                        "GITHUB_OFFICIAL" : re.compile("github.com/?.*?"),
                        "GITLAB_OFFICIAL" : re.compile("gitlab.com/?.*?"),
                        "GITLAB_SELFHOSTED" : re.compile(".*?gitlab.*?"),
                        "BITBUCKET_OFFICIAL" : re.compile("bitbucket.org/.*?"),
                        "BITBUCKET_SELFHOSTED" : re.compile(".*?bitbucket.*?")
                }
                
                if regexes["GITHUB_OFFICIAL"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.GITHUB
                        self._hostType = RepositoryLocation.HostType.OFFICIAL
                elif regexes["GITLAB_OFFICIAL"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.GITLAB
                        self._hostType = RepositoryLocation.HostType.OFFICIAL
                elif regexes["GITLAB_SELFHOSTED"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.GITLAB
                        self._hostType = RepositoryLocation.HostType.SELFHOSTED
                elif regexes["BITBUCKET_OFFICIAL"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.BITBUCKET
                        self._hostType = RepositoryLocation.HostType.OFFICIAL
                elif regexes["BITBUCKET_SELFHOSTED"].search(self._url):
                        self._platform = RepositoryLocation.VersionControlPlatform.BITBUCKET
                        self._hostType = RepositoryLocation.HostType.SELFHOSTED
                else:
                        self._platform = RepositoryLocation.VersionControlPlatform.UNKNOWN
                        self._hostType = RepositoryLocation.HostType.UNKNOWN
                        
        def _guessOwnerAndRepositoryNameFromURL(self):
                """
                If the user does not explicitly state the expected owner and repository name, 
                we attempt to deduce these based on the URL. 
                """
                
                regexes = {
                        "GITHUB_OFFICIAL" : re.compile("^(?:(?:http|https)://)?github.com/([^/]+)/([^/]+)$"),
                        "GITLAB_OFFICIAL" : re.compile("^(?:(?:http|https)://)?gitlab.com/([^/]+)/([^/]+)$"),
                        "GITLAB_SELFHOSTED" : re.compile("^.*?gitlab.*?/([^/]+)/([^/]+)$"),
                        "BITBUCKET_OFFICIAL" : re.compile("^(?:(?:http|https)://)?bitbucket.org/([^/]+)/([^/]+)$"),
                        "BITBUCKET_SELFHOSTED" : re.compile("^.*?bitbucket.*?/([^/]+)/([^/]+)$"),
                        "UNKNOWN" : re.compile("^(?:(?:http|https)://)?.*?/([^/]+)/([^/]+)$")
                }
                
                if self._platform == RepositoryLocation.VersionControlPlatform.GITHUB:
                        regex = regexes["GITHUB_OFFICIAL"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.GITLAB and self._hostType == RepositoryLocation.HostType.OFFICIAL:
                        regex = regexes["GITLAB_OFFICIAL"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.GITLAB and self._hostType == RepositoryLocation.HostType.SELFHOSTED:
                        regex = regexes["GITLAB_SELFHOSTED"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.BITBUCKET and self._hostType == RepositoryLocation.HostType.OFFICIAL:
                        regex = regexes["BITBUCKET_OFFICIAL"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.BITBUCKET and self._hostType == RepositoryLocation.HostType.SELFHOSTED:
                        regex = regexes["BITBUCKET_SELFHOSTED"]
                elif self._platform == RepositoryLocation.VersionControlPlatform.UNKNOWN or self._hostType == RepositoryLocation.HostType.UNKNOWN:
                        regex = regexes["UNKNOWN"]
                else:
                        raise ValueError("In the RepositoryLocation class, _guessOwnerAndRepositoryLocationFromURL \
                        does not know how to parse this platform/hostType: {platform}/{hostType}. \
                        This is likely an implementation error.".format(platform=self._platform,hostType=self._hostType))
                
                match = regex.match(self._url)
                if match is None:
                        self._owner = None
                        self._repositoryName = None
                        
                else:
                        if len(match.group(1)) > 0:
                                self._owner = match.group(1)
                        else:
                                self._owner = None
                        if len(match.group(2)) > 0:
                                self._repositoryName = match.group(2)
                        else:
                                self._repositoryName = None
                
        
        
        def __init__(self,url,expectedPlatform=None,expectedHostType=None,expectedOwner=None,expectedRepositoryName=None):
                """
                Parameters:
                        url: The URL to the repository.
                        expectedPlatform (optional): 
                                        The expected platform where the repository is hosted. 
                                        By default, this is automatically detected, and does not
                                        need to be specified by the user.
                        expectedHostType (optional):
                                        If the user passes an expected platform, they should also
                                        pass an expected host type (e.g. hosted on an official site
                                        or self-hosted on a privately-owned server).
                        expectedOwner (optional):
                                        The organization or individual that is assumed to own the repository.
                                        For example, GitHub URLs are canonically written as
                                        https://github.com/<OWNER>/<REPOSITORYNAME>.
                                        Unless both <expectedOwner> and <expectedRepositoryName> are supplied,
                                        or they will both be overwritten by values estimated based on the URL.
                        expectedRepositoryName (optional):
                                        The name of the repository.
                                        For example, GitHub URLs are canonically written as
                                        https://github.com/<OWNER>/<REPOSITORYNAME>.
                                        Both <expectedOwner> and <expectedRepositoryName> should be supplied,
                                        or they will both be overwritten by values estimated based on the URL.
                                        
                """
                self._url = url
                if expectedPlatform is not None:
                        self._platform = expectedPlatform
                        if expectedHostType is not None:
                                self._hostType = expectedHostType
                        else:
                                self._hostType = RepositoryLocation.HostType.UNKNOWN
                else:
                        self._guessPlatformFromURL()
                if expectedOwner is not None and expectedRepositoryName is not None:
                        self._owner = expectedOwner
                        self._repositoryName = expectedRepositoryName
                else:
                        self._guessOwnerAndRepositoryNameFromURL()
                                
                        
                        
                
        def getURL(self):
                return self._url
                
        def getVersionControlPlatform(self):
                return self._platform
                
        def getVersionControlHostType(self):
                return self._hostType
                
        def getOwner(self):
                return self._owner
                
        def getRepositoryName(self):
                return self._repositoryName
                
        def getCanonicalName(self):
                return "{owner}/{repo}".format(owner=self._owner,repo=self._repositoryName)
                
        def isRecognizable(self):
                return (self._platform != RepositoryLocation.VersionControlPlatform.UNKNOWN and
                        self._hostType != RepositoryLocation.HostType.UNKNOWN and
                        self._owner != None and
                        self._repositoryName != None)