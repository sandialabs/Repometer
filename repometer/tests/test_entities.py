#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

import pytest
import repometer.core.entities as entities
import datetime


def test_EntityVisitor_CanVisitCustomer(mocker):
    mocker.patch.multiple(entities.EntityVisitor, __abstractmethods__=set())
    mocker.spy(entities.EntityVisitor, 'visitCustomer')
    visitor = entities.EntityVisitor()
    account = entities.EntityFactory.makeCustomerEntity("institute")
    account.accept(visitor)
    assert(visitor.visitCustomer.call_count == 1)


def test_EntityVisitor_CanVisitVCSAccount(mocker):
    mocker.patch.multiple(entities.EntityVisitor, __abstractmethods__=set())
    mocker.spy(entities.EntityVisitor, 'visitVCSAccount')
    visitor = entities.EntityVisitor()
    account = entities.EntityFactory.makeVCSAccountEntity("alice",
                                                          "github.com")
    account.accept(visitor)
    assert(visitor.visitVCSAccount.call_count == 1)


def test_EntityVisitor_CanVisitAccessToken(mocker):
    mocker.patch.multiple(entities.EntityVisitor, __abstractmethods__=set())
    mocker.spy(entities.EntityVisitor, 'visitAccessToken')
    visitor = entities.EntityVisitor()
    token = entities.EntityFactory.makeAccessTokenEntity("f751a9b")
    token.accept(visitor)
    assert(visitor.visitAccessToken.call_count == 1)


def test_EntityVisitor_CanVisitRepository(mocker):
    mocker.patch.multiple(entities.EntityVisitor, __abstractmethods__=set())
    mocker.spy(entities.EntityVisitor, 'visitRepository')
    visitor = entities.EntityVisitor()
    repository = entities.EntityFactory.makeRepositoryEntity(
        ownerName="equine", repositoryName="troy", domainURL="github.com")
    repository.accept(visitor)
    assert(visitor.visitRepository.call_count == 1)


def test_EntityVisitor_CanVisitObservation(mocker):
    mocker.patch.multiple(entities.EntityVisitor, __abstractmethods__=set())
    mocker.spy(entities.EntityVisitor, 'visitObservation')
    visitor = entities.EntityVisitor()
    observation = entities.EntityFactory.makeObservationEntity(
        tag="stargazers", timestamp="2014-02-27T15:05:06", value=273)
    observation.accept(visitor)
    assert(visitor.visitObservation.call_count == 1)


def test_Customer_IsConstructibleByFactory():
    customerName = "institute"
    customerEntity = entities.EntityFactory.makeCustomerEntity(
        customerName=customerName)
    assert(isinstance(customerEntity, entities.Customer))


def test_Customer_IsDirectlyConstructible():
    customerName = "institute"
    customerEntity = entities.Customer(customerName)


def test_Customer_StoresCustomerName():
    customerName = "institute"
    customerEntity = entities.Customer(customerName)
    assert(customerEntity.getCustomerName() == customerName)


def test_Customer_HandleMustBeString():
    badCustomerName = 5
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        customerEntity = entities.Customer(badCustomerName)


def test_Customer_CustomerNameMustHaveNonZeroLength():
    customerName = ""
    with pytest.raises(entities.EntityDataValueException) as e_info:
        customerEntity = entities.Customer(customerName)


def test_VCSAccount_IsConstructibleByFactory():
    VCSAccountName = "accountName"
    domainURL = "github.com"
    accountEntity = entities.EntityFactory.makeVCSAccountEntity(
        username=VCSAccountName, domainURL=domainURL)
    assert(isinstance(accountEntity, entities.VCSAccount))


def test_VCSAccount_IsDirectlyConstructible():
    VCSAccountName = "accountName"
    domainURL = "github.com"
    accountEntity = entities.VCSAccount(VCSAccountName, domainURL)


def test_VCSAccount_StoresHandle():
    VCSAccountName = "accountName"
    domainURL = "gitlab.com"
    accountEntity = entities.VCSAccount(VCSAccountName, domainURL)
    assert(accountEntity.getUsername() == VCSAccountName)


