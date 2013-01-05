import base.cleanup

class doCleanup(base.cleanup.Cleanup ):
    def __init__(self, source, db, cache, args):
        super(doCleanup, self).__init__(source, db, cache, args)
        self.tables_cache = ['az_ro']
        self.tables_data = [ 'az_ro_data' ]

    