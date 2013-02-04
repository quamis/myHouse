# -*- coding: utf-8 -*-

class CurrencyConverter(object):
    def __init__(self, ):
        self.rates = {
            'RON' : 1.000,
            'EUR' : 4.500, 
        }
        
    def RONEUR(self, price):
        return (float(price)*self.rates['RON']/self.rates['EUR'])
