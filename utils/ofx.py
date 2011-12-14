from sgmllib import SGMLParser

class QFXParser(SGMLParser):
    """
        OFX to dict/list translator
               
    """
    def reset(self):
        """
            Bring self & super to a consistent state
        """
        SGMLParser.reset(self)
        self.myQueue = []
        self.tagData = []
        self.tree = {}
        self.myCurrentTag = ""
       
    def unknown_starttag(self, tag, attrs):        
        self.myQueue.append({tag:None})
        self.myCurrentTag = tag

   
    def handle_data(self,data):
        if(data != None and data.strip() != ""):
            self.myQueue[-1][self.myCurrentTag] = data.strip()


    def unknown_endtag(self, tag):
       
        newNode = {}
        newQueue = []
       
       
        while not tag in self.myQueue[-1]:
            node = self.myQueue.pop()
            for key in node.keys():
                if key in newNode: #the Parent node already has this value, in which case we need to conver the parents container to an list
                    if hasattr(newNode[key], ("append")) == False : #then we need to create an array
                        firstNode = newNode[key]
                        newNode[key] = [firstNode,node[key]]                        
                    else:
                        newNode[key].append(node[key])
                else:
                    newNode.update(node)
           
           
        self.myQueue[-1][tag] = newNode


class OfxHandler:
    
    root_path = "/home/dward/Desktop/Audit/allaccounts.qfx"
    
    
    #class RawNode(object):
    #    __slots__ = ["name","value","children"]
    #    def __init__(self, name):
    #        self.name = name
    #        self.value = None
    #        self.children = None
    #        
    #    def __getstate__(self):
    #        st = {}
    #        st["name"] = self.name
    #        st["value"] = self.value if self.value is not None else None
    #        st["children"] = self.children
    #        return st;
    #        
    #    def __setstate__(self,dic):
    #        self.name, self.value, self.children = dic["name"], dic["value"], dic["children"]
    #        
    #
    #        
    #
    def process(self, body):
        
        #file = open(root_path,"rb");
        #file.seek(0)
        #line = file.readline().strip()
        
        lines = body.splitlines()
        
        linenumber = 0
        
        stats = {}
        buffer = ""

        
        try:
            for i, line in enumerate(lines):
                line = line.strip()
                try:
                    key, value = line.split(":")
                    
                    stats[key] = value                
                except ValueError:
                    linenumber = i
                    raise ValueError
        except:
            pass
            
        buffer = ' '.join(lines[linenumber:])
        
        results = QFXParser()
        results.feed(buffer)
        
        return results.myQueue[0]['ofx']['bankmsgsrsv1']['stmttrnrs']['stmtrs']['banktranlist']['stmttrn']
        