from datetime import datetime

HOLIDAYS = {
    2025: [
        {"date": "2025-03-14", "name": "פורים"},
        {"date": "2025-04-13", "name": "ערב פסח"},
        {"date": "2025-04-14", "name": "פסח"},
        {"date": "2025-04-15", "name": "פסח"},
        {"date": "2025-04-19", "name": "שביעי של פסח"},
        {"date": "2025-04-20", "name": "אחרון של פסח"},
        {"date": "2025-04-24", "name": "יום השואה"},
        {"date": "2025-05-01", "name": "יום הזיכרון"},
        {"date": "2025-05-02", "name": "יום העצמאות"},
        {"date": "2025-06-02", "name": "שבועות"},
        {"date": "2025-06-03", "name": "שבועות"},
        {"date": "2025-09-23", "name": "ראש השנה"},
        {"date": "2025-09-24", "name": "ראש השנה"},
        {"date": "2025-09-25", "name": "צום גדליה"},
        {"date": "2025-10-02", "name": "יום כיפור"},
        {"date": "2025-10-07", "name": "סוכות"},
        {"date": "2025-10-14", "name": "שמחת תורה"},
        {"date": "2025-12-15", "name": "חנוכה (יום 1)"},
    ],
    2026: [
        {"date": "2026-03-01", "name": "תענית אסתר"},
        {"date": "2026-03-03", "name": "פורים"},
        {"date": "2026-04-02", "name": "ערב פסח"},
        {"date": "2026-04-03", "name": "פסח"},
        {"date": "2026-04-04", "name": "פסח"},
        {"date": "2026-04-08", "name": "שביעי של פסח"},
        {"date": "2026-04-09", "name": "אחרון של פסח"},
        {"date": "2026-04-15", "name": "יום השואה"},
        {"date": "2026-04-22", "name": "יום הזיכרון"},
        {"date": "2026-04-23", "name": "יום העצמאות"},
        {"date": "2026-05-22", "name": "שבועות"},
        {"date": "2026-05-23", "name": "שבועות"},
        {"date": "2026-09-12", "name": "ראש השנה"},
        {"date": "2026-09-13", "name": "ראש השנה"},
        {"date": "2026-09-14", "name": "צום גדליה"},
        {"date": "2026-09-21", "name": "יום כיפור"},
        {"date": "2026-09-26", "name": "סוכות"},
        {"date": "2026-10-03", "name": "שמחת תורה"},
        {"date": "2026-12-14", "name": "חנוכה (יום 1)"},
    ],
    2027: [
        {"date": "2027-03-23", "name": "פורים"},
        {"date": "2027-04-22", "name": "ערב פסח"},
        {"date": "2027-04-23", "name": "פסח"},
        {"date": "2027-04-24", "name": "פסח"},
        {"date": "2027-04-28", "name": "שביעי של פסח"},
        {"date": "2027-04-29", "name": "אחרון של פסח"},
        {"date": "2027-05-05", "name": "יום השואה"},
        {"date": "2027-05-12", "name": "יום הזיכרון"},
        {"date": "2027-05-13", "name": "יום העצמאות"},
        {"date": "2027-06-12", "name": "שבועות"},
        {"date": "2027-06-13", "name": "שבועות"},
        {"date": "2027-10-02", "name": "ראש השנה"},
        {"date": "2027-10-03", "name": "ראש השנה"},
        {"date": "2027-10-11", "name": "יום כיפור"},
        {"date": "2027-10-16", "name": "סוכות"},
        {"date": "2027-10-23", "name": "שמחת תורה"},
    ],
}


def get_holidays(year: int) -> list:
    return HOLIDAYS.get(year, [])


def get_holidays_range(date_from: str, date_to: str) -> list:
    start = datetime.fromisoformat(date_from)
    end = datetime.fromisoformat(date_to)
    result = []
    for year in range(start.year, end.year + 1):
        for h in get_holidays(year):
            h_date = datetime.fromisoformat(h['date'])
            if start <= h_date <= end:
                result.append(h)
    return result


def is_holiday(date_str: str) -> str | None:
    d = datetime.fromisoformat(date_str)
    for h in get_holidays(d.year):
        if h['date'] == date_str:
            return h['name']
    return None
