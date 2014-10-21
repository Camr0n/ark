"""
This sample plugin prints a simple status report at the end of each build.

"""

from malt import hooks, site


@hooks.register('exit')
def print_status_report():
    pcount = site.page_count()
    btime = site.build_time()
    average = btime / (pcount or 1)
    status = "%s pages rendered in %.2f seconds. %.4f seconds per page."
    print(status % (pcount, btime, average))
