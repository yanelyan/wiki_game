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
