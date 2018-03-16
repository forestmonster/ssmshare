"""Utility functions for SSM orchestration."""

import logging

logger = logging.getLogger(__name__)


def flatten(self, deeplist):
        """Flatten a list.

        :deeplist: List. A hierarchical list, to be flattened.
        :returns: List. The flattened list.

        """
        flattened_list = [item for sublist in deeplist for item in sublist]
        logger.debug("Flattened the list.")
        return flattened_list


def gen_nums():
    """Generate backoff values for polling.

    : returns: Generator.
    """
    n = 1
    while n < 10:
        yield n
        n += 2
