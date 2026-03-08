async def diarize_speakers(segments: list, transcription_text: str) -> list:
    if not segments:
        return segments

    doctor_keywords = [
        "אני רואה", "בדיקה", "מרשם", "טיפול", "תרופה", "אבחנה",
        "אני ממליץ", "לקבוע תור", "בוא נבדוק", "מה מביא אותך",
    ]
    patient_keywords = [
        "כואב לי", "אני מרגיש", "יש לי", "מאז", "התחיל",
        "לא ישנתי", "קשה לי", "אני לוקח", "מפריע",
    ]

    for segment in segments:
        text = segment.get("text", "").lower()
        doctor_score = sum(1 for kw in doctor_keywords if kw in text)
        patient_score = sum(1 for kw in patient_keywords if kw in text)

        if doctor_score > patient_score:
            segment["speaker"] = "doctor"
        elif patient_score > doctor_score:
            segment["speaker"] = "patient"
        else:
            segment["speaker"] = "unknown"

    return segments
