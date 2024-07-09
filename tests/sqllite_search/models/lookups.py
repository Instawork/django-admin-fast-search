from django.db import models


class Search(models.Lookup):
    lookup_name = "search"

    def as_sqlite(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s = %s" % (lhs, rhs), params


models.CharField.register_lookup(Search)
models.TextField.register_lookup(Search)
