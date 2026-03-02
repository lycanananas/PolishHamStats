# Docker

## Co jest w setupie

- `web`: Django na WSGI (`gunicorn`)
- `db`: `mariadb:11.4`
- bez wewnętrznego `nginx` (reverse proxy ma być na hoście)

## 1) Przeniesienie envów do osobnego pliku

Tak, jest to zrobione.

`docker-compose.yml` używa zmiennych z pliku podawanego przez `--env-file`.

Przygotuj własne pliki na bazie szablonów:

```bash
cp docker/dev.env.example docker/dev.env
cp docker/master.env.example docker/master.env
```

## 2) Dwa środowiska na jednym serwerze (dev + master)

Tak, można uruchomić równolegle.

Warunki:
- różne `COMPOSE_PROJECT_NAME`
- różne porty hosta (`WEB_PORT_PUBLISH`, `DB_PORT_PUBLISH`)

Przykład uruchomienia:

```bash
docker compose --env-file docker/dev.env up --build -d
docker compose --env-file docker/master.env up --build -d
```

Przykład zatrzymania:

```bash
docker compose --env-file docker/dev.env down
docker compose --env-file docker/master.env down
```

Każde środowisko dostaje osobną sieć i osobny wolumen `mysql_data` dzięki innemu `COMPOSE_PROJECT_NAME`.

## 3) CRON

Najprościej i najczyściej: CRON na hoście, który wywołuje komendę w kontenerze `web`.

Przykład (co 6 godzin, środowisko master):

```cron
0 */6 * * * cd /home/USER/path/to/polishhamstats && docker compose --env-file docker/master.env exec -T web python manage.py updatedb >> /var/log/polishhamstats-updatedb-master.log 2>&1
```

Przykład (co 6 godzin, środowisko dev):

```cron
15 */6 * * * cd /home/USER/path/to/polishhamstats && docker compose --env-file docker/dev.env exec -T web python manage.py updatedb >> /var/log/polishhamstats-updatedb-dev.log 2>&1
```

Jeśli środowisko może być czasem wyłączone, lepszy wariant to `run --rm`:

```cron
0 */6 * * * cd /home/USER/path/to/polishhamstats && docker compose --env-file docker/master.env run --rm web python manage.py updatedb >> /var/log/polishhamstats-updatedb-master.log 2>&1
```

## Komendy robocze

Start (master):

```bash
docker compose --env-file docker/master.env up --build -d
```

Logi aplikacji:

```bash
docker compose --env-file docker/master.env logs -f web
```

Migracje ręczne:

```bash
docker compose --env-file docker/master.env exec web python manage.py migrate
```

Shell Django:

```bash
docker compose --env-file docker/master.env exec web python manage.py shell
```
