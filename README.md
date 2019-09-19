# MD5 hash based file deduplicator

`dupidup` deduplicates files in given folder by creating their md5 hashes and listing collisions. It's also a console application runing in text mode (curses) that helps you to deal with the duplicates by selecting.

# Structure

`dupidup` the deduplication app
`magicur` Magic Curses library, later maybe to be separated

dupidup \
  --ignore "/media/nas/Photos/.Trash-1000" \
  --ignore "/media/nas/Photos/.dtrash" \
  --debug-log debug.log \
  /media/nas/Photos \
  --debug "localhost:5005:/home/mlinhard/.p2/pool/plugins/org.python.pydev.core_6.4.3.201807050139/pysrc"

