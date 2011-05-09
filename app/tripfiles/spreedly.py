#Original source from http://bitbucket.org/jespern/pyspreedly/src/tip/spreedly.py

import urllib, xml.dom.minidom
from google.appengine.api import urlfetch
import base64
import logging

__version__ = '0.1'

#Replace these values appropriately
SITE_NAME = 'sitaname'
SPREEDLY_TOKEN = 'thetoken'
SPREEDLY_TEST_PLAN_CODE='code'


def remove_whitespace_nodes(node, unlink=True):
    remove_list = set()
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE and not child.data.strip():
            remove_list.add(child)
        elif child.hasChildNodes():
            remove_whitespace_nodes(child, unlink)

    for node in remove_list:
        node.parentNode.removeChild(node)
        node.unlink()


class XMLReply(object):
    def __init__(self, payload):
        self.error = 'None'
        if payload and payload.status_code==200:
            self.data = payload.content
            self.xml = None
            dom = self.to_xml()
            self.dict = self.to_dict(dom.documentElement)
        else:
            logging.debug('payload'+str(payload))
            self.error = payload.content
            self.error_code = payload.status_code
        
    def to_xml(self):
        if self.xml is None:
            self.xml = xml.dom.minidom.parseString(self.data)
            remove_whitespace_nodes(self.xml.documentElement)
        return self.xml

    def to_dict(self, parent):
        child = parent.firstChild
    
        if not child:
            return None
        elif child.nodeType == child.TEXT_NODE:
            return child.nodeValue
    
        block = dict()
    
        while child is not None:
            if child.nodeType == child.ELEMENT_NODE:
                block[child.tagName] = self.to_dict(child)
    
            child = child.nextSibling
    
        return block

    # -- 

    def __repr__(self):
        return '<XMLReply: data=%d bytes>' % len(self.data)


class Spreedly(object):
    def __init__(self):        
        self.subscriber_url = 'https://spreedly.com/api/v4/%s/subscribers/%s.xml'
        
    def subscriber_details(self, sub_id):
        url = self.subscriber_url % (str(SITE_NAME), str(sub_id))
        logging.debug('Subs url = '+url)
        xml = XMLReply(self.fetch_spreedly_data(url))
        logging.debug("xml.error="+str(xml.error))
        return xml.dict
    
    def fetch_spreedly_data(self, url):
        result = urlfetch.fetch(url,
                            headers={"Authorization": 
                                     "Basic %s" % base64.encodestring(SPREEDLY_TOKEN+":X").replace('\n', '')})
        logging.debug('spreedly data: '+str(result))
        return result
    
    
if __name__ == "__main__":
    sp = Spreedly()
    #setup to run outside dev server
    from google.appengine.api import apiproxy_stub_map, urlfetch_stub
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap() 
    apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())     
    
    #fetch the url
    result = sp.subscriber_details('auserid')
    print result
    