import 'dart:async';
import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/services/upload_service.dart';

class RecordingState {
  final String? selectedPatientId;
  final String? patientName;
  final int? patientDisplayId;
  final String? visitId;
  final double? uploadProgress;
  final bool isComplete;
  final String? error;
  final List<PatientModel> searchResults;
  final bool isSearching;
  final int chunksUploaded;
  final bool isUploading;
  final String? transcriptionStatus; // processing, done, error
  final String? summaryStatus;       // processing, done, error

  const RecordingState({
    this.selectedPatientId,
    this.patientName,
    this.patientDisplayId,
    this.visitId,
    this.uploadProgress,
    this.isComplete = false,
    this.error,
    this.searchResults = const [],
    this.isSearching = false,
    this.chunksUploaded = 0,
    this.isUploading = false,
    this.transcriptionStatus,
    this.summaryStatus,
  });

  RecordingState copyWith({
    String? selectedPatientId,
    String? patientName,
    int? patientDisplayId,
    String? visitId,
    double? uploadProgress,
    bool? isComplete,
    String? error,
    List<PatientModel>? searchResults,
    bool? isSearching,
    int? chunksUploaded,
    bool? isUploading,
    String? transcriptionStatus,
    String? summaryStatus,
  }) {
    return RecordingState(
      selectedPatientId: selectedPatientId ?? this.selectedPatientId,
      patientName: patientName ?? this.patientName,
      patientDisplayId: patientDisplayId ?? this.patientDisplayId,
      visitId: visitId ?? this.visitId,
      uploadProgress: uploadProgress ?? this.uploadProgress,
      isComplete: isComplete ?? this.isComplete,
      error: error ?? this.error,
      searchResults: searchResults ?? this.searchResults,
      isSearching: isSearching ?? this.isSearching,
      chunksUploaded: chunksUploaded ?? this.chunksUploaded,
      isUploading: isUploading ?? this.isUploading,
      transcriptionStatus: transcriptionStatus ?? this.transcriptionStatus,
      summaryStatus: summaryStatus ?? this.summaryStatus,
    );
  }
}

class RecordingNotifier extends StateNotifier<RecordingState> {
  final _api = api;
  final _uploadService = UploadService();
  Timer? _debounce;
  Timer? _pollTimer;

  RecordingNotifier() : super(const RecordingState());

  @override
  void dispose() {
    _debounce?.cancel();
    _pollTimer?.cancel();
    super.dispose();
  }

  void _startPolling() {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(seconds: 5), (_) => _checkStatus());
  }

  Future<void> _checkStatus() async {
    if (state.visitId == null) return;
    if (state.summaryStatus == 'done') {
      _pollTimer?.cancel();
      return;
    }
    try {
      final resp = await _api.get('/visits/${state.visitId}/status');
      final data = resp.data;
      final tStatus = data['transcription_status'] as String?;
      final sStatus = data['summary_status'] as String?;
      state = state.copyWith(
        transcriptionStatus: tStatus,
        summaryStatus: sStatus,
      );
      if (sStatus == 'done' || sStatus == 'error') {
        _pollTimer?.cancel();
      }
    } catch (_) {}
  }

  Future<void> selectPatient(String patientId, String patientName, {int? displayId}) async {
    try {
      final response = await _api.post('/visits', data: {'patient_id': patientId});
      state = RecordingState(
        selectedPatientId: patientId,
        patientName: patientName,
        patientDisplayId: displayId,
        visitId: response.data['id'],
      );
    } catch (e) {
      state = RecordingState(error: e.toString());
    }
  }

  void searchPatient(String query) {
    _debounce?.cancel();
    if (query.trim().isEmpty) {
      state = const RecordingState();
      return;
    }
    state = state.copyWith(isSearching: true);
    _debounce = Timer(const Duration(milliseconds: 250), () {
      _doSearch(query.trim());
    });
  }

  Future<void> _doSearch(String query) async {
    try {
      final response = await _api.get('/patients/search', queryParameters: {'q': query});
      final patients = (response.data as List).map((e) => PatientModel.fromJson(e)).toList();
      state = RecordingState(searchResults: patients, isSearching: false);
    } catch (e) {
      state = RecordingState(searchResults: [], isSearching: false, error: e.toString());
    }
  }

  Future<void> onChunkReady(Uint8List data, String mimeType, int chunkIndex, bool isFinal) async {
    if (state.visitId == null) return;

    state = state.copyWith(isUploading: true);
    try {
      await _uploadService.uploadChunk(
        visitId: state.visitId!,
        audioData: data,
        mimeType: mimeType,
        chunkIndex: chunkIndex,
        isFinal: isFinal,
      );
      state = state.copyWith(
        chunksUploaded: state.chunksUploaded + 1,
        isUploading: false,
      );

      if (isFinal) {
        state = RecordingState(
          selectedPatientId: state.selectedPatientId,
          patientName: state.patientName,
          patientDisplayId: state.patientDisplayId,
          visitId: state.visitId,
          isComplete: true,
          chunksUploaded: state.chunksUploaded,
          transcriptionStatus: 'processing',
        );
        _startPolling();
      }
    } catch (e) {
      state = state.copyWith(
        isUploading: false,
        error: 'Upload error chunk $chunkIndex: $e',
      );
    }
  }

  Future<void> onRecordingComplete(Uint8List data, String mimeType) async {
    if (state.visitId == null) return;
    state = RecordingState(
      selectedPatientId: state.selectedPatientId,
      patientName: state.patientName,
      patientDisplayId: state.patientDisplayId,
      visitId: state.visitId,
      uploadProgress: 0.0,
    );
    try {
      await _uploadService.uploadRecording(
        visitId: state.visitId!,
        audioData: data,
        mimeType: mimeType,
        onProgress: (progress) {
          state = RecordingState(
            selectedPatientId: state.selectedPatientId,
            patientName: state.patientName,
            patientDisplayId: state.patientDisplayId,
            visitId: state.visitId,
            uploadProgress: progress,
          );
        },
      );
      state = RecordingState(
        selectedPatientId: state.selectedPatientId,
        patientName: state.patientName,
        patientDisplayId: state.patientDisplayId,
        visitId: state.visitId,
        isComplete: true,
        transcriptionStatus: 'processing',
      );
      _startPolling();
    } catch (e) {
      state = RecordingState(
        selectedPatientId: state.selectedPatientId,
        patientName: state.patientName,
        patientDisplayId: state.patientDisplayId,
        visitId: state.visitId,
        error: e.toString(),
      );
    }
  }

  void reset() {
    state = const RecordingState();
  }
}

final recordingProvider = StateNotifierProvider<RecordingNotifier, RecordingState>((ref) {
  return RecordingNotifier();
});
