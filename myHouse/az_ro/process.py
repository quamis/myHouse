import base.process
import re

class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        c = self.db.selectStart("SELECT `category`, `contact`, `description`, `url`, `price`, `id`  FROM `az_ro_data` WHERE 1 ORDER BY `category` ASC, `description` ASC")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def myTrim(self, regex, text):
        tx = ""
        while tx!=text:
            tx = text
            text = re.sub(regex, "", tx)
        return text
        
    def _processRow(self, row):
        newRow = {}
        newRow['category'] = row[0]
        newRow['description'] = re.sub("[\s]+", " ", row[2])
        newRow['url'] =     row[3]
        newRow['price'] =   row[4]
        newRow['id'] =      row[5]
        
        if row[4]=="":
            return None
        
        if newRow['price']<2:
            newRow['price'] = 0
            
        """
        if re.match("^http", newRow['url']) is None:
            newRow['url'] = "http://az.ro"+newRow['url']
        """
        
        contact = []
        contact.append({ "key":"phone", "value":row[1] })
        newRow['contacts'] = contact
        
        
        print newRow['url'] 
        
        #print newRow
        return newRow
    