# A python command line tool for creating files with Postgres DB objects' DDL

You can use it for comparing Postgres databases schemas or for versioning DB schema in external tools like GIT or SVN. 

CLI parameters:
- catalog name for creating files with DDL. Catalog is created if it doesn't exist, all files in this catalog are removed.
- File name fith postgres db schema dump, the result of the command "pg_dump -h <host> -U <user> -d <bd> -s

The schema dump is splitted to files with DDL by object. Constraints, rules, triggers are put inot files with table DDL.
The tool has been tested with dump files from pg_dump version 15.3 and python 3.1

