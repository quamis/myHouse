# -*- coding: utf-8 -*-

import sources.base.cleanup as base

class doCleanup(base.Cleanup ):
    def __init__(self, source, db, cache, args):
        super(doCleanup, self).__init__(source, db, cache, args)
        self.tables_cache = ['romino_ro']
        self.tables_data = [ 'romino_ro_data' ]

    