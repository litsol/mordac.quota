from Products.Five.browser import BrowserView
from plone import api
from zope.interface import implementer
# from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

import logging
logger = logging.getLogger(__name__)


class DemoView(BrowserView):
    """ This is a sample browser view with one method.
    """

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


@implementer(IPublishTraverse)
class QuotaView(BrowserView):
    """ This is the quota view """
#     implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        self.verbose = str(name)
        return self

    def get_objects(self):
        results = []
        portal_catalog = api.portal.get_tool('portal_catalog')
        current_path = "/".join(self.context.getPhysicalPath())

        brains = portal_catalog(path=current_path)
        
        for brain in brains:
            #for i in brain.__record_schema__.items(): print i
            results.append({
                'url': brain.getURL(),
                'size': brain.getObjSize,
                'type': brain.portal_type,
                'state': brain.review_state,
                })
        return results

    def human_format(self, num):
        magnitude = 0
        while num >= 1024:
            magnitude += 1
            num /= 1024.0
        # add more suffixes if you need them
        return '%.0f %sB' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    def getSize(self, brain):
        return float(brain.getObjSize.split()[0])*(
            brain.getObjSize.endswith('KB') and 1024
            or brain.getObjSize.endswith('MB') and 1024*1024
            or 1)

    def total(self):
        portal_catalog = api.portal.get_tool('portal_catalog')
        current_path = "/".join(self.context.getPhysicalPath())
        brains = portal_catalog(path=current_path)
        return self.human_format(
            sum([self.getSize(brain) for brain in brains]))

    def isset(self):
        return hasattr(self, 'verbose')

    # def __call__(self):
    #     import pdb; pdb.set_trace()
    #     return self
