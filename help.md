### Storinator Help
Commands (auth needed):
- /help: Shows this
  
- /pool create <name>: Creates a pool
- /pool recycle <name>: Sends a pool to the recycle bin
- /pool restore <name>: Restores a pool from the recycle bin
- /pool delete <name>: Deletes a pool permanently
- /pool empty-recycle: Empties the recycle bin permanently

- /file store <pool> <local-path-on-machine> [custom-name]...: Stores a new file
- /file retrieve <pool> <file-name> <local-path-on-machine>: Retrieves a file
- /file download <pool> <url> [custom-name]...: Stores a new file from the web
- /file delete <pool> <file>: Permanently deletes a file
- /file yank <pool> <file>: Unlinks a file from the DB, leaving it in the pool

- /list [pool]: Lists files in the system
- /search file <pool> <query>: Searches a file by its filename
- /search name <pool> <query>: Searches a file by its custom name
- /gsearch file <query>: Globally searches a file by its filename
- /gsearch name <query>: Globally searches a file by its custom name