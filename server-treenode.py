import http.server
import socketserver
import pprint
import shelve
import json
from json import JSONEncoder
import sys
import unittest

PORT = 8000

class MyEncoder(JSONEncoder):
    ExcludeList = ['parent']
    
    def default(self, o):
        oc = {}
        for key in o.__dict__.keys():
            if key not in MyEncoder.ExcludeList:
                oc[key] = o.__dict__[key]
                
        return oc   

class Node:
    def __init__(self):
        self.id = 0
        self.name = "Unnamed"
        self.parent = None
        self.children = []
    
    def searchTree(self, chain, create=False):
        if len(chain) == 0:
            return self
            
        id = int(chain.pop(0))
        print("Searching: " + str(id) + " in " + str(len(self.children)) + "C:" + str(create))
        for c in self.children:
            if c.id == id and len(chain) > 0:
                return c.searchTree(chain, create)
            if c.id == id:
                return c
        if create:
            print("Createds some stuffs")
            n = Node()
            n.id = id
            self.add(n)
            return n.searchTree(chain, create)
        
        return None

    def add(self, c):
        c.parent = self
        self.children.append(c)
        return True
        
class Memory:
    root = Node()
    file = "server-treenode.dat"
    
    @staticmethod
    def searchTree(chain, create=False):
        print("Searching: " + str(chain))
        if len(chain) == 0 or (len(chain) == 1 and len(chain[0]) == 0):
            return Memory.root
            
        id = int(chain.pop(0))
        
        if Memory.root.id == id:
            return Memory.root.searchTree(chain, create)
        
        return None

    @staticmethod
    def load():
        try:
            with shelve.open(Memory.file) as db:
                Memory.root = db['root']
                
        except Exception as inst:
            print(str(type(inst)))     # the exception instance
            print(str(inst.args))   # arguments stored in .args
            print(str(inst))    # __str__ allows args to be printed directly
        return True
    
    @staticmethod
    def save():
        with shelve.open(Memory.file) as db:
            db['root'] =  Memory.root
        
        return True
        
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.responded = False
        http.server.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        
        
    def respond(self, content):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(content, 'UTF-8'))
        
        self.responded = True

        
    def do_POST(self):
        try:
            if(self.path.startswith("/nodes/")):
                ar = self.path.split("?")
                pt = ar[0].split("/")
                
                nd = Memory.searchTree(pt[2:], True) # Search and/or create nodes as needed
                if nd:
                    content_len = int(self.headers.get('content-length', 0))
                    post_body = self.rfile.read(content_len)
                    
                    inJson = json.loads(post_body.decode("utf-8", "strict"))
                    
                    for key in inJson.keys():
                        val = inJson[key]
                        #if hasattr(nd, key):
                        setattr(nd, key, val)
                        
                        print("KEY " + key + " VAL " + str(val))
                    
                    Memory.save()
                    
                    self.respond(MyEncoder().encode(nd))
                else:
                    self.send_response(404)
                
            
            if not self.responded:
                # Default response
                http.server.SimpleHTTPRequestHandler.do_POST(self)
        
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]))
            raise
        
    def do_GET(self):    
        try:
            if(self.path.startswith("/nodes/")):
                ar = self.path.split("?")
                pt = ar[0].split("/")
                
                nd = Memory.searchTree(pt[2:])
                if nd:
                    self.respond(MyEncoder().encode(nd))
                else:
                    self.send_response(404)
            
            if not self.responded:
                # Default response
                http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        except:
            print("Unexpected error:" + str(sys.exc_info()[0]))
            raise

            
class TreeNodeTests(unittest.TestCase):        
    def testRootNodeExists(self):
        self.assertEqual(Memory.root.id, 0)
        self.assertTrue(isinstance(Memory.root, Node))

    def testSmallStructure(self):
        n1 = Node()
        n1.id = 1
        n1.name = "First node"
        n2 = Node()
        n2.id = 2
        n2.name = "Second node"
        n3 = Node()
        n3.id = 3
        n3.name = "Third node"
        
        Memory.root.add(n1)
        n2.add(n3)
        Memory.root.add(n2)
        
        self.assertEqual(Memory.searchTree([0, 1]).name, "First node")
        self.assertEqual(Memory.searchTree([0, 2, 3]).name, "Third node")

#if __name__ == '__main__':
#unittest.main()

Memory.load()
            
httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()