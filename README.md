## Offline PostgreSQL mode

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

```bash
export WIKIGAME_DB_HOST=192.168.1.10
export WIKIGAME_DB_PORT=5432
export WIKIGAME_DB_NAME=wiki_game
export WIKIGAME_DB_USER=wiki_game_user
export WIKIGAME_DB_PASSWORD=strong_password_123
```

### Import Wikimedia dumps

```bash
python -m wikigame.import_cli \
  --page-dump /path/to/ruwiki-latest-page.sql.gz \
  --pagelinks-dump /path/to/ruwiki-latest-pagelinks.sql.gz \
  --truncate
```

### Run offline search

```bash
python -m wikigame.offline_cli \
  --start "Москва" \
  --goal "Санкт-Петербург"
```

### Interactive smoke test

```bash
python -m wikigame.interactive_test
```

## NAS project mode

For Synology NAS, the more reliable setup is:

- store the app code on NAS
- store Wikimedia dumps on NAS
- run PostgreSQL and the importer on NAS

Files added for this flow:

- `Dockerfile`
- `docker-compose.nas.yml`

Expected NAS folders:

- `/volume1/docker/postgres-wikigame/data`
- `/volume1/docker/postgres-wikigame/raw`
- `/volume1/docker/postgres-wikigame/work`
- `/volume1/docker/wiki-game/app`

Suggested deploy flow:

1. Copy this repository to `/volume1/docker/wiki-game/app`
2. Copy `docker-compose.nas.yml` into your Synology project folder as `docker-compose.yml`
3. Start the project in Container Manager
4. Run the `importer` service to load the dumps into PostgreSQL
