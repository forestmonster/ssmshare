"""The Account class encapsulates the useful features of an AWS account."""

import logging

logger = logging.getLogger(__name__)


class Account(object):
    """An AWS account."""

    def __init__(self, name):
        """Instantiate the AWS account.

        :name: String.
        :returns: Account object.
        """
        self.name = name

        logger.debug(
            "AWS account object (name: \"{}\", number: \"{}\") "
            "created.".format(
                self.name, self.number)
        )

    @property
    def number(self):
        """Provide the corresponding account number, given the account name.

        :accountname: String. One of: 'prod', 'test'.
        :returns: String. Corresponding account number.
        """
        accountname = self.name
        assert (accountname == 'prod' or accountname == 'test'), (
            "This currently only works in the 'prod' or 'test' accounts."
        )
        accountnumber = {
            'prod': '1234567890',
            'test': '0123456789'
        }
        return accountnumber[accountname]
