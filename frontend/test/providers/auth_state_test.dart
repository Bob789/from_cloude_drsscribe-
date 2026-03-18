import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/models/user_model.dart';

void main() {
  group('AuthState', () {
    test('default state is loading', () {
      const state = AuthState();
      expect(state.status, AuthStatus.loading);
      expect(state.user, isNull);
      expect(state.error, isNull);
    });

    test('copyWith updates status', () {
      const state = AuthState();
      final updated = state.copyWith(status: AuthStatus.authenticated);
      expect(updated.status, AuthStatus.authenticated);
      expect(updated.user, isNull);
    });

    test('copyWith sets user', () {
      const state = AuthState();
      final user = UserModel(
        id: 'u-1', email: 'a@b.com', name: 'Test',
        role: 'admin', isActive: true, createdAt: DateTime.now(),
      );

      final updated = state.copyWith(status: AuthStatus.authenticated, user: user);

      expect(updated.status, AuthStatus.authenticated);
      expect(updated.user?.name, 'Test');
      expect(updated.user?.role, 'admin');
    });

    test('copyWith sets error', () {
      const state = AuthState();
      final updated = state.copyWith(status: AuthStatus.error, error: 'invalid credentials');

      expect(updated.status, AuthStatus.error);
      expect(updated.error, 'invalid credentials');
    });
  });
}
