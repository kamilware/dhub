# DHub

This is a small NoSQL .ndjson based database (?) that backs up data to GitHub

# Prerequisites

- Python > 3.8
- curl(or winget) + unzip (terminal utils)
- git
- git SSH configured on the machine

# Usage

1. create an repo as you would normally do on GitHub
2. clone the repo wherever you want it to be (note that this directory will be used as dhub base)
3. run

```bash
curl -sL https://raw.githubusercontent.com/kamilware/dhub/master/quickstart.sh -o quickstart.sh && source quickstart.sh && rm quickstart.sh
```

Promise this is not malware:)
What it does:

- save the content of quickstart.sh from my github to a folder
- runs installation and exports
- cleans up

4. You can use

```bash
dhub-cli
```

and

```bash
dhub-server
```

to interact with cli and the server respectively.

# CLI

commands:

```bash
dhub-cli
```

prints usage example

```bash
dhub-cli --list
```

lists tables

```bash
dhub-cli --create <table_name>
```

creates a <table_name> table

```bash
dhub-cli --delete <table_name>
```

deletes <table_name> table

# Server

To be able to access and get records you need to use a REST server.

To start server use:

```bash
dhub-server [optional: --port <port>, example --port 1234]
```

By default server uses port 8000.

Endpoints:

- GET /<table_name> -> array of JSON objects that belong to <table_name>

- POST /<table_name>, body: JSON -> insert a record into <table_name>

That's it. Very simple.

# Backup

By default the repo will push new changes on every:

- create table
- delete table
- new record added

commit message will be in format DD/MM/YYYY HH:MM:SS

example: 17/06/2025 19:49:45
