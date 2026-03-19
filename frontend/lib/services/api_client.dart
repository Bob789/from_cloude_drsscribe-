import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

Dio get api => ApiClient._instance.dio;

class AppException implements Exception {
  final String errorId;
  final String message;
  final String? code;
  final int? statusCode;

  AppException({required this.errorId, required this.message, this.code, this.statusCode});

  @override
  String toString() => '[$errorId] $message';
}

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  late final Dio dio;

  ApiClient._internal() {
    dio = Dio(BaseOptions(
      baseUrl: '/api',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401 && error.requestOptions.path != '/auth/refresh') {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final options = error.requestOptions;
            final prefs = await SharedPreferences.getInstance();
            final newToken = prefs.getString('access_token');
            options.headers['Authorization'] = 'Bearer $newToken';
            final retryResponse = await dio.fetch(options);
            return handler.resolve(retryResponse);
          }
        }
        final data = error.response?.data;
        if (data is Map && data.containsKey('error_id')) {
          return handler.reject(DioException(
            requestOptions: error.requestOptions,
            response: error.response,
            type: error.type,
            error: AppException(
              errorId: data['error_id'],
              message: data['message'] ?? 'Unknown error',
              code: data['code'],
              statusCode: error.response?.statusCode,
            ),
          ));
        }
        if (error.type == DioExceptionType.connectionTimeout || error.type == DioExceptionType.sendTimeout) {
          return handler.reject(DioException(
            requestOptions: error.requestOptions,
            type: error.type,
            error: AppException(errorId: 'TIMEOUT', message: 'System not responding, please try again'),
          ));
        }
        if (error.type == DioExceptionType.connectionError) {
          return handler.reject(DioException(
            requestOptions: error.requestOptions,
            type: error.type,
            error: AppException(errorId: 'NETWORK', message: 'No internet connection'),
          ));
        }
        return handler.next(error);
      },
    ));
  }

  Future<bool> _refreshToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString('refresh_token');
      if (refreshToken == null) return false;
      final refreshDio = Dio(BaseOptions(baseUrl: dio.options.baseUrl));
      final response = await refreshDio.post('/auth/refresh', data: {'refresh_token': refreshToken});
      if (response.statusCode == 200) {
        await prefs.setString('access_token', response.data['access_token']);
        if (response.data['refresh_token'] != null) {
          await prefs.setString('refresh_token', response.data['refresh_token']);
        }
        return true;
      }
      return false;
    } catch (e) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('access_token');
      await prefs.remove('refresh_token');
      return false;
    }
  }
}
