import datetime

from django.db import IntegrityError
from django.test import TestCase

from app.management.commands.updatedb import Command
from app.models import Callsign, License
from app.templatetags.license_helper import license_category, license_type


class ModelConstraintsTests(TestCase):
	def test_callsign_must_be_unique(self):
		Callsign.objects.create(
			callsign="SP1ABC",
			first_seen=datetime.date(2026, 1, 1),
			last_seen=datetime.date(2026, 1, 1),
		)

		with self.assertRaises(IntegrityError):
			Callsign.objects.create(
				callsign="SP1ABC",
				first_seen=datetime.date(2026, 1, 2),
				last_seen=datetime.date(2026, 1, 2),
			)

	def test_license_must_be_unique(self):
		callsign = Callsign.objects.create(
			callsign="SP2ABC",
			first_seen=datetime.date(2026, 1, 1),
			last_seen=datetime.date(2026, 1, 1),
		)

		License.objects.create(
			license="ABC/1/2026",
			category=License.Category.KATEGORIA_1,
			assigned_callsign=callsign,
			expiration_date=datetime.date(2026, 12, 31),
			first_seen=datetime.date(2026, 1, 1),
			last_seen=datetime.date(2026, 1, 1),
		)

		with self.assertRaises(IntegrityError):
			License.objects.create(
				license="ABC/1/2026",
				category=License.Category.KATEGORIA_1,
				assigned_callsign=callsign,
				expiration_date=datetime.date(2026, 12, 31),
				first_seen=datetime.date(2026, 1, 2),
				last_seen=datetime.date(2026, 1, 2),
			)


class TemplateFilterTests(TestCase):
	def test_license_category_filter_for_invalid_value(self):
		self.assertEqual(license_category("invalid"), License.CATEGORY_MAP[License.Category.INVALID])

	def test_license_type_filter_for_invalid_value(self):
		self.assertEqual(license_type("invalid"), License.TYPE_MAP[License.Type.INVALID])


class UpdateDbParserTests(TestCase):
	def test_build_license_data_returns_none_for_invalid_date(self):
		command = Command()
		row = [
			"ABC/2/2026",
			"not-a-date",
			"sp3abc",
			"Kategoria1",
			"100",
			"Warszawa",
		]

		parsed = command._build_license_data("INDIVIDUALS", row, datetime.date(2026, 3, 1))
		self.assertIsNone(parsed)

	def test_build_license_data_for_individual_sets_defaults(self):
		command = Command()
		today = datetime.date(2026, 3, 1)
		row = [
			"ABC/3/2026",
			"2026-12-31",
			"sp4abc",
			"Kategoria1",
			"",
			"Warszawa",
		]

		parsed = command._build_license_data("INDIVIDUALS", row, today)
		self.assertIsNotNone(parsed)
		callsign, data = parsed

		self.assertEqual(callsign, "SP4ABC")
		self.assertEqual(data["power"], -1)
		self.assertEqual(data["type"], License.Type.INDIVIDUAL)
		self.assertEqual(data["station_location"], "Warszawa")
