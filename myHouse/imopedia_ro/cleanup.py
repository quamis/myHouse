import base.cleanup

class doCleanup(base.cleanup.Cleanup ):
    def __init__(self, source, db, cache, args):
        super(doCleanup, self).__init__(source, db, cache, args)
        self.tables_cache = ['imopedia_ro']
        self.tables_data = [ 'imopedia_ro_data' ]

    