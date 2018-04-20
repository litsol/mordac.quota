from Products.Five.browser import BrowserView
from plone import api
from zope.interface import implementer
# from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from bs4 import BeautifulSoup
import json

import logging
logger = logging.getLogger(__name__)


class DemoView(BrowserView):
    ''' This is a sample browser view with one method. '''

    def get_types(self):
        """Returns a dict with type names and the amount of items
        for this type in the site.
        """
        portal_catalog = api.portal.get_tool('portal_catalog')
        portal_types = api.portal.get_tool('portal_types')
        content_types = portal_types.listContentTypes()
        results = []
        for ct in content_types:
            brains = portal_catalog(portal_type=ct)
            if brains:
                results.append({
                    'type': ct,
                    'qtt': len(brains),
                })
            else:
                logger.info("No elements of type {0}".format(ct))

        return results


class LinkView(BrowserView):
    '''The Link View.
       Returns a list of tuples where the first and second
       member of each tuple are a url and a list of external links
       from that url respectively.
    '''

    def get_links(self):
        ''' '''
        portal_catalog = api.portal.get_tool('portal_catalog')
        # This queries cataloged brain of every content object
        for brain in portal_catalog.searchResults():
            path = brain.getURL()
            links = self._brain_links(brain)
            if links:
                yield (path, links)

    def _brain_links(self, brain):
        ''' Checks Links '''
        urls = []
        try:
            obj = brain.getObject()
            # Call to the content object will render its default view
            # and return it as text
            # Note: this will be slow - it equals to load every page
            # from your Plone site
            rendered = obj()
            soup = BeautifulSoup(rendered, 'lxml')
            elements = soup.find_all('a', {'data-linktype': 'external'})
            urls = [e.get_attribute_list('data-val').pop() for e in elements]
        except:
            pass  # Something may fail here if the content object is broken
        return urls


class LinkJson(LinkView, BrowserView):
    ''' Subclass LinkView and with sole purpose
        to redefine the __call__ special method. '''

    def __call__(self):
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(list(self.get_links()))


@implementer(IPublishTraverse)
class QuotaView(BrowserView):
    ''' This is the quota view '''

# implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        ''' '''
        self.verbose = str(name)
        return self

    def get_objects(self):
        ''' Return a list of dictionaries - one for each object.'''
        results = []
        portal_catalog = api.portal.get_tool('portal_catalog')
        current_path = "/".join(self.context.getPhysicalPath())
        brains = portal_catalog(path=current_path)

        for brain in brains:
            # for i in brain.__record_schema__.items(): print i
            results.append({
                'url': brain.getURL(),
                'size': brain.getObjSize,
                'type': brain.portal_type,
                'state': brain.review_state,
            })
        return results

    def human_format(self, num):
        ''' Render the size in a human readable format. '''
        magnitude = 0
        while num >= 1024:
            magnitude += 1
            num /= 1024.0
        # add more suffixes if you need them
        return '%.0f %sB' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    def getSize(self, brain):
        ''' Return an object's size. '''
        return float(brain.getObjSize.split()[0]) * \
            ((brain.getObjSize.endswith('KB') and 1024) or
             (brain.getObjSize.endswith('MB') and 1024 * 1024) or 1)

    def total(self):
        ''' Tally the total. '''
        portal_catalog = api.portal.get_tool('portal_catalog')
        current_path = "/".join(self.context.getPhysicalPath())
        brains = portal_catalog(path=current_path)
        return self.human_format(
            sum([self.getSize(brain) for brain in brains]))

    def isset(self):
        ''' Ask if verbose attribute is set. '''
        return hasattr(self, 'verbose')

    # def __call__(self):
    #     import pdb; pdb.set_trace()
    #     return self
