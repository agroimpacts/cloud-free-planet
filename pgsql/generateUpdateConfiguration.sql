\pset fieldsep ''
\pset format unaligned
\pset tuples_only
\o updateConfiguration.sql
select '-- ', comment, '
UPDATE configuration SET value = ''', value, ''' WHERE key = ''', key, '''' from configuration order by key;
