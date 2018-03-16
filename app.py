"""The App class encapsulates your organization's view of an application."""

import logging
import requests
from itertools import groupby

logger = logging.getLogger(__name__)

# Given an INTERNALTOOL application name, where can we obtain cluster names?
CLUSTERS_URL = (
    'https://INTERNALTOOL/applications/'
    '{application}/clusters')

# Given a clustername, where can we learn its details?
CLUSTERDETAILS_URL = (
    'https://INTERNALTOOL/applications/'
    '{application}/clusters/{account}/{clustername}')


class App(object):
    """An Application, specifically as your organization sees it."""

    def __init__(self, name, account):
        """Instantiate a new App using the bare minimum of information.

        :name: String. The app's name, according to INTERNALTOOL.
        :account: Object (Account). The AWS account to which the app is deployed.

        """
        self.name = name
        self.account = account
        # Try to make fewer requests of your internal tool over the network.
        # - Request a list of clusters, selected by providing the application
        # name.
        # - Request each set of cluster details once, to pull cluster names and
        # server groups.
        # - Derive instances locally from the list of cluster names and server
        # groups.

        # We lazy-load the first two properties because we expect the HTTP REST
        # request to be the slowest piece of App class initialization. The
        # others depend upon the first two.
        self.__clusternames = None
        self.__clusterdetails = None
        self.__servergroups = None
        self.__instances_by_region = None
        logger.debug("App instantiated as \"{}\" in account \"{}\".".format(
            self.name, self.account.name)
        )
        # logger.debug("\"{name}\" contains \"{total}\" instances.".format(
        #     name=self.name,
        #     total=len(self.instances))
        # )

    def __str__(self):
        """Return a user-friendly String representation of App."""
        return("An App named \"{}\".".format(name=self.name))

    @property
    def clusternames(self):
        """Get a list of this application's clusters from internal tooling.

        :returns: List. A list of cluster names.

        """
        if self.__clusternames is None:
            logger.debug("Requesting cluster list.")
            result = requests.get(CLUSTERS_URL.format(
                application=str(self.name))
            )
            self.__clusternames = result.json()[self.account.name]
            logger.debug("Returning clusternames: {}".format(
                self.__clusternames)
            )
        return self.__clusternames

    @property
    def clusterdetails(self):
        """Get cluster details for all clusters.

        :returns: Dict. The key for each sub-Dict is its clusterName.

        """
        if self.__clusterdetails is None:
            details = {}
            for clustername in self.clusternames:
                logger.debug("Requesting cluster details for \"{}\".".format(clustername))
                result = requests.get(CLUSTERDETAILS_URL.format(
                    application=str(self.name),
                    account=self.account.name,
                    clustername=clustername)
                )
                details[clustername] = result.json()
            self.__clusterdetails = details
            logger.debug("Obtained clusterdetails JSON payload.")
        return self.__clusterdetails

    @property
    def servergroups(self):
        """Get servergroups and their active instances.

        :returns: Dict. Instances grouped by servergroup.

        """
        if self.__servergroups is None:
            groups = []
            for cluster in self.clusterdetails.keys():
                logger.debug("Extracting servergroups from clusterdetails payload "
                             "for cluster \"{}\".".format(cluster))
                for element in self.clusterdetails[cluster]['serverGroups']:
                    group = element['name']
                    region = element['region']
                    instances = [instance['instanceId'] for instance in element['instances']]
                    logger.debug("Got group \"{group}\", region \"{region}\", "
                                 "instances \"{instances}\" from "
                                 "element \"{element}\".".format(
                                     group=group,
                                     region=region,
                                     instances=instances,
                                     element=element))
                    groups.append([region, group, instances])
            self.__servergroups = groups
            logger.debug("Returning full servergroups: {}".format(groups))
        return self.__servergroups

    @property
    def instances_by_region(self):
        """Convert a dict of servergroups into a dict of instances grouped by region.

        :returns: Dict. Regions as keys; a list of instances as values.

        """
        if self.__instances_by_region is None:
            groups = self.servergroups
            logger.debug("Converting servergroups into instances grouped by region.")
            by_region = {}
            sortedgroups = sorted(groups, key=lambda x: x[0])  # By region
            for key, value in groupby(sortedgroups, key=lambda x: x[1]):
                by_region[key] = list(value)[0][2]
                # for key, group in groupby(sortedgroups, key=lambda x: x[1]):
                #     for thing in group:
            self.__instances_by_region = by_region
            logger.debug("Returning instances_by_region: {}".format(by_region))
        return self.__instances_by_region
