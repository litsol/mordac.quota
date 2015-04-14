# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from mordac.quota.testing import MORDAC_QUOTA_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestInstall(unittest.TestCase):
    """Test installation of mordac.quota into Plone."""

    layer = MORDAC_QUOTA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mordac.quota is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('mordac.quota'))

    def test_uninstall(self):
        """Test if mordac.quota is cleanly uninstalled."""
        self.installer.uninstallProducts(['mordac.quota'])
        self.assertFalse(self.installer.isProductInstalled('mordac.quota'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IMordacQuotaLayer is registered."""
        from mordac.quota.interfaces import IMordacQuotaLayer
        from plone.browserlayer import utils
        self.assertIn(IMordacQuotaLayer, utils.registered_layers())
