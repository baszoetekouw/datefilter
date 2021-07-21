# datefilter
Filter a list of dates according to a filter spec

For example, suppose you make hourly backups, but you don't want to keep older backups.  Then a command like this:
```
cd /backups && ls | datefilter -print0 | xargs -0 rm 
```
will make a decent selection of files to remove.

By default, it will use the following filter specification:
 - keep a file every hour for the past 2 weeks
 - keep a file every day for the past 4 weeks
 - keep a file every week for the past 3 months
 - keep a file every 2 weeks for the past year
