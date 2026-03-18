import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/models/user_model.dart';

void main() {
  group('UserModel.fromJson', () {
    test('parses complete JSON', () {
      final json = {
        'id': 'u-123',
        'email': 'yossi@test.com',
        'name': 'Yossi Levi',
        'role': 'admin',
        'avatar_url': 'https://example.com/avatar.jpg',
        'is_active': true,
        'patient_key_type': 'phone',
        'preferred_language': 'he',
        'created_at': '2026-01-01T00:00:00Z',
      };

      final user = UserModel.fromJson(json);

      expect(user.id, 'u-123');
      expect(user.email, 'yossi@test.com');
      expect(user.name, 'Yossi Levi');
      expect(user.role, 'admin');
      expect(user.avatarUrl, contains('avatar.jpg'));
      expect(user.isActive, true);
      expect(user.patientKeyType, 'phone');
      expect(user.preferredLanguage, 'he');
    });

    test('uses defaults for missing fields', () {
      final json = {
        'id': 'u-1',
        'email': 'a@b.com',
        'name': 'Test',
        'role': 'doctor',
        'created_at': '2026-01-01T00:00:00Z',
      };

      final user = UserModel.fromJson(json);

      expect(user.avatarUrl, isNull);
      expect(user.isActive, true);
      expect(user.patientKeyType, 'national_id');
      expect(user.preferredLanguage, 'he');
    });

    test('toJson roundtrip preserves data', () {
      final user = UserModel(
        id: 'u-1', email: 'a@b.com', name: 'Test', role: 'doctor',
        isActive: true, createdAt: DateTime(2026, 1, 1),
      );

      final json = user.toJson();
      final restored = UserModel.fromJson(json);

      expect(restored.id, user.id);
      expect(restored.email, user.email);
      expect(restored.name, user.name);
      expect(restored.role, user.role);
    });
  });
}
