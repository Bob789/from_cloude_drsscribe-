import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'api_client.dart';

class AuthService {
  // הגדרת ה-Google Sign-In עם התאמות ל-Web
  final _googleSignIn = GoogleSignIn(
    // שימוש ב-clientId מהסביבה או ערך ברירת מחדל
    clientId: const String.fromEnvironment(
      'GOOGLE_CLIENT_ID',
      defaultValue: '459295230393-a7tahndgdhses9shhg0oue74ealf009r.apps.googleusercontent.com',
    ),
    // ה-Scopes המומלצים לאפליקציה רפואית: מינימום הרשאות הכרחי
    scopes: [
      'email',
      'https://www.googleapis.com/auth/userinfo.profile',
      'openid',
    ],
  );

  final _dio = ApiClient().dio;

  /// מבצע התחברות מול גוגל ושולח את ה-Token לשרת ה-Backend
  Future<Map<String, dynamic>?> signInWithGoogle() async {
    try {
      // פתיחת חלונית ההתחברות של גוגל
      final account = await _googleSignIn.signIn();
      
      if (account == null) {
        print('Google Sign-In: user cancelled or no account returned');
        return null;
      }

      final auth = await account.authentication;
      final token = auth.accessToken;

      if (token == null) {
        print('Google Sign-In: no accessToken received');
        return null;
      }

      final response = await _dio.post('/auth/google', data: {'token': token, 'token_type': 'access_token'});

      // שמירת ה-Tokens שחזרו מהשרת ב-Local Storage של הדפדפן
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', response.data['access_token']);
      await prefs.setString('refresh_token', response.data['refresh_token']);

      return response.data['user'];
    } catch (e) {
      print('Google Sign-In error: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>?> signInLocal(String username, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'username': username,
        'password': password,
      });

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', response.data['access_token']);
      await prefs.setString('refresh_token', response.data['refresh_token']);

      return response.data['user'];
    } catch (e) {
      print('Local login error: $e');
      rethrow;
    }
  }

  /// שליפת פרטי המשתמש הנוכחי מהשרת
  Future<Map<String, dynamic>?> getCurrentUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      if (prefs.getString('access_token') == null) return null;
      final response = await _dio.get('/auth/me');
      return response.data;
    } catch (_) {
      return null;
    }
  }

  /// התנתקות מהמערכת וניקוי ה-Tokens
  Future<void> signOut() async {
    try {
      await _googleSignIn.signOut();
    } catch (e) {
      print('Google Sign-Out error: $e');
    }
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }

  /// בדיקה האם קיים Access Token שמור
  Future<bool> isAuthenticated() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token') != null;
  }
}