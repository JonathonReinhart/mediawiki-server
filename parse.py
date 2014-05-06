import sys
import os, os.path
import xml.etree.ElementTree as ET


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
    mw = MediaWiki('nes_pages_current.xml')
    
    p = mw.getpage('NES Wiki')
    print p
    open('NES_Wiki.wiki', 'w').write(p)
    

if __name__ == '__main__':
    sys.exit(main())
    
    
