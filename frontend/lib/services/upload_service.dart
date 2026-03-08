import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:medscribe_ai/services/api_client.dart';

class UploadService {
  final _api = api;
  static const _maxRetries = 3;

  Future<String> uploadRecording({
    required String visitId,
    required Uint8List audioData,
    required String mimeType,
    void Function(double progress)? onProgress,
  }) async {
    final formData = FormData.fromMap({
      'visit_id': visitId,
      'file': MultipartFile.fromBytes(
        audioData,
        filename: 'recording.webm',
        contentType: DioMediaType.parse(mimeType),
      ),
    });

    final response = await _api.post(
      '/recordings/upload',
      data: formData,
      queryParameters: {'visit_id': visitId},
      onSendProgress: (sent, total) {
        if (total > 0 && onProgress != null) {
          onProgress(sent / total);
        }
      },
    );

    return response.data['id'];
  }

  Future<int> uploadChunk({
    required String visitId,
    required Uint8List audioData,
    required String mimeType,
    required int chunkIndex,
    required bool isFinal,
    void Function(double progress)? onProgress,
  }) async {
    for (int attempt = 0; attempt < _maxRetries; attempt++) {
      try {
        final formData = FormData.fromMap({
          'visit_id': visitId,
          'chunk_index': chunkIndex,
          'is_final': isFinal,
          'file': MultipartFile.fromBytes(
            audioData,
            filename: 'chunk_${chunkIndex.toString().padLeft(4, '0')}.webm',
            contentType: DioMediaType.parse(mimeType),
          ),
        });
        final response = await _api.post(
          '/recordings/upload-chunk',
          data: formData,
          onSendProgress: (sent, total) {
            if (total > 0 && onProgress != null) {
              onProgress(sent / total);
            }
          },
        );
        return response.data['chunk_id'] as int;
      } catch (e) {
        if (attempt == _maxRetries - 1) rethrow;
        await Future.delayed(Duration(seconds: (attempt + 1) * 2));
      }
    }
    throw Exception('Upload failed after $_maxRetries retries');
  }

  Future<void> finalizeRecording({required String visitId}) async {
    await _api.post('/recordings/finalize/$visitId');
  }
}