def test_VCSAccount_StoresDomainURL():
    VCSAccountName = "accountName"
    domainURL = "gitlab.com"
    accountEntity = entities.VCSAccount(VCSAccountName, domainURL)
    assert(accountEntity.getDomainURL() == domainURL)


def test_VCSAccount_DomainURLMustBeString():
    VCSAccountName = "accountName"
    domainURL = 5
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        accountEntity = entities.VCSAccount(VCSAccountName, domainURL)


def test_VCSAccount_DomainURLMustHaveNonZeroLength():
    accountName = "accountName"
    domainURL = ""
    with pytest.raises(entities.EntityDataValueException) as e_info:
        accountEntity = entities.VCSAccount(accountName, domainURL)


def test_VCSAccount_HandleMustBeString():
    accountName = 5
    domainURL = "github.com"
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        accountEntity = entities.VCSAccount(accountName, domainURL)


def test_VCSAccount_HandleMustHaveNonZeroLength():
    badAccountName = ""
    domainURL = "github.com"
    with pytest.raises(entities.EntityDataValueException) as e_info:
        accountEntity = entities.VCSAccount(badAccountName, domainURL)

def test_Observation_ConstructibleByFactory():
    tag = "stars"
    timestamp = "2014-02-27T15:05:06"
    value = 273
    observationEntity = entities.EntityFactory.makeObservationEntity(
        tag=tag, timestamp=timestamp, value=value)
    assert(isinstance(observationEntity, entities.Observation))


def test_Observation_IsDirectlyConstructible():
    tag = "stars"
    timestamp = "2014-02-27T15:05:06"
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)


def test_Observation_TagMustBeString():
    tag = 5
    timestamp = "2014-02-27T15:05:06"
    value = 273
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        observationEntity = entities.Observation(
            tag=tag, timestamp=timestamp, value=value)


def test_Observation_TagMustHaveNonZeroLength():
    tag = ""
    timestamp = "2014-02-27T15:05:06"
    value = 273
    with pytest.raises(entities.EntityDataValueException) as e_info:
        observationEntity = entities.Observation(
            tag=tag, timestamp=timestamp, value=value)


def test_Observation_StoresTag():
    tag = "stars"
    timestamp = "2014-02-27T15:05:06"
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)
    assert(observationEntity.getTag() == tag)


def test_Observation_StoresValue():
    tag = "stars"
    timestamp = "2014-02-27T15:05:06"
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)
    assert(observationEntity.getValue() == value)


def test_Observation_ValueCanBeNone():
    tag = "stars"
    timestamp = "2014-02-27T15:05:06"
    value = None
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)
    assert(observationEntity.getValue() == value)


def test_Observation_StoresDateTimestampAsDate():
    tag = "stars"
    timestamp = datetime.date(2007, 12, 5)
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)
    assert(isinstance(observationEntity.getTimestamp(), datetime.date))


def test_Observation_StoresDatetimeTimestampAsDate():
    tag = "stars"
    timestamp = datetime.datetime.strptime(
        "2014-02-27T15:05:06", "%Y-%m-%dT%H:%M:%S")
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)
    assert(isinstance(observationEntity.getTimestamp(), datetime.date))


def test_Observation_StoresTimestampStringAsDate():
    tag = "stars"
    timestamp = "2014-02-27T15:05:06"
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)
    assert(isinstance(observationEntity.getTimestamp(), datetime.date))


def test_Observation_TimestampStringSupportsYearMonthDayOnly():
    tag = "stars"
    timestamp = "2014-02-27"
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)


def test_Observation_TimestampStringMustBeInCorrectFormat():
    tag = "stars"
    timestamp = "A long time ago, in a galaxy far, far away"
    value = 273
    with pytest.raises(entities.EntityDataValueException) as e_info:
        observationEntity = entities.Observation(
            tag=tag, timestamp=timestamp, value=value)


def test_Observation_TimestampMustBeDatetimeOrString():
    tag = "stars"
    timestamp = None
    value = 273
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        observationEntity = entities.Observation(
            tag=tag, timestamp=timestamp, value=value)


def test_Observation_TimestampStringSupportsTimezoneExtension():
    tag = "stars"
    timestamp = "2008-07-09T16:13:30+12:00"
    value = 273
    observationEntity = entities.Observation(
        tag=tag, timestamp=timestamp, value=value)


