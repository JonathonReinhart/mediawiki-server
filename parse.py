import sys
import os, os.path
import SimpleHTTPServer, SocketServer
import xml.etree.ElementTree as ET

import wikimarkup



class MediaWiki(object):

    def __init__(self, filename, default_page):
        tree = ET.parse(filename)
        self.root = tree.getroot()
        self.namespaces = {'mw': 'http://www.mediawiki.org/xml/export-0.6/'}    # TODO: Make dynamic?
        self.default_page = default_page
        
        
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
            
            


class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def _send_404(self, message):
        self.send_response(404)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(message)
        
        
    def _do_GET_root(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        
        def w(s):
            self.wfile.write(s + '\n')
        w('<html>')
        w('<head><title>Simple MediaWikiServer - Index</title></head>')
        w('<body>')
        w('<h1>Simple MediaWikiServer - Index</h1>')
        w('<h2>Loaded Wikis:</h2>')
        w('<ul>')
        for k,v in self.server.wikis.iteritems():
            w('<li><a href="/{0}">{0}</a></li>'.format(k))
        w('</ul>')
        w('</body>')
        w('</html>')

        
    def _do_GET_wiki_page(self, wiki_name, page_title):
        # Get the MediaWiki
        mw = self.server.wikis.get(wiki_name)
        if not mw:
            return self._send_404('Wiki "{0}" not found'.format(wiki_name))
    
        # Try to get the page from the MediaWiki
        if not page_title:
            page_title = mw.default_page
            print 'Using default page: {0}'.format(page_title)
    
        wiki_text = mw.getpage(page_title)
        if not wiki_text:
            return self._send_404('Page "{0}" not found in {1} wiki'.format(page_title, wiki_name))
    
        # Parse it to HTML
        parser = wikimarkup.Parser()
        html = parser.parse(wiki_text)
        
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(html)
        return
        
        
    def do_GET(self):
        # URL should look like:
        # http://localhost:8080/wiki_name/page_title
        
        if self.path == '/':
            return self._do_GET_root()
        
        parts = self.path.split('/', 2)[1:]
        wiki_name = parts[0]
        page_title = None if (len(parts) < 2) else parts[1]
        return self._do_GET_wiki_page(wiki_name, page_title)

        '''
        # serve files, and directory listings by following self.path from
        # current working directory
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        '''
            
        


def main():
    if len(sys.argv) < 3:
        print 'Usage: {0} mediawiki_dump.xml "Default Page"'.format(APPNAME)
        return 1
        
    xml_filename, default_page = sys.argv[1:]
        
    # Load the media wiki
    mw = MediaWiki(xml_filename, default_page)
    
    # Start webserver
    server = SocketServer.TCPServer(('0.0.0.0', 8080), MyRequestHandler)
    server.wikis = {}
    server.wikis['wiki'] = mw
    
    print 'Starting server...'
    server.serve_forever()
    

if __name__ == '__main__':
    APPNAME = os.path.basename(sys.argv[0])
    sys.exit(main())
    
    
