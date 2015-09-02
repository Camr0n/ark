"""
This extension prints a simple status report at the end of each build.

Author: Darren Mulholland <dmulholland@outlook.ie>
License: Public Domain

"""

from ark import hooks, site


# Register a callback on the 'exit' event hook to print our status report.
@hooks.register('exit')
def print_status_report():
    num_rendered, num_written = site.page_count()
    rendered = "1 page" if num_rendered == 1 else "%s pages" % num_rendered
    written = "1 page" if num_written == 1 else "%s pages" % num_written
    time = site.build_time()
    average = time / (num_rendered or 1)
    status = "%s rendered, %s written in %.2f seconds. %.4f seconds per page."
    print(status % (rendered, written, time, average))