def test_AccessToken_IsConstructibleByFactory():
    tokenValue = "ff34885a8624460a855540c6592698d2f1812843"
    accessTokenEntity = entities.EntityFactory.makeAccessTokenEntity(
        tokenValue=tokenValue)
    assert(isinstance(accessTokenEntity, entities.AccessToken))


def test_AccessToken_IsDirectlyConstructible():
    tokenValue = "ff34885a8624460a855540c6592698d2f1812843"
    accessTokenEntity = entities.AccessToken(tokenValue=tokenValue)


def test_AccessToken_StoresToken():
    tokenValue = "ff34885a8624460a855540c6592698d2f1812843"
    accessTokenEntity = entities.AccessToken(tokenValue=tokenValue)
    assert(accessTokenEntity.getTokenValue() == tokenValue)


def test_AccessToken_TokenValueMustBeString():
    tokenValue = 5
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        accessTokenEntity = entities.AccessToken(tokenValue=tokenValue)


def test_Repository_IsConstructibleByFactory():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "github.com"
    repositoryEntity = entities.EntityFactory.makeRepositoryEntity(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)
    assert(isinstance(repositoryEntity, entities.Repository))


def test_Repository_IsDirectlyConstructible():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "github.com"
    repositoryEntity = entities.Repository(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)


def test_Repository_StoresOwnerName():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "github.com"
    repositoryEntity = entities.Repository(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)
    assert(repositoryEntity.getOwnerName() == ownerName)


def test_Repository_StoresRepositoryName():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "github.com"
    repositoryEntity = entities.Repository(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)
    assert(repositoryEntity.getRepositoryName() == repositoryName)


def test_Repository_StoresDomainURL():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "github.com"
    repositoryEntity = entities.Repository(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)
    assert(repositoryEntity.getDomainURL() == domainURL)


def test_Repository_DomainURLNameMustBeString():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = 5
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        repositoryEntity = entities.Repository(
            ownerName=ownerName,
            repositoryName=repositoryName,
            domainURL=domainURL)


def test_Repository_DomainURLNameMustHaveNonZeroLength():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = ""
    with pytest.raises(entities.EntityDataValueException) as e_info:
        repositoryEntity = entities.Repository(
            ownerName=ownerName,
            repositoryName=repositoryName,
            domainURL=domainURL)


def test_Repository_OwnerNameMustBeString1():
    ownerName = 5
    repositoryName = "equine"
    domainURL = "github.com"
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        repositoryEntity = entities.Repository(
            ownerName=ownerName,
            repositoryName=repositoryName,
            domainURL=domainURL)


def test_Repository_OwnerNameMustBeString2():
    ownerName = "illiad"
    repositoryName = 5
    domainURL = "github.com"
    with pytest.raises(entities.EntityDataTypeException) as e_info:
        repositoryEntity = entities.Repository(
            ownerName=ownerName,
            repositoryName=repositoryName,
            domainURL=domainURL)


def test_Repository_OwnerNameMustHaveNonZeroLength():
    ownerName = ""
    repositoryName = "equine"
    domainURL = "github.com"
    with pytest.raises(entities.EntityDataValueException) as e_info:
        repositoryEntity = entities.Repository(
            ownerName=ownerName,
            repositoryName=repositoryName,
            domainURL=domainURL)


def test_Repository_RepositoryNameMustHaveNonZeroLength():
    ownerName = "illiad"
    repositoryName = ""
    domainURL = "github.com"
    with pytest.raises(entities.EntityDataValueException) as e_info:
        repositoryEntity = entities.Repository(
            ownerName=ownerName,
            repositoryName=repositoryName,
            domainURL=domainURL)


def test_Repository_CanonicalNameIsOwnerPlusRepo():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "github.com"
    repositoryEntity = entities.Repository(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)
    assert(repositoryEntity.getCanonicalName()
           == ownerName + "/" + repositoryName)
           

def test_VCSAccount_RecognizesGitHubDomainURL():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "https://github.com/"
    repositoryEntity = entities.Repository(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)
    assert(repositoryEntity.isGitHubRepository())
    assert(not repositoryEntity.isGitlabRepository())
    
