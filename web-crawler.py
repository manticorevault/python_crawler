from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError
from http.client import InvalidURL
from ssl import _create_unverified_context

class AnchorParser(HTMLParser):
    def __init__(self, baseURL = ""):
        # Parent class constructor
        HTMLParser.__init__(self)

        # Set that will contain all hyperlinks found in a webpage
        self.pageLinks = set()

        # The base url of the webpage to parse
        self.baseURL = baseURL

    def getLinks(self):
        return self.pageLinks

    def handle_starttag(self, tag, attrs):
        # Identify anchor tags
        if tag == "a":
            for(attribute, value) in attrs:
                if attribute == "href":
                    # Form an absolute URL based on the relative URL
                    absoluteURL = urljoin(self.baseURL, value)

                    # Avoid href values that are not http/https
                    if urlparse(absoluteURL).scheme in ["http", "https"]:
                        # Once a new hyperlink is obtained, add it to the set
                        self.pageLinks.add(absoluteURL)    

class MyWebCrawler(object):
    # Basic Web Crawler using Python Standard Libraries

    def __init__(self, url, maxCrawl=10):
        """Args:
            url (str): The starting URL for the web crawler
            maxCrawl (int): Max amount of URLs to crawl
        """
        self.visited = set() # Track all visited URLs
        self.starterURL = url
        self.max = maxCrawl

    def crawl(self):
        """Track the visited URLs in a set in order to crawl through different sites
        Will crawl only as many URLs as declared with "maxCrawl" when instantiating
        """
        urlsToParse = {self.starterURL}

        # While there are still more URLs to parse and we have not exceeded the crawling limit
        while(len(urlsToParse) > 0 and len(self.visited) < self.max):
            # Get the next URL if it has already been visited
            nextURL = urlsToParse.pop()

            # Skip the next URL if it has already been visited
            if nextURL not in self.visited:
                # Mark the next URL as visited
                self.visited.add(nextURL)

                # Call the .parse method to make a web request
                # and parse any new URLs from HTML content
                print("Parsing: {}".format(nextURL))
                urlsToParse |= self.parse(nextURL)

    def parse(self, url):
        """Makes a web request and uses and uses an AnchorParses object to parse the HTML content

        Args: 
            url (str): URL to request and parse

        Returns: 
            set: Absolute URLs found in HTML content   
        """
        try: 
            # Open the URL, read content, decode content
            htmlContent = urlopen(url, context=_create_unverified_context()).read().decode()

            # Initiate the AnchorParser object
            parser = AnchorParser(url)

            # Feed in the HTML content to our AnchorParser object
            parser.feed(htmlContent)

            # The AnchorParser object has a set of absolute URLs that can be returned
            return parser.getLinks()
        
        except(HTTPError, InvalidURL, UnicodeDecodeError):
            # In the case we get any http error, e.g.: 403 error
            print("Failed: {}".format(url))
            return set()
    
    def getVisited(self):
        """Returns the set of URLs visited
        Note: Will include urls that raised HTTPError and InvalidURL

        Returns: 
            set: All URLs visited/parsed
        """
        return self.visited

if __name__ == "__main__":
    # Change the URL below
    crawler = MyWebCrawler("https://CHANGEME.com", maxCrawl=20)
    crawler.crawl()
    print("\nThe following websites were visited:\n{}".format(crawler.getVisited()))