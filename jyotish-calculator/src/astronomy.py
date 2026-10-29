from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe


# Default location: Harda, Madhya Pradesh, India
HARDA_LATITUDE = 22.34
HARDA_LONGITUDE = 77.10
TIMEZONE = ZoneInfo("Asia/Kolkata")


def local_noon_utc(day: date) -> datetime:
    """Return noon on the given local date, converted to UTC."""
    local_noon = datetime(
        day.year, day.month, day.day,
        12, 0, 0,
        tzinfo=TIMEZONE,
    )
    return local_noon.astimezone(timezone.utc)


def julian_day(dt_utc: datetime) -> float:
    """Convert a timezone-aware UTC datetime to a Julian Day."""
    if dt_utc.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")

    utc = dt_utc.astimezone(timezone.utc)

    hour = (
        utc.hour
        + utc.minute / 60
        + utc.second / 3600
        + utc.microsecond / 3_600_000_000
    )

    return swe.julday(
        utc.year, utc.month, utc.day, hour, swe.GREG_CAL
    )


def sunrise_sunset(day: date) -> dict[str, datetime]:
    """Calculate disc-center sunrise and sunset for Harda."""
    noon_utc = local_noon_utc(day)
    jd_noon = julian_day(noon_utc)

    # Swiss Ephemeris rise/set flags:
    # CALC_RISE / CALC_SET select the event.
    # BIT_DISC_CENTER uses the Sun's center, not its upper limb.
    # BIT_NO_REFRACTION is deliberately NOT set.
    flags = swe.FLG_SWIEPH | swe.BIT_DISC_CENTER

    geopos = (HARDA_LONGITUDE, HARDA_LATITUDE, 0.0)

    def find_event(event_flag: int) -> datetime:
        result, tret = swe.rise_trans(
            jd_noon,
            swe.SUN,
            event_flag,
            geopos,
            0.0,  # atmospheric pressure: Swiss Ephemeris default
            15.0,  # temperature in Celsius
            flags,
        )

        if result < 0:
            raise RuntimeError(
                f"Swiss Ephemeris could not calculate event for {day}"
            )

        event_jd = tret[0]
        year, month, day_num, hour = swe.revjul(
            event_jd, swe.GREG_CAL
        )

        whole_seconds = round(hour * 3600)
        event_utc = datetime(
            year, month, day_num, tzinfo=timezone.utc
        ) + timedelta(seconds=whole_seconds)

        return event_utc.astimezone(TIMEZONE)

    return {
        "sunrise": find_event(swe.CALC_RISE),
        "sunset": find_event(swe.CALC_SET),
    }