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

POSVERSION = 0
POSUP = 1
POSDOWN = 2

TABLE = 'schemaversion'
FIELD = 'version'

MYSQL_DEFAULT_PORT = 3306

def mysql_update(new_version, history, host, database, user, password,
                 port=MYSQL_DEFAULT_PORT, charset=None):
    '''
    Takes a version to proceed to; a list of tuples of database
    update history; and a database host, db name, username,
    password, and optionally a port or charset.

    Each tuple in the history list has 3 elements:
    0: The version number,
    1: The SQL to run going forward into this version, and
    2: The SQL to run going backward from this version.

    Versioning is performed as version number increases, regardless
    of given list order. You should include the base version as the
    first tuple in the list and put None in place of the SQL
    statements.
    '''
    import MySQLdb
    
    global POSVERSION, POSUP, POSDOWN, TABLE, FIELD
    
    # Sort the history by version number:
    history.sort()
    
    # Get the current version number in the database:
    conn = MySQLdb.connect(host=host, user=user, passwd=password,
                           db=database, port=port)
    cursor = conn.cursor()
    cursor.execute('SELECT ' + FIELD + ' FROM ' + TABLE)
    current_version = cursor.fetchone()[0]
    
    # Make sure the requested version is in the history
    if new_version not in [i[POSVERSION] for i in history]:
        raise InvalidVersion(str(new_version)
                             + ' does not refer to a valid version')
    
    # Make sure the current version is in the history:
    if current_version not in [i[POSVERSION] for i in history]:
        raise InvalidVersion('Current database version ' + str(current_version)
                             + ' does not refer to a valid version')
    
    # Starting at the database's current version, upgrade through
    # versions up to and including the given version:
    history_iterator = history.__iter__()
    has_more_versions = True
    #TODO: Make this work backward as well as forward:
    while has_more_versions:
        next = history_iterator.next()
        # If this is the target version, end after this round:
        if next[POSVERSION] == new_version:
            has_more_versions = False
        if next[POSVERSION] > current_version:
            # Run this version's change on the database:
            cursor = conn.cursor()
            cursor.execute(next[POSUP])
            # Update the version number:
            cursor = conn.cursor()
            cursor.execute('UPDATE ' + TABLE + ' SET ' + FIELD + '='
                           + str(next[POSVERSION]))

class InvalidVersion(ValueError):
    '''Raise this if a user specifies a nonexistent version.'''
    pass