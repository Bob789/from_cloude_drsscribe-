import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:medscribe_ai/services/upload_service.dart';

class PendingRecording {
  final String visitId;
  final Uint8List audioData;
  final String mimeType;
  final DateTime createdAt;

  PendingRecording({required this.visitId, required this.audioData, required this.mimeType})
      : createdAt = DateTime.now();
}

class OfflineService {
  static final OfflineService _instance = OfflineService._internal();
  factory OfflineService() => _instance;
  OfflineService._internal();

  final List<PendingRecording> _pendingQueue = [];
  final _uploadService = UploadService();
  bool _isSyncing = false;

  int get pendingCount => _pendingQueue.length;

  void addPendingRecording(String visitId, Uint8List audioData, String mimeType) {
    _pendingQueue.add(PendingRecording(visitId: visitId, audioData: audioData, mimeType: mimeType));
  }

  Future<void> syncPending() async {
    if (_isSyncing || _pendingQueue.isEmpty) return;
    _isSyncing = true;
    try {
      final pending = List<PendingRecording>.from(_pendingQueue);
      for (final recording in pending) {
        try {
          await _uploadService.uploadRecording(
            visitId: recording.visitId,
            audioData: recording.audioData,
            mimeType: recording.mimeType,
          );
          _pendingQueue.remove(recording);
        } catch (_) {
          break;
        }
      }
    } finally {
      _isSyncing = false;
    }
  }
}
