import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/models/patient_file_model.dart';
import 'package:medscribe_ai/services/api_client.dart';

class PatientFilesState {
  final List<PatientFileModel> files;
  final bool isLoading;
  final bool isUploading;
  final double uploadProgress;
  final String? error;
  final String? activeCategory;
  final int total;

  const PatientFilesState({
    this.files = const [],
    this.isLoading = false,
    this.isUploading = false,
    this.uploadProgress = 0,
    this.error,
    this.activeCategory,
    this.total = 0,
  });

  PatientFilesState copyWith({
    List<PatientFileModel>? files,
    bool? isLoading,
    bool? isUploading,
    double? uploadProgress,
    String? error,
    String? activeCategory,
    int? total,
    bool clearCategory = false,
    bool clearError = false,
  }) {
    return PatientFilesState(
      files: files ?? this.files,
      isLoading: isLoading ?? this.isLoading,
      isUploading: isUploading ?? this.isUploading,
      uploadProgress: uploadProgress ?? this.uploadProgress,
      error: clearError ? null : (error ?? this.error),
      activeCategory: clearCategory ? null : (activeCategory ?? this.activeCategory),
      total: total ?? this.total,
    );
  }
}

class PatientFilesNotifier extends StateNotifier<PatientFilesState> {
  final _api = api;

  PatientFilesNotifier() : super(const PatientFilesState());

  Future<void> loadFiles(String patientId, {String? category}) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final params = <String, dynamic>{};
      final cat = category ?? state.activeCategory;
      if (cat != null) params['category'] = cat;

      final response = await _api.get(
        '/patients/$patientId/files/',
        queryParameters: params,
      );
      final data = response.data;
      final files = (data['files'] as List)
          .map((f) => PatientFileModel.fromJson(f))
          .toList();
      state = state.copyWith(
        files: files,
        total: data['total'] ?? files.length,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> uploadFile({
    required String patientId,
    required Uint8List bytes,
    required String fileName,
    required String category,
    String? description,
    String? visitId,
  }) async {
    state = state.copyWith(isUploading: true, uploadProgress: 0, clearError: true);
    try {
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: fileName),
        'category': category,
        if (description != null && description.isNotEmpty) 'description': description,
        if (visitId != null && visitId.isNotEmpty) 'visit_id': visitId,
      });

      await _api.post(
        '/patients/$patientId/files/upload',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
        onSendProgress: (sent, total) {
          if (total > 0) {
            state = state.copyWith(uploadProgress: sent / total);
          }
        },
      );

      state = state.copyWith(isUploading: false, uploadProgress: 1.0);
      await loadFiles(patientId);
      return true;
    } catch (e) {
      state = state.copyWith(isUploading: false, error: e.toString());
      return false;
    }
  }

  Future<bool> uploadMultiple({
    required String patientId,
    required List<MapEntry<String, Uint8List>> filesData,
    required String category,
  }) async {
    state = state.copyWith(isUploading: true, uploadProgress: 0, clearError: true);
    try {
      final multipartFiles = filesData.map((entry) {
        return MultipartFile.fromBytes(entry.value, filename: entry.key);
      }).toList();

      final formData = FormData.fromMap({
        'files': multipartFiles,
        'category': category,
      });

      await _api.post(
        '/patients/$patientId/files/upload-multiple',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
        onSendProgress: (sent, total) {
          if (total > 0) {
            state = state.copyWith(uploadProgress: sent / total);
          }
        },
      );

      state = state.copyWith(isUploading: false, uploadProgress: 1.0);
      await loadFiles(patientId);
      return true;
    } catch (e) {
      state = state.copyWith(isUploading: false, error: e.toString());
      return false;
    }
  }

  Future<bool> deleteFile(String patientId, int fileId) async {
    try {
      await _api.delete('/patients/$patientId/files/$fileId');
      await loadFiles(patientId);
      return true;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }

  Future<bool> updateFile(String patientId, int fileId, {String? category, String? description}) async {
    try {
      await _api.put('/patients/$patientId/files/$fileId', data: {
        if (category != null) 'category': category,
        if (description != null) 'description': description,
      });
      await loadFiles(patientId);
      return true;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }

  Future<String?> getDownloadUrl(String patientId, int fileId) async {
    try {
      final response = await _api.get('/patients/$patientId/files/$fileId/download');
      return response.data['download_url'];
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> getPreviewInfo(String patientId, int fileId) async {
    try {
      final response = await _api.get('/patients/$patientId/files/$fileId/preview');
      return response.data;
    } catch (e) {
      return null;
    }
  }

  void filterByCategory(String? category) {
    if (category == null) {
      state = state.copyWith(clearCategory: true);
    } else {
      state = state.copyWith(activeCategory: category);
    }
  }
}

final patientFilesProvider =
    StateNotifierProvider<PatientFilesNotifier, PatientFilesState>((ref) {
  return PatientFilesNotifier();
});
