import os
import random
import string
import StringIO
import unittest
import Missing
from plone import api
from traceback import print_exc
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from AccessControl import getSecurityManager
from mordac.quota.testing import MORDAC_QUOTA_INTEGRATION_TESTING
# from zope.component import getMultiAdapter
from AccessControl import Unauthorized


def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    '''Return a random selection of characters and digits. '''
    return ''.join(random.choice(chars) for x in range(size))


def print_exception():
    ''' Pretty print the exception. '''
    f = StringIO.StringIO()
    print_exc(file=f)
    error_mess = f.getvalue().splitlines()
    print "Exception Occurred :\n"
    for line in error_mess:
        print line
    f.close()


class QuotaViewTestAPI():
    ''' Common Test functionality. '''
    def get_quota_view(self):
        ''' Retrieve the quota view. '''
        return api.content.get_view(
            name='quotaview',
            context=self.portal,
            request=self.request,)

    def create_document(self, docId='doc'):
        ''' Create an empty document. '''
        return api.content.create(
            container=self.portal,
            type='Document',
            id=docId,
            title='A Document')

    def print_to_devnull(self, s):
        bitbucket = open(os.devnull, 'w')
        print >>bitbucket,  s
        bitbucket.close()


class MordacQuotaViewAcquisitionTraversalIntegrationTest(unittest.TestCase,
                                                         QuotaViewTestAPI):
    ''' Test whether the view exists, whether we can acquire it
        and whether we can traverse it by various means. '''
    layer = MORDAC_QUOTA_INTEGRATION_TESTING

    def setUp(self):
        ''' Get the portal and request objects.'''
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_quota_view_exists(self):
        ''' Ascertain whether the view exists. '''
        view = self.get_quota_view()
        self.assertIsNotNone(view)

    def test_quota_browserlayer_interface_is_registered(self):
        ''' Test that IMordacQuotaLayer is registered. '''
        from mordac.quota.interfaces import IMordacQuotaLayer
        from plone.browserlayer import utils
        self.assertIn(IMordacQuotaLayer, utils.registered_layers())

    def test_view_with_browser_layer(self):
        ''' Assert the view returns something. '''
        view = self.get_quota_view()
        view = view.aq_inner.__of__(self.portal)
        self.assertTrue(view())

    def test_view_with_restricted_traverse(self):
        ''' Assert that restricted traversal returns something. '''
        view = self.portal.restrictedTraverse('quotaview')
        self.assertTrue(view())

    def test_view_with_unrestricted_traverse(self):
        ''' Assert that unrestricted traversal returns something. '''
        view = self.portal.unrestrictedTraverse('quotaview')
        self.assertTrue(view())

    def test_view_html_structure(self):
        ''' Assert correct html structure. '''
        import lxml
        view = self.get_quota_view()
        view = view.aq_inner.__of__(self.portal)
        output = lxml.html.fromstring(view())
        self.assertEqual(1, len(output.xpath("/html/body/div")))


class MordacQuotaViewSecurityIntegrationTest(unittest.TestCase,
                                             QuotaViewTestAPI):
    ''' Test that only the Manager role can use the view. '''
    layer = MORDAC_QUOTA_INTEGRATION_TESTING

    def setUp(self):
        ''' Get the portal and request objects.'''
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_quota_member_role(self):
        ''' Apply the quotaview to an empty site;
            The view should not be accessable to non Manager roles. '''
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        user = getSecurityManager().getUser()
        roles = ['Member', 'Authenticated']
        self.assertEqual(user.getRolesInContext(self.portal), roles)
        with self.assertRaises(Unauthorized) as cm:
            self.portal.restrictedTraverse('quotaview')
#        import ipdb; ipdb.set_trace()
        the_exception = cm.exception
        self.print_to_devnull(the_exception)

    def test_quota_anonymous_role(self):
        ''' Apply the quotaview to an empty site;
            The view should not be accessable to an anonymous user. '''
        logout()
        with self.assertRaises(Unauthorized) as cm:
            self.portal.restrictedTraverse('quotaview')
        the_exception = cm.exception
        self.print_to_devnull(the_exception)

    def test_quota_manager_role(self):
        ''' Apply the quotaview to an empty site;
            The view should be accessable to the Manager role. '''
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        user = getSecurityManager().getUser()
        roles = ['Manager', 'Authenticated']
        self.assertEqual(user.getRolesInContext(self.portal), roles)
        self.portal.restrictedTraverse('quotaview')


class MordacQuotaViewIntegrationTest(unittest.TestCase,
                                     QuotaViewTestAPI):
    ''' Test whether the view actually works. '''
    layer = MORDAC_QUOTA_INTEGRATION_TESTING

    def setUp(self):
        ''' Get the portal and request objects.'''
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_quota_empty_site(self):
        ''' Apply the quotaview to an empty site;
            the total returned should be zero bytes. '''
        view = self.get_quota_view()
        self.assertEqual('0 B', view.total())

    def test_quota_empty_document(self):
        ''' Create an empty document at the root of an empty site.
            The total returned should be zero bytes. '''
        view = self.get_quota_view()
        self.create_document()
        self.assertEqual('0 B', view.total())

    def test_quota_2k_document(self):
        ''' Create a document at the root of an empty
            site and populate it with two kilobytes
            of content. The view should confirm the size. '''
        view = self.get_quota_view()
        doc = self.create_document()
        doc.edit(text_format='html', text=random_generator(size=2048))
        self.assertEqual('2 KB', view.total())

    def test_quota_two_2k_document(self):
        ''' Create two documents at the root of an empty
            site and populate them with two kilobytes of
             content each. The view should confirm the size. '''
        view = self.get_quota_view()
        rtext = random_generator(size=2048)
        self.create_document(docId='doc1').edit(text_format='html', text=rtext)
        self.create_document(docId='doc2').edit(text_format='html', text=rtext)
        self.assertEqual('4 KB', view.total())

    def test_quota_objects(self):
        ''' Check whether the get_objects() function returns a list of
            dictionaries, and that the first dictionary contains the
            proper values. '''

        view = self.get_quota_view()
        self.create_document()
        objects = view.get_objects()
        obj = objects.pop()
        self.assertEqual('http://nohost/plone/doc', obj['url'])
        self.assertEqual('Document', obj['type'])
        self.assertEqual('0 KB', obj['size'])
        self.assertEqual(Missing.Value, obj['state'])
# finis
