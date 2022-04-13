#############################################################################
# Copyright 2022 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#############################################################################

"""
Main:
    Main frontend function for Repometer
"""

import argparse
from repometer.core.request import RequestFactory
from repometer.core.interactor import InteractorFactory


def buildParser():
    """
    The top-level parser.

    Values
    -------
    addcustomer      : Requires Customer_Name
    removecustomer   : Requires Customer_Name
    addaccount       : Requires Customer_Name,
                                URL,
                                Username,
                                Access_Token
    removeaccount    : Requires Customer_Name,
                                URL,
                                Username
    addrepository    : Requires URL,
                                Username,
                                Owner_Name,
                                Repository_Name
    removerepository : Requires URL,
                                Username,
                                Owner_Name,
                                Repository_Name
    showdata         : Requires URL,
                                Owner_Name,
                                Repository_Name
    collectdata      : (No subargument)
    status           : (No subargument)

    """
    # The top level parser.
    parser = argparse.ArgumentParser(
        description="The main function for Repometer. \
            Type 'repometer COMMAND --help' to get information \
            about a particular command.")
    # Holds the parsers for all the individual commands.
    subparsers = parser.add_subparsers(title="commands", dest="command")

    parser_addcustomer = subparsers.add_parser(
        'addcustomer', description="Add a customer to the database.")
    parser_addcustomer.add_argument('Customer_Name', type=str)

    parser_removecustomer = subparsers.add_parser(
        'removecustomer', description="Remove a customer to the database.")
    parser_removecustomer.add_argument('Customer_Name', type=str)

    parser_addaccount = subparsers.add_parser(
        'addaccount', description="Add a customer's version \
            control platform account to the database.")
    parser_addaccount.add_argument('Customer_Name', type=str)
    parser_addaccount.add_argument('URL', type=str)
    parser_addaccount.add_argument('Username', type=str)
    parser_addaccount.add_argument('Access_Token', type=str)

    parser_removeaccount = subparsers.add_parser(
        'removeaccount',
        description="Remove a customer's version control platform \
            account from the database.")
    parser_removeaccount.add_argument('Customer_Name', type=str)
    parser_removeaccount.add_argument('URL', type=str)
    parser_removeaccount.add_argument('Username', type=str)

    parser_addrepository = subparsers.add_parser(
        'addrepository',
        description="Associate a repository \
            (https://github.com/<OWNER>/<REPOSITORY>) to\
            a customer's VCS account.")
    parser_addrepository.add_argument('URL', type=str)
    parser_addrepository.add_argument('Username', type=str)
    parser_addrepository.add_argument('Owner_Name', type=str)
    parser_addrepository.add_argument('Repository_Name', type=str)

    parser_removerepository = subparsers.add_parser(
        'removerepository',
        description="Remove a repository association from a customer's\
            VCS account.")
    parser_removerepository.add_argument('URL', type=str)
    parser_removerepository.add_argument('Username', type=str)
    parser_removerepository.add_argument('Owner_Name', type=str)
    parser_removerepository.add_argument('Repository_Name', type=str)

    parser_showdata = subparsers.add_parser(
        'showdata',
        description="Show all data associated with a customer's VCS account,\
            owner, repository combo \
            (https://github.com/<OWNER>/<REPOSITORY>).")
    parser_showdata.add_argument('VCS_Account_Name', type=str)
    parser_showdata.add_argument('Owner_Name', type=str)
    parser_showdata.add_argument('Repository_Name', type=str)

    parser_showdata = subparsers.add_parser(
        'collectdata', description="Collect data for all \
            customer VCS accounts in database.")

    parser_showdata = subparsers.add_parser(
        'status', description="Display Database status information.")

    return parser


def createRequest(arguments):
    """
    Creates the request bases on input values.

    Parameters
    ----------
    arguments : str
        Arguments parsed from the command line.

    Raises
    ------
    RuntimeError
        Raises error if insufficient/incorrect arguments were parsed.

    Returns
    -------
    Request
        Requests call of the appropriate type.

    """
    if arguments.command == "addcustomer":
        return RequestFactory.createAddCustomerRequest(
            customerName=arguments.Customer_Name)
    if arguments.command == "removecustomer":
        return RequestFactory.createRemoveCustomerRequest(
            customerName=arguments.Customer_Name)
    elif arguments.command == "addaccount":
        return RequestFactory.createAddVCSAccountRequest(
            username=arguments.Username,
            tokenValue=arguments.Access_Token,
            customerName=arguments.Customer_Name,
            domainURL=arguments.URL)
    elif arguments.command == "removeaccount":
        return RequestFactory.createRemoveVCSAccountRequest(
            username=arguments.Username,
            customerName=arguments.Customer_Name,
            domainURL=arguments.URL)
    elif arguments.command == "addrepository":
        return RequestFactory.createAddRepositoryRequest(
            username=arguments.Username,
            domainURL=arguments.URL,
            ownerName=arguments.Owner_Name,
            repositoryName=arguments.Repository_Name)
    elif arguments.command == "removerepository":
        return RequestFactory.createRemoveRepositoryRequest(
            username=arguments.Username,
            domainURL=arguments.URL,
            ownerName=arguments.Owner_Name,
            repositoryName=arguments.Repository_Name)
    elif arguments.command == "showdata":
        return RequestFactory.createGetObservationsForRepositoryRequest(
            username=arguments.Username,
            domainURL=arguments.URL,
            ownerName=arguments.Owner_Name,
            repositoryName=arguments.Repository_Name)
    elif arguments.command == "collectdata":
        return RequestFactory.createCollectObservationsRequest()
    elif arguments.command == "status":
        return RequestFactory.createStatusRequest()
    else:
        raise RuntimeError("Missing request type for command.")


def createInteractor():
    """
    Creates the individual InteractorFactories for the orchestrator.

    Returns
    -------
    orchestrator : InteractorFactory

    """
    orchestrator = InteractorFactory.createOrchestrator()
    orchestrator.addChild(InteractorFactory.createAddCustomerInteractor())
    orchestrator.addChild(InteractorFactory.createRemoveCustomerInteractor())
    orchestrator.addChild(InteractorFactory.createAddVCSAccountInteractor())
    orchestrator.addChild(InteractorFactory.createRemoveVCSAccountInteractor())
    orchestrator.addChild(InteractorFactory.createAddRepositoryInteractor())
    orchestrator.addChild(InteractorFactory.createRemoveRepositoryInteractor())
    orchestrator.addChild(
        InteractorFactory.createGetObservationsForRepositoryInteractor())
    orchestrator.addChild(
        InteractorFactory.createCollectObservationsInteractor())
    orchestrator.addChild(
        InteractorFactory.createStatusInteractor())
    return orchestrator


def main():
    """
    Main function - parses the arguments and creates/executes the request

    Returns
    -------
    Success/Failure.

    """
    parser = buildParser()
    arguments = parser.parse_args()
    interactor = createInteractor()
    request = createRequest(arguments)
    response = interactor.execute(request)

    if response.wasSuccessful():
        print("Response: Success ✅")
    else:
        print("Response: Failure ❌")
    print("Message: {message}".format(message=response.getMessage()))
    if response.hasAttachments():
        attachments = response.getAttachments()
        for attachment in attachments:
            print(attachment)
    if not response.wasSuccessful():
        raise RuntimeError("Repometer indicated that one or more failures occurred while processing the request.")


if __name__ == "__main__":
    main()
