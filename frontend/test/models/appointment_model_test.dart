import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/models/appointment_model.dart';

void main() {
  group('AppointmentModel.fromJson', () {
    test('parses complete JSON correctly', () {
      final json = {
        'id': 42,
        'patient_id': 'p-123',
        'patient_name': 'ישראל ישראלי',
        'title': 'ביקור ראשוני',
        'description': 'בדיקה כללית',
        'start_time': '2026-03-18T15:00:00Z',
        'end_time': '2026-03-18T15:30:00Z',
        'duration_minutes': 30,
        'status': 'scheduled',
        'reminder_minutes': 60,
        'synced_to_google': true,
        'google_event_id': 'g-evt-1',
        'created_at': '2026-03-18T10:00:00Z',
      };

      final appt = AppointmentModel.fromJson(json);

      expect(appt.id, 42);
      expect(appt.patientName, 'ישראל ישראלי');
      expect(appt.title, 'ביקור ראשוני');
      expect(appt.durationMinutes, 30);
      expect(appt.status, 'scheduled');
      expect(appt.syncedToGoogle, true);
      expect(appt.startTime.hour, 15);
    });

    test('handles missing optional fields with defaults', () {
      final json = {
        'id': 1,
        'title': 'Test',
        'start_time': '2026-03-18T10:00:00Z',
        'end_time': '2026-03-18T10:20:00Z',
        'created_at': '2026-03-18T10:00:00Z',
      };

      final appt = AppointmentModel.fromJson(json);

      expect(appt.patientId, isNull);
      expect(appt.patientName, isNull);
      expect(appt.description, isNull);
      expect(appt.durationMinutes, 20);
      expect(appt.status, 'scheduled');
      expect(appt.reminderMinutes, 60);
      expect(appt.syncedToGoogle, false);
    });

    test('handles null id as 0', () {
      final json = {
        'title': 'No ID',
        'start_time': '2026-01-01T00:00:00Z',
        'end_time': '2026-01-01T00:20:00Z',
        'created_at': '2026-01-01T00:00:00Z',
      };

      final appt = AppointmentModel.fromJson(json);
      expect(appt.id, 0);
    });
  });

  group('HolidayModel.fromJson', () {
    test('parses correctly', () {
      final json = {'date': '2026-09-25', 'name': 'ראש השנה'};
      final holiday = HolidayModel.fromJson(json);
      expect(holiday.date, '2026-09-25');
      expect(holiday.name, 'ראש השנה');
    });
  });
}
