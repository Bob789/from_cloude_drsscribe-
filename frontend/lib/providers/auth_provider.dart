import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/models/user_model.dart';
import 'package:medscribe_ai/services/auth_service.dart';

enum AuthStatus { loading, authenticated, unauthenticated, error }

class AuthState {
  final AuthStatus status;
  final UserModel? user;
  final String? error;

  const AuthState({this.status = AuthStatus.loading, this.user, this.error});

  AuthState copyWith({AuthStatus? status, UserModel? user, String? error}) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      error: error ?? this.error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;

  AuthNotifier(this._authService) : super(const AuthState()) {
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    try {
      final userData = await _authService.getCurrentUser();
      if (userData != null) {
        state = AuthState(status: AuthStatus.authenticated, user: UserModel.fromJson(userData));
      } else {
        state = const AuthState(status: AuthStatus.unauthenticated);
      }
    } catch (_) {
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> signInWithGoogle() async {
    state = const AuthState(status: AuthStatus.loading);
    try {
      final userData = await _authService.signInWithGoogle();
      if (userData != null) {
        state = AuthState(status: AuthStatus.authenticated, user: UserModel.fromJson(userData));
      } else {
        state = const AuthState(
          status: AuthStatus.unauthenticated,
          error: 'login.cancelled',
        );
      }
    } catch (e) {
      state = AuthState(status: AuthStatus.error, error: 'login.error');
    }
  }

  Future<void> signInLocal(String username, String password) async {
    state = const AuthState(status: AuthStatus.loading);
    try {
      final userData = await _authService.signInLocal(username, password);
      if (userData != null) {
        state = AuthState(status: AuthStatus.authenticated, user: UserModel.fromJson(userData));
      } else {
        state = const AuthState(status: AuthStatus.unauthenticated, error: 'login.login_error');
      }
    } catch (e) {
      state = const AuthState(status: AuthStatus.error, error: 'login.wrong_credentials');
    }
  }

  Future<void> signOut() async {
    await _authService.signOut();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}

final authServiceProvider = Provider((ref) => AuthService());

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(authServiceProvider));
});

final currentUserProvider = Provider<UserModel?>((ref) {
  return ref.watch(authProvider).user;
});
