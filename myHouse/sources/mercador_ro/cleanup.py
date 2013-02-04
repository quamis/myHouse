import base.cleanup

class doCleanup(base.cleanup.Cleanup ):
    def __init__(self, source, db, cache, args):
        super(doCleanup, self).__init__(source, db, cache, args)
        self.tables_cache = ['mercador_ro']
        self.tables_data = [ 'mercador_ro_data' ]
    