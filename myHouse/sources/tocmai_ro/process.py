# -*- coding: utf-8 -*-

import sources.base.Processor.Processor as Processor
import sources.base.HTML as HTML

import re

import logging, os, tempfile
import sources.base.gather as Gather
import sources.base.imageReader as ImageReader

"""
import resource, fcntl, os
def get_open_fds():
    fds = []
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    for fd in range(0, soft):
        try:
            flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        except IOError:
            continue
        fds.append(fd)
    return fds

def get_file_names_from_file_number(fds):
    names = []
    for fd in fds:
        names.append(os.readlink('/proc/self/fd/%d' % fd))
    return names

print get_file_names_from_file_number(get_open_fds())
"""



class doProcess( Processor.Processor ):
    def getBrowser(self):
        if self.browser is None:
            self.args.UA = ""
            self.browser = Gather.Extractor(None, None, None, None, self.args)
        return self.browser
            
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `tocmai_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def _extractData_apt(self, newRow, row, tree):
        desc = newRow['description']
        newRow = self.processor_helper.extract_floor(newRow, desc, "apt")
        newRow = self.processor_helper.extract_apartmentType(newRow, desc, "apt")
        return newRow
        
    def _processRow(self, row):
        newRow = {}
        newRow['id'] =      row[0]
        newRow['category'] =row[1]
        newRow['url'] =     row[3]

        tree = HTML.HTML(self.db.decompress(row[2]))
        
        location1 =     tree.first(".//*[@id='main']//div/p/b[contains(text(), 'Localitate')]/../text()")
        location2 =     tree.first(".//*[@id='main']//div/p/b[contains(text(), 'Zona')]/../text()")
        if location1 and location2:
            newRow['location'] =      ", ".join((location1, location2))
        elif location1:
            newRow['location'] =      location1
        elif location2:
            newRow['location'] =      location2
            
        
        newRow['price'] =   tree.asPrice(".//*[@id='main']//span[@itemprop= 'price']/text()")
        if not newRow['price']:
            newRow['price']=tree.asPrice(".//*[@id='main']//div[contains(text(), 'Pret')]/text()")
            
        newRow['surface_total'] = tree.asFloat(".//*[@id='main']//div/p/b[contains(text(), 'Suprafata')]/../text()")
        
        newRow['rooms'] =         tree.asInt(".//*[@id='main']//div/p/b[contains(text(), 'camere')]/../text()")
        
        newRow['description'] =   tree.concat(".//*[@id='main']//div[contains(@class, 'item-description')]/text()")
        
        newRow = self.processor_helper.extract_year(newRow, newRow['description'])
        
        if newRow['category']=="case-vile":
            if not re.search("(vila|casa|curte)", newRow['description']) and re.search("apartament", newRow['description']) and re.search("etaj", newRow['description']):
                newRow['category'] = "apt-%d-cam" %(max(2, min(4, newRow['rooms'])))
        
        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow, row, tree)
        else:
            newRow = self._extractData_apt(newRow, row, tree)
        

        # extract phone number, if any        
        contact = []
        img_src = tree.first(".//*[@id='main']//div[contains(@class, 'published_by')]//div[contains(@class, 'phone')]/img/@src")
        if img_src:
            (__, tempFile) = tempfile.mkstemp(os.path.basename(img_src))
            os.close(__)
            
            
            f=open(tempFile, "wb")
            f.write(self.getBrowser().wget(img_src))
            f.close()
            
            reader = ImageReader.ImageReader(tempFile, self.args)
            reader.init()
            p = reader.detect().get().strip()
            reader.destroy()
            
            os.unlink(tempFile)
            
            if re.match("^([0-9]{10})$", p):
                contact.append({ "key":"phone", "value":p })
            else:
                logging.debug("unreconized phone number: '%s'", p)

        newRow['contacts'] = contact            
        newRow = super(doProcess, self).extractData_base(newRow)
        
        return newRow
    