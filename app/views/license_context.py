from datetime import date

from app.models import License


def serialize_license(db_license: License) -> dict:
    return {
        "license": db_license.license,
        "license_slug": db_license.license.replace("/", "-"),
        "category": License.CATEGORY_MAP[db_license.category],
        "expiration_date": db_license.expiration_date,
        "power": db_license.power,
        "type": License.TYPE_MAP[db_license.type],
        "type_numeric": db_license.type,
        "first_seen": db_license.first_seen,
        "last_seen": db_license.last_seen,
        "station_location": db_license.station_location,
        "applicant_name": db_license.applicant_name,
        "applicant_city": db_license.applicant_city,
        "applicant_street": db_license.applicant_street,
        "applicant_house": db_license.applicant_house,
        "applicant_number": db_license.applicant_number,
        "enduser_name": db_license.enduser_name,
        "enduser_city": db_license.enduser_city,
        "enduser_street": db_license.enduser_street,
        "enduser_house": db_license.enduser_house,
        "enduser_number": db_license.enduser_number,
        "station_city": db_license.station_city,
        "station_street": db_license.station_street,
        "station_house": db_license.station_house,
        "station_number": db_license.station_number,
        "lat": db_license.lat,
        "lng": db_license.lng,
        "name_type_station": db_license.name_type_station,
        "emission": db_license.emission,
        "input_frequency": db_license.input_frequency,
        "output_frequency": db_license.output_frequency,
    }


def is_license_active(db_license: License) -> bool:
    return db_license.expiration_date >= date.today()