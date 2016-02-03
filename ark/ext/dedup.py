# --------------------------------------------------------------------------
# This extension adds a dictionary deduplication filter to Ibis templates.
#
# The filter accepts an input dictionary and returns a copy with duplicate
# values marked as aliases. This filter is intended for internal use in the
# bundled debug theme.
#
# Author: Darren Mulholland <darren@mulholland.xyz>
# License: Public Domain
# --------------------------------------------------------------------------

import ibis


@ibis.filters.register('dedup')
def dedup_dict(indict):
    outdict = {}
    for k in sorted(indict):
        v = indict[k]
        if v is '' or v is None or isinstance(v, int) or isinstance(v, bool):
            outdict[k] = v
            continue
        for outk, outv in outdict.items():
            if v is outv:
                outdict[k] = "<alias of [%s]>" % outk
                break
        if not k in outdict:
            outdict[k] = v
    return outdict
