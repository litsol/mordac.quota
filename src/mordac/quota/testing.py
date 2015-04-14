# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig

import mordac.quota


class MordacQuotaLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        xmlconfig.file(
            'configure.zcml',
            mordac.quota,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'mordac.quota:default')


MORDAC_QUOTA_FIXTURE = MordacQuotaLayer()


MORDAC_QUOTA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MORDAC_QUOTA_FIXTURE,),
    name='MordacQuotaLayer:IntegrationTesting'
)


MORDAC_QUOTA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MORDAC_QUOTA_FIXTURE,),
    name='MordacQuotaLayer:FunctionalTesting'
)


MORDAC_QUOTA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MORDAC_QUOTA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='MordacQuotaLayer:AcceptanceTesting'
)
