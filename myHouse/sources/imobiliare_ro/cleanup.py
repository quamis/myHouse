# -*- coding: utf-8 -*-

import sources.base.cleanup as base

class doCleanup(base.Cleanup ):
    def __init__(self, source, db, cache, args):
        super(doCleanup, self).__init__(source, db, cache, args)
        self.tables_cache = ['imobiliare_ro']
        self.tables_data = [ 'imobiliare_ro_data' ]

    