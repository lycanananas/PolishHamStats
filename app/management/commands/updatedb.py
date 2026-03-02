import datetime
import csv
import io
import json
from pathlib import Path

import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from app.models import Callsign, License


class Command(BaseCommand):
    help = "Updates database from new date from UKE"

    API_URL = {
        "INDIVIDUALS": "https://amator.uke.gov.pl/pl/individuals/export.csv",
        "CLUBS": "https://amator.uke.gov.pl/pl/clubs/export.csv",
        "DEVICES_INDIVIDUALS": "https://amator.uke.gov.pl/pl/individual_devices/export.csv",
        "DEVICES_CLUBS": "https://amator.uke.gov.pl/pl/club_devices/export.csv",
    }
    API_URL_CHARSET = "Windows-1250"
    API_DELIMITER = ";"
    HTTP_TIMEOUT = 30
    DATE_FORMAT = "%Y-%m-%d"
    SOON_EXPIRE_DAYS = 30
    CATEGORY_MAP = {
        "Kategoria1": License.Category.KATEGORIA_1,
        "Kategoria3": License.Category.KATEGORIA_3,
        "Kategoria5": License.Category.KATEGORIA_5,
        "Dodatkowe": License.Category.KATEGORIA_DODATKOWA,
    }

    TYPE_MAP = {
        "INDIVIDUALS": License.Type.INDIVIDUAL,
        "CLUBS": License.Type.CLUB,
        "DEVICES_INDIVIDUALS": License.Type.INDIVIDUAL_DEVICE,
        "DEVICES_CLUBS": License.Type.CLUB_DEVICE,
    }

    def _reports_dir(self):
        path = Path(settings.BASE_DIR) / "reports" / "updatedb"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _save_json(self, path, payload):
        with path.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, ensure_ascii=False, indent=2)

    def _load_json_or_default(self, path, default_payload):
        if not path.exists():
            return default_payload
        try:
            with path.open("r", encoding="utf-8") as file_handle:
                return json.load(file_handle)
        except (OSError, json.JSONDecodeError):
            return default_payload

    def _get_value(self, row, index):
        if index >= len(row):
            return ""
        return row[index].strip()

    def _parse_int(self, value, default):
        if value == "":
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def _parse_float(self, value, default):
        if value == "":
            return default
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return default

    def _parse_date(self, value):
        try:
            return datetime.datetime.strptime(value, self.DATE_FORMAT).date()
        except ValueError:
            return None

    def _download_csv_rows(self, dataset_type, url):
        self.stdout.write(f"Pobieranie CSV: {dataset_type}")
        try:
            response = requests.get(url, timeout=self.HTTP_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as error:
            raise CommandError(f"Nie można pobrać CSV dla {dataset_type}: {error}") from error

        decoded = response.content.decode(self.API_URL_CHARSET, errors="replace")
        reader = csv.reader(io.StringIO(decoded), delimiter=self.API_DELIMITER)
        return list(reader)

    def _build_soon_expire_current(self, today):
        end_date = today + datetime.timedelta(days=self.SOON_EXPIRE_DAYS)
        soon_expire_licenses = (
            License.objects.filter(expiration_date__gte=today, expiration_date__lte=end_date)
            .select_related("assigned_callsign")
            .order_by("expiration_date", "assigned_callsign__callsign", "license")
        )

        future_licenses = (
            License.objects.filter(expiration_date__gt=end_date)
            .select_related("assigned_callsign")
            .order_by("assigned_callsign__callsign", "expiration_date", "license")
        )

        future_by_callsign = {}
        for license_obj in future_licenses:
            callsign_value = license_obj.assigned_callsign.callsign
            if callsign_value in future_by_callsign:
                continue
            future_by_callsign[callsign_value] = license_obj

        earliest_by_callsign = {}
        for license_obj in soon_expire_licenses:
            callsign_value = license_obj.assigned_callsign.callsign
            if callsign_value in earliest_by_callsign:
                continue
            days_left = (license_obj.expiration_date - today).days
            future_license_obj = future_by_callsign.get(callsign_value)
            future_license = None
            if future_license_obj is not None:
                future_license = {
                    "license": future_license_obj.license,
                    "expiration_date": future_license_obj.expiration_date.isoformat(),
                    "days_left": (future_license_obj.expiration_date - today).days,
                }
            earliest_by_callsign[callsign_value] = {
                "callsign": callsign_value,
                "license": license_obj.license,
                "expiration_date": license_obj.expiration_date.isoformat(),
                "days_left": days_left,
                "has_future_license": future_license is not None,
                "renewed": future_license is not None,
                "future_license": future_license,
                "alert_eligible": future_license is None,
            }

        return earliest_by_callsign

    def _build_soon_expire_report(self, today, run_token):
        reports_dir = self._reports_dir()
        snapshot_path = reports_dir / "soon_expire_snapshot.json"
        report_path = reports_dir / f"soon_expire_{run_token}.json"

        previous_snapshot = self._load_json_or_default(snapshot_path, {"callsigns": {}})
        previous_map = previous_snapshot.get("callsigns", {})
        if not isinstance(previous_map, dict):
            previous_map = {}

        current_map_all = self._build_soon_expire_current(today)
        current_map = {
            callsign: data
            for callsign, data in current_map_all.items()
            if data.get("alert_eligible", False)
        }
        excluded_map = {
            callsign: data
            for callsign, data in current_map_all.items()
            if not data.get("alert_eligible", False)
        }
        renewed_callsigns = sorted(excluded_map.keys())

        previous_set = set(previous_map.keys())
        current_set = set(current_map.keys())

        added_callsigns = sorted(current_set - previous_set)
        removed_callsigns = sorted(previous_set - current_set)
        unchanged_callsigns = sorted(current_set & previous_set)

        report_payload = {
            "generated_at": timezone.now().isoformat(),
            "today": today.isoformat(),
            "window_days": self.SOON_EXPIRE_DAYS,
            "counts": {
                "current": len(current_set),
                "current_all": len(current_map_all),
                "excluded_has_future_license": len(excluded_map),
                "renewed": len(renewed_callsigns),
                "added": len(added_callsigns),
                "removed": len(removed_callsigns),
                "unchanged": len(unchanged_callsigns),
            },
            "added": [current_map[callsign] for callsign in added_callsigns],
            "removed": [
                {
                    "callsign": callsign,
                    "previous": previous_map[callsign],
                }
                for callsign in removed_callsigns
            ],
            "unchanged": [current_map[callsign] for callsign in unchanged_callsigns],
            "current": [current_map[callsign] for callsign in sorted(current_set)],
            "current_all": [current_map_all[callsign] for callsign in sorted(current_map_all.keys())],
            "excluded_has_future_license": [
                excluded_map[callsign] for callsign in sorted(excluded_map.keys())
            ],
            "renewed": [excluded_map[callsign] for callsign in renewed_callsigns],
            "mailing": {
                "expiring_alerts": [current_map[callsign] for callsign in sorted(current_set)],
                "renewed": [excluded_map[callsign] for callsign in renewed_callsigns],
            },
        }

        snapshot_payload = {
            "generated_at": timezone.now().isoformat(),
            "today": today.isoformat(),
            "window_days": self.SOON_EXPIRE_DAYS,
            "callsigns": current_map,
            "all_callsigns": current_map_all,
        }

        self._save_json(report_path, report_payload)
        self._save_json(snapshot_path, snapshot_payload)

        return {
            "report_path": report_path,
            "snapshot_path": snapshot_path,
            "counts": report_payload["counts"],
        }

    def _build_license_data(self, dataset_type, row, today):
        license_number = self._get_value(row, 0)
        expiration_raw = self._get_value(row, 1)
        callsign = self._get_value(row, 2).upper()
        category_raw = self._get_value(row, 3)
        power = self._parse_int(self._get_value(row, 4), -1)

        expiration_date = self._parse_date(expiration_raw)
        if not license_number or not callsign or expiration_date is None:
            return None

        data = {
            "license": license_number,
            "category": self.CATEGORY_MAP.get(category_raw, License.Category.INVALID),
            "expiration_date": expiration_date,
            "power": power,
            "type": self.TYPE_MAP.get(dataset_type, License.Type.INVALID),
            "station_location": None,
            "applicant_name": None,
            "applicant_city": None,
            "applicant_street": None,
            "applicant_house": None,
            "applicant_number": None,
            "enduser_name": None,
            "enduser_city": None,
            "enduser_street": None,
            "enduser_house": None,
            "enduser_number": None,
            "station_city": None,
            "station_street": None,
            "station_house": None,
            "station_number": None,
            "lat": 0.0,
            "lng": 0.0,
            "name_type_station": None,
            "emission": None,
            "input_frequency": None,
            "output_frequency": None,
            "last_seen": today,
        }

        if dataset_type == "INDIVIDUALS":
            data["station_location"] = self._get_value(row, 5) or None

        if dataset_type == "DEVICES_INDIVIDUALS":
            data["name_type_station"] = self._get_value(row, 5) or None
            data["emission"] = self._get_value(row, 6) or None
            data["input_frequency"] = self._get_value(row, 7) or None
            data["output_frequency"] = self._get_value(row, 8) or None
            data["station_location"] = self._get_value(row, 9) or None

        if dataset_type == "DEVICES_CLUBS":
            data["name_type_station"] = self._get_value(row, 5) or None
            data["emission"] = self._get_value(row, 6) or None
            data["input_frequency"] = self._get_value(row, 7) or None
            data["output_frequency"] = self._get_value(row, 8) or None

        if dataset_type in {"CLUBS", "DEVICES_CLUBS"}:
            offset = 4 if dataset_type == "DEVICES_CLUBS" else 0
            data["applicant_name"] = self._get_value(row, 5 + offset) or None
            data["applicant_city"] = self._get_value(row, 6 + offset) or None
            data["applicant_street"] = self._get_value(row, 7 + offset) or None
            data["applicant_house"] = self._get_value(row, 8 + offset) or None
            data["applicant_number"] = self._get_value(row, 9 + offset) or None
            data["enduser_name"] = self._get_value(row, 10 + offset) or None
            data["enduser_city"] = self._get_value(row, 11 + offset) or None
            data["enduser_street"] = self._get_value(row, 12 + offset) or None
            data["enduser_house"] = self._get_value(row, 13 + offset) or None
            data["enduser_number"] = self._get_value(row, 14 + offset) or None
            data["station_city"] = self._get_value(row, 15 + offset) or None
            data["station_street"] = self._get_value(row, 16 + offset) or None
            data["station_house"] = self._get_value(row, 17 + offset) or None
            data["station_number"] = self._get_value(row, 18 + offset) or None
            data["lat"] = self._parse_float(self._get_value(row, 19 + offset), 0.0)
            data["lng"] = self._parse_float(self._get_value(row, 20 + offset), 0.0)

        return callsign, data

    def handle(self, *args, **options):
        self.stdout.write("Start importu danych z UKE")
        today = timezone.localdate()
        run_token = timezone.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = self._reports_dir()
        db_report_path = reports_dir / f"updatedb_{run_token}.json"

        created_callsigns = 0
        touched_callsigns = 0
        created_licenses = 0
        updated_licenses = 0
        skipped_rows = 0
        unchanged_licenses = 0

        created_callsign_values = []
        touched_callsign_values = []
        created_license_values = []
        updated_license_values = []

        dataset_summary = {}

        with transaction.atomic():
            for dataset_type, dataset_url in self.API_URL.items():
                rows = self._download_csv_rows(dataset_type, dataset_url)

                if not rows:
                    dataset_summary[dataset_type] = {
                        "rows": 0,
                        "processed": 0,
                        "skipped": 0,
                        "created_callsigns": 0,
                        "touched_callsigns": 0,
                        "created_licenses": 0,
                        "updated_licenses": 0,
                        "unchanged_licenses": 0,
                    }
                    continue

                dataset_rows = max(0, len(rows) - 1)
                dataset_processed = 0
                dataset_skipped = 0
                dataset_created_callsigns = 0
                dataset_touched_callsigns = 0
                dataset_created_licenses = 0
                dataset_updated_licenses = 0
                dataset_unchanged_licenses = 0

                for row in rows[1:]:
                    parsed = self._build_license_data(dataset_type, row, today)
                    if parsed is None:
                        skipped_rows += 1
                        dataset_skipped += 1
                        continue

                    dataset_processed += 1

                    callsign_value, license_data = parsed

                    callsign_obj, created = Callsign.objects.get_or_create(
                        callsign=callsign_value,
                        defaults={
                            "first_seen": today,
                            "last_seen": today,
                        },
                    )

                    if created:
                        created_callsigns += 1
                        dataset_created_callsigns += 1
                        created_callsign_values.append(callsign_value)
                    else:
                        if callsign_obj.last_seen != today:
                            callsign_obj.last_seen = today
                            callsign_obj.save(update_fields=["last_seen"])
                            touched_callsigns += 1
                            dataset_touched_callsigns += 1
                            touched_callsign_values.append(callsign_value)

                    license_number = license_data.pop("license")
                    license_data["assigned_callsign"] = callsign_obj

                    license_obj, created = License.objects.get_or_create(
                        license=license_number,
                        defaults={
                            **license_data,
                            "first_seen": today,
                        },
                    )

                    if created:
                        created_licenses += 1
                        dataset_created_licenses += 1
                        created_license_values.append(license_number)
                    else:
                        update_fields = []
                        for field, value in license_data.items():
                            if getattr(license_obj, field) != value:
                                setattr(license_obj, field, value)
                                update_fields.append(field)

                        if update_fields:
                            license_obj.save(update_fields=update_fields)
                            updated_licenses += 1
                            dataset_updated_licenses += 1
                            updated_license_values.append(license_number)
                        else:
                            unchanged_licenses += 1
                            dataset_unchanged_licenses += 1

                dataset_summary[dataset_type] = {
                    "rows": dataset_rows,
                    "processed": dataset_processed,
                    "skipped": dataset_skipped,
                    "created_callsigns": dataset_created_callsigns,
                    "touched_callsigns": dataset_touched_callsigns,
                    "created_licenses": dataset_created_licenses,
                    "updated_licenses": dataset_updated_licenses,
                    "unchanged_licenses": dataset_unchanged_licenses,
                }

            missing_callsigns_today = sorted(
                Callsign.objects.filter(last_seen__lt=today).values_list("callsign", flat=True)
            )
            missing_licenses_today = sorted(
                License.objects.filter(last_seen__lt=today).values_list("license", flat=True)
            )

            soon_expire_report_info = self._build_soon_expire_report(today, run_token)

            db_report_payload = {
                "generated_at": timezone.now().isoformat(),
                "today": today.isoformat(),
                "summary": {
                    "created_callsigns": created_callsigns,
                    "touched_callsigns": touched_callsigns,
                    "created_licenses": created_licenses,
                    "updated_licenses": updated_licenses,
                    "unchanged_licenses": unchanged_licenses,
                    "skipped_rows": skipped_rows,
                    "missing_callsigns_today": len(missing_callsigns_today),
                    "missing_licenses_today": len(missing_licenses_today),
                },
                "datasets": dataset_summary,
                "created_callsigns": sorted(created_callsign_values),
                "touched_callsigns": sorted(set(touched_callsign_values)),
                "created_licenses": sorted(created_license_values),
                "updated_licenses": sorted(set(updated_license_values)),
                "missing_callsigns_today": missing_callsigns_today,
                "missing_licenses_today": missing_licenses_today,
            }

            self._save_json(db_report_path, db_report_payload)

        self.stdout.write(
            self.style.SUCCESS("Import zakończony pomyślnie")
        )
        self.stdout.write(
            (
                f"Podsumowanie: created_callsigns={created_callsigns}, "
                f"touched_callsigns={touched_callsigns}, "
                f"created_licenses={created_licenses}, "
                f"updated_licenses={updated_licenses}, "
                f"unchanged_licenses={unchanged_licenses}, "
                f"skipped_rows={skipped_rows}"
            )
        )
        self.stdout.write(
            (
                f"Brakujące dziś: callsigns={len(missing_callsigns_today)}, "
                f"licenses={len(missing_licenses_today)}"
            )
        )
        self.stdout.write(
            (
                f"Raport importu: {db_report_path}"
            )
        )
        self.stdout.write(
            (
                f"Raport 30 dni: {soon_expire_report_info['report_path']} "
                f"(current={soon_expire_report_info['counts']['current']}, "
                f"renewed={soon_expire_report_info['counts']['renewed']}, "
                f"added={soon_expire_report_info['counts']['added']}, "
                f"removed={soon_expire_report_info['counts']['removed']})"
            )
        )
        self.stdout.write(
            (
                f"Snapshot 30 dni: {soon_expire_report_info['snapshot_path']}"
            )
        )