def test_VCSAccount_RecognizesGitlabDomainURL():
    ownerName = "illiad"
    repositoryName = "equine"
    domainURL = "https://gitlab.com/"
    repositoryEntity = entities.Repository(
        ownerName=ownerName,
        repositoryName=repositoryName,
        domainURL=domainURL)
    assert(repositoryEntity.isGitlabRepository())
    assert(not repositoryEntity.isGitHubRepository())



def test_RepositoryLocation_isDirectlyConstructible():
        repositoryLocation = entities.RepositoryLocation(
            url="github.com/owner/repository")
        
def test_RepositoryLocation_canStoreURL():
        url = "arbitrary.edu/repo/name"
        repositoryLocation = entities.RepositoryLocation(
            url="arbitrary.edu/repo/name")
        assert(repositoryLocation.getURL() == url) 
        
def test_RepositoryLocation_canIdentifyGitHubURLs():
        repositoryLocation = entities.RepositoryLocation(
            url="https://github.com/Parallel-NetCDF/PnetCDF")
        assert(repositoryLocation.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.GITHUB)
        assert(repositoryLocation.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.OFFICIAL)
        
def test_RepositoryLocation_canIdentifyGitlabURLs():
        repositoryLocationOfficial = entities.RepositoryLocation(
            url="https://gitlab.com/exaalt/parsplice")
        assert(repositoryLocationOfficial.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocationOfficial.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.OFFICIAL)
        
        repositoryLocationSelfHosted = entities.RepositoryLocation(
            url="https://xgitlab.cels.anl.gov/darshan/darshan")
        assert(repositoryLocationSelfHosted.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocationSelfHosted.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.SELFHOSTED)
        
