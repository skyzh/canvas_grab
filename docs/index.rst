canvas_grab: synchronize files from Canvas
===========================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   source/modules
   source/canvas_grab.rst
   source/canvas_grab.config.rst
   source/canvas_grab.course_filter.rst
   source/canvas_grab.snapshot.rst

Introduction
============


Canvas Grab is a one-click script to synchronize files from Canvas LMS.
See repository hosted on GitHub
`skyzh/canvas_grab <https://github.com/skyzh/canvas_grab>`_
for installation and usage guide. For how canvas_grab works
internally, you may start with this documentation site.

How Canvas Grab Works
======================

Canvas Grab provides an easy-to-use TUI for tweaking configurations.
All configuration items could be set in command-line, and then be
serialized to ``config.toml``.

After the configuration phase, Canvas Grab starts synchronizing files
from Canvas LMS course-by-course. For each course, Canvas Grab takes
a snapshot of remote files and local files, which contains metadata of
each object (size, name, modified time, etc.). Then, two snapshots will
be fed into transfer planner, which decides what file to transfer and
what file to delete. Finally, Canvas Grab begins the transfer, which
downloads files from Canvas LMS and delete stale local files.

You may refer to ``canvas_grab`` module for more information.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
