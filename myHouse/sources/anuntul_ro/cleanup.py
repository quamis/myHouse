import base.cleanup

class doCleanup(base.cleanup.Cleanup ):
    def __init__(self, source, db, cache, args):
        super(doCleanup, self).__init__(source, db, cache, args)
        self.tables_cache = ['anuntul_ro']
        self.tables_data = [ 'anuntul_ro_data' ]

    