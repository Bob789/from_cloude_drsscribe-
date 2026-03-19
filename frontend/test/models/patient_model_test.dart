import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/models/patient_model.dart';

void main() {
  group('PatientModel.fromJson', () {
    test('parses complete JSON correctly', () {
      final json = {
        'id': 'abc-123',
        'display_id': 5,
        'name': 'דני כהן',
        'id_number': '123456789',
        'dob': '1985-03-15',
        'phone': '050-1234567',
        'email': 'dani@test.com',
        'blood_type': 'A+',
        'allergies': ['פניצילין', 'אספירין'],
        'insurance_info': 'מכבי',
        'notes': 'מטופל קבוע',
        'created_at': '2026-03-18T10:00:00Z',
      };

      final patient = PatientModel.fromJson(json);

      expect(patient.id, 'abc-123');
      expect(patient.displayId, 5);
      expect(patient.name, 'דני כהן');
      expect(patient.idNumber, '123456789');
      expect(patient.dob, '1985-03-15');
      expect(patient.phone, '050-1234567');
      expect(patient.email, 'dani@test.com');
      expect(patient.bloodType, 'A+');
      expect(patient.allergies, ['פניצילין', 'אספירין']);
      expect(patient.insuranceInfo, 'מכבי');
      expect(patient.notes, 'מטופל קבוע');
      expect(patient.createdAt.year, 2026);
    });

    test('handles null optional fields', () {
      final json = {
        'id': 'abc-123',
        'display_id': 1,
        'name': 'שרה לוי',
        'created_at': '2026-01-01T00:00:00Z',
      };

      final patient = PatientModel.fromJson(json);

      expect(patient.name, 'שרה לוי');
      expect(patient.phone, isNull);
      expect(patient.email, isNull);
      expect(patient.allergies, isNull);
      expect(patient.bloodType, isNull);
    });

    test('handles missing display_id with default 0', () {
      final json = {
        'id': 'abc-123',
        'name': 'Test',
        'created_at': '2026-01-01T00:00:00Z',
      };

      final patient = PatientModel.fromJson(json);
      expect(patient.displayId, 0);
    });

    test('toJson excludes id and created_at', () {
      final patient = PatientModel(
        id: 'abc', displayId: 1, name: 'Test', createdAt: DateTime.now(),
        phone: '050-111', email: 'a@b.com',
      );

      final json = patient.toJson();
      expect(json.containsKey('id'), isFalse);
      expect(json.containsKey('created_at'), isFalse);
      expect(json['name'], 'Test');
      expect(json['phone'], '050-111');
    });
  });
}
