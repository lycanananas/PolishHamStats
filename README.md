# polishHamStats

Projekt agreguje dane o znakach i pozwoleniach krótkofalarskich z `amator.uke.gov.pl`, zapisuje je lokalnie i utrzymuje historię widoczności rekordów (`first_seen` / `last_seen`).

## Dla kogo jest ten projekt

- dla krótkofalowców SP,
- dla osób analizujących historię wydań i wygasania pozwoleń,
- dla osób chcących uruchomić własny portal statystyczny na bazie danych UKE.

## Stack

- Python + Django,
- MariaDB (zalecane uruchomienie w Dockerze),
- dane źródłowe pobierane przez komendę `manage.py updatedb`.

## Szybki start (10 minut)

1. Skonfiguruj bazę MariaDB w Dockerze.
2. Skonfiguruj `.env`.
3. Utwórz i aktywuj `venv`.
4. Zainstaluj zależności.
5. Zrób migracje.
6. Uruchom import danych z UKE.
7. Odpal serwer Django.

Szczegóły krok po kroku są poniżej.

---

## 1) Wymagania

- Linux/macOS/WSL,
- Docker,
- Python 3.12+,
- `pip` i `venv`.

## 2) Konfiguracja `.env`

Skopiuj przykład:

```bash
cp example.env .env
```

Ustaw parametry połączenia do DB (ważne: `DB_HOST=127.0.0.1`, nie `localhost`):

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=uke_user
DB_PASS=uke_pass
DB_DBDB=uke
PY_DEBUG=true
PY_HOSTS=127.0.0.1
```

## 3) Baza danych MariaDB w Dockerze

### Pierwsze uruchomienie

```bash
docker pull mariadb:11
docker run -d \
  --name stat-uke-mariadb \
  -e MARIADB_ROOT_PASSWORD=mypass \
  -e MARIADB_DATABASE=uke \
  -e MARIADB_USER=uke_user \
  -e MARIADB_PASSWORD=uke_pass \
  -p 3306:3306 \
  -v stat-uke-mariadb-data:/var/lib/mysql \
  mariadb:11
```

### Start / stop

```bash
docker start stat-uke-mariadb
docker stop stat-uke-mariadb
```

### Szybki test połączenia

```bash
docker exec -it stat-uke-mariadb mariadb -u uke_user -puke_pass -e "SHOW DATABASES;"
```

---

## 4) Python `venv` i zależności

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Migracje i uruchomienie aplikacji

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

Aplikacja lokalnie: `http://127.0.0.1:8000`

---

## 6) Import danych z UKE

Ręczne uruchomienie:

```bash
python3 manage.py updatedb
```

Co robi komenda:

- pobiera CSV z kilku endpointów UKE,
- aktualizuje rekordy znaków i pozwoleń,
- odświeża pola `last_seen` i dane rekordów,
- loguje podsumowanie importu,
- zapisuje raporty JSON w `reports/updatedb/`:
  - `updatedb_YYYYMMDD_HHMMSS.json` — pełny raport zmian (dodane/zmienione/brakujące dziś),
  - `soon_expire_YYYYMMDD_HHMMSS.json` — lista znaków wygasających w 30 dni + delta względem poprzedniego uruchomienia (pole `current` zawiera tylko wpisy bez kolejnego pozwolenia poza oknem 30 dni, `excluded_has_future_license`/`renewed` zawiera wpisy wykluczone z alarmu, czyli znaki już przedłużone),
  - `soon_expire_snapshot.json` — snapshot używany do wyliczania delty.

---

## 7) Cron (import kilka razy dziennie)

Przykład co 6 godzin:

```cron
0 */6 * * * cd /home/USER/path/to/polishhamstats && . .venv/bin/activate && python3 manage.py updatedb >> /var/log/polishhamstats-updatedb.log 2>&1
```

Wersja bezpieczniejsza (blokada równoległych uruchomień):

```cron
0 */6 * * * cd /home/USER/path/to/polishhamstats && flock -n /tmp/polishhamstats-updatedb.lock . .venv/bin/activate && python3 manage.py updatedb >> /var/log/polishhamstats-updatedb.log 2>&1
```

---

## 8) Najczęstsze problemy

### `ModuleNotFoundError: django`

Nieaktywny `venv` lub brak instalacji zależności:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Brak połączenia do DB

- sprawdź czy kontener działa: `docker ps`,
- sprawdź `.env` (`DB_HOST=127.0.0.1`),
- sprawdź port `3306`.

### Błąd importu z UKE

- sprawdź połączenie internetowe,
- sprawdź czy endpointy UKE odpowiadają,
- uruchom import ręcznie i przejrzyj log.

---

## 9) Polecenia developerskie

```bash
python3 manage.py makemigrations app
python3 manage.py migrate
python3 manage.py test
python3 manage.py makemessages -l pl_PL
python3 manage.py compilemessages
```

## Licencja i autorzy

Projekt jest na licencji AGPLv3.

Jeśli uruchamiasz publiczny fork jako usługę sieciową, masz obowiązek udostępnić kod źródłowy zgodnie z AGPLv3.

Autor:

- SQ5FOX (Adrian Grzeca)
