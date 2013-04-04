# -*- coding: utf-8 -*-
# schemaversion.py

'''This module upgrades a Python project's database using a
serialized list of SQL statements assigned to version numbers.
Upgrade deltas start from a version number pre-recorded in the
database and end with a given number (usually specified in the
Python script that needs the database updated). This process
allows users to update projects from a repository, for example,
and implicitly update the database schema the first time it is
run.'''