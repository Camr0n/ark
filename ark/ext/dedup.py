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
def dedup_dict(input):
    output = {}
    for k in sorted(input):
        v = input[k]
        if v is '' or v is None or isinstance(v, int) or isinstance(v, bool):
            output[k] = v
            continue
        for outk, outv in output.items():
            if v is outv:
                output[k] = "<alias of [%s]>" % outk
                break
        if not k in output:
            output[k] = v
    return output
