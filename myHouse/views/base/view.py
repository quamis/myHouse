import locale
import datetime

class baseView(object):
    def __init__(self, args):
        self.args = args
        self.heap = { }
        
    def printHeader(self):
        pass
    
    def printFooter(self, stats):
        pass
    
    def printItem(self, data, data_contacts, data_extracted):
        pass
    
    def format_number(self, number):
        return locale.format("%.*f", (0, number), True)
    
    def format_timestamp(self, timestamp, fmt='%Y-%m-%d'):
        return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)

    def printRow_extraData(self, type, extr, tag, fmt=None, valType='int'):
        if tag in extr and extr[tag]!='':
            val = extr[tag]
            if valType==None:
                val = val
            elif valType=='int':
                val = int(float(val))
            elif valType=='float':
                val = float(val)
            elif valType=='year':
                val = int(float(val))
            elif valType=='location':
                val = unicode(val)
            else:
                raise Exception("invalid 'valType'")
            
            if fmt:
                return fmt % (val)
            else:
                pass
        return None
        