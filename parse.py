import sys
import os, os.path
import xml.etree.ElementTree as ET

import wikimarkup

class MediaWiki(object):

    def __init__(self, filename):
        tree = ET.parse(filename)
        self.root = tree.getroot()
        self.namespaces = {'mw': 'http://www.mediawiki.org/xml/export-0.6/'}    # TODO: Make dynamic?
        
        
    def iterpages(self):
        for page in self.root.iterfind('mw:page', namespaces=self.namespaces):
            title = page.find('mw:title', namespaces=self.namespaces).text
            yield title

            
    def getpage(self, title):
        for page in self.root.iterfind('mw:page', namespaces=self.namespaces):
            page_title = page.find('mw:title', namespaces=self.namespaces).text
            if page_title == title: break
        else:
            return None
            
        rev = page.find('mw:revision', namespaces=self.namespaces)
        text = rev.find('mw:text', namespaces=self.namespaces).text
        return text  
            

def main():
    if len(sys.argv) < 3:
        print 'Usage: {0} mediawiki_dump.xml "Default Page"'.format(APPNAME)
        return 1
        
    xml_filename, default_page = sys.argv[1:]
        
    mw = MediaWiki(xml_filename)
    
    w = mw.getpage(default_page)
    
    html = wikimarkup.parse(w)
    
    open(default_page+'.html', 'w').write(html)
    

if __name__ == '__main__':
    APPNAME = os.path.basename(sys.argv[0])
    sys.exit(main())
    
    
