imagedir=/home/jbauwens/github/server/kerberos_io/capture
find $imagedir -type f -mtime +31 | xargs -r rm -rf;