def test_RepositoryLocation_canIdentifyBitbucketURLs():
        repositoryLocationOfficial = entities.RepositoryLocation(
            url="https://bitbucket.org/berkeleylab/picsar")
        assert(repositoryLocationOfficial.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        assert(repositoryLocationOfficial.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.OFFICIAL)
        
        repositoryLocationSelfHosted = entities.RepositoryLocation(
            url="https://bitbucket.hdfgroup.org/scm/hdffv/hdf5")
        assert(repositoryLocationSelfHosted.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        assert(repositoryLocationSelfHosted.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.SELFHOSTED)
        
def test_RepositoryLocation_unrecognizedURLsAreUnknown():
        repositoryLocationA = entities.RepositoryLocation(
            url="http://flash.uchicago.edu/site/flashcode/coderequest/")
        assert(repositoryLocationA.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.UNKNOWN)
        assert(repositoryLocationA.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.UNKNOWN)
        
        repositoryLocationB = entities.RepositoryLocation(
            url="https://code-int.ornl.gov/exnihilo/Exnihilo")
        assert(repositoryLocationB.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.UNKNOWN)
        assert(repositoryLocationB.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.UNKNOWN)
        
def test_RepositoryLocation_expectedPlatformOverridesActualPlatform():
        repositoryLocationA = entities.RepositoryLocation(
            url="https://code-int.ornl.gov/exnihilo/Exnihilo",
                expectedPlatform=entities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocationA.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.GITLAB)
        
        repositoryLocationB = entities.RepositoryLocation(
            url="https://github.com/Parallel-NetCDF/PnetCDF",
                expectedPlatform=entities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        assert(repositoryLocationB.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.BITBUCKET)
        
def test_RepositoryLocation_providingPlatformButNotHostTypeMakesItUnknown():
        repositoryLocation = entities.RepositoryLocation(
            url="https://code-int.ornl.gov/exnihilo/Exnihilo",
                expectedPlatform=entities.RepositoryLocation.VersionControlPlatform.GITLAB)
        assert(repositoryLocation.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.UNKNOWN)
        
def test_RepositoryLocation_providingBothPlatformAndHostTypeRespectsBothChoices():
        repositoryLocation = entities.RepositoryLocation(
            url="https://code-int.ornl.gov/exnihilo/Exnihilo",
                expectedPlatform=entities.RepositoryLocation.VersionControlPlatform.GITLAB,
                expectedHostType=entities.RepositoryLocation.HostType.SELFHOSTED)
        assert(repositoryLocation.getVersionControlPlatform() ==
               entities.RepositoryLocation.VersionControlPlatform.GITLAB)     
        assert(repositoryLocation.getVersionControlHostType() ==
               entities.RepositoryLocation.HostType.SELFHOSTED)
        
def test_RepositoryLocation_providingBothOwnerAndRepositoryNameRespectsBothChoices():
        repositoryLocation = entities.RepositoryLocation(
            url="https://bitbucket.hdfgroup.org/scm/hdffv/hdf5",
                expectedOwner="hdffv",
                expectedRepositoryName="hdf5")
        assert(repositoryLocation.getOwner() == "hdffv")     
        assert(repositoryLocation.getRepositoryName() == "hdf5")
        
def test_RepositoryLocation_canParseOwnerAndNameOfGitHubRepository():
        repositoryLocation = entities.RepositoryLocation(
            url="https://github.com/Parallel-NetCDF/PnetCDF")
        assert(repositoryLocation.getOwner() == "Parallel-NetCDF")     
        assert(repositoryLocation.getRepositoryName() == "PnetCDF")
        
def test_RepositoryLocation_canParseOwnerAndNameOfOfficialGitlabRepository():
        repositoryLocation = entities.RepositoryLocation(
            url="https://gitlab.com/exaalt/parsplice")
        assert(repositoryLocation.getOwner() == "exaalt")     
        assert(repositoryLocation.getRepositoryName() == "parsplice")
        
def test_RepositoryLocation_canParseOwnerAndNameOfSelfHostedGitlabRepository():
        repositoryLocation = entities.RepositoryLocation(
            url="https://xgitlab.cels.anl.gov/darshan/darshancode")
        assert(repositoryLocation.getOwner() == "darshan")     
        assert(repositoryLocation.getRepositoryName() == "darshancode")
        
def test_RepositoryLocation_canParseOwnerAndNameOfOfficialBitbucketRepository():
        repositoryLocation = entities.RepositoryLocation(
            url="https://bitbucket.org/berkeleylab/picsar")
        assert(repositoryLocation.getOwner() == "berkeleylab")     
        assert(repositoryLocation.getRepositoryName() == "picsar")
        
def test_RepositoryLocation_canParseOwnerAndNameOfSelfHostedBitbucketRepository():
        repositoryLocation = entities.RepositoryLocation(
            url="bitbucket.snl.gov/project/repo")
        assert(repositoryLocation.getOwner() == "project")     
        assert(repositoryLocation.getRepositoryName() == "repo")
        
def test_RepositoryLocation_canParseOwnerAndNameOfUnknownRepository():
        repositoryLocation = entities.RepositoryLocation(
            url="https://code-int.ornl.gov/exnihilo/Exnihilo")
        assert(repositoryLocation.getOwner() == "exnihilo")     
        assert(repositoryLocation.getRepositoryName() == "Exnihilo")
        
def test_RepositoryLocation_AllOrNothingForPartialMatchesOnOwnerAndRepo():
        repositoryLocationA = entities.RepositoryLocation(
            url="https://github.com/Parallel-NetCDF/")
        assert(repositoryLocationA.getOwner() == None)
        assert(repositoryLocationA.getRepositoryName() == None)

        repositoryLocationB = entities.RepositoryLocation(
            url="https://gitlab.com/exaalt")
        assert(repositoryLocationB.getOwner() == None)
        assert(repositoryLocationB.getRepositoryName() == None)

        repositoryLocationC = entities.RepositoryLocation(
            url="https://xgitlab.cels.anl.gov/darshan/")
        assert(repositoryLocationC.getOwner() == None)
        assert(repositoryLocationC.getRepositoryName() == None)

        repositoryLocationD = entities.RepositoryLocation(
            url="https://bitbucket.org/berkeleylab/")
        assert(repositoryLocationD.getOwner() == None)
        assert(repositoryLocationD.getRepositoryName() == None)

        repositoryLocationE = entities.RepositoryLocation(
            url="https://bitbucket.hdfgroup.org/hdffv/")
        assert(repositoryLocationE.getOwner() == None)
        assert(repositoryLocationE.getRepositoryName() == None)

        repositoryLocationE = entities.RepositoryLocation(
            url="https://code-int.ornl.gov/")
        assert(repositoryLocationE.getOwner() == None)
        assert(repositoryLocationE.getRepositoryName() == None)
