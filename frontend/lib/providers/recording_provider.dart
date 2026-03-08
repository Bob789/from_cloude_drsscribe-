import 'dart:async';
import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/services/upload_service.dart';

class RecordingState {
  final String? selectedPatientId;
  final String? patientName;
  final String? visitId;
  final double? uploadProgress;
  final bool isComplete;
  final String? error;
  final List<PatientModel> searchResults;
  final bool isSearching;
  final int chunksUploaded;
  final bool isUploading;

  const RecordingState({
    this.selectedPatientId,
    this.patientName,
    this.visitId,
    this.uploadProgress,
    this.isComplete = false,
    this.error,
    this.searchResults = const [],
    this.isSearching = false,
    this.chunksUploaded = 0,
    this.isUploading = false,
  });

  RecordingState copyWith({
    String? selectedPatientId,
    String? patientName,
    String? visitId,
    double? uploadProgress,
    bool? isComplete,
    String? error,
    List<PatientModel>? searchResults,
    bool? isSearching,
    int? chunksUploaded,
    bool? isUploading,
  }) {
    return RecordingState(
      selectedPatientId: selectedPatientId ?? this.selectedPatientId,
      patientName: patientName ?? this.patientName,
      visitId: visitId ?? this.visitId,
      uploadProgress: uploadProgress ?? this.uploadProgress,
      isComplete: isComplete ?? this.isComplete,
      error: error ?? this.error,
      searchResults: searchResults ?? this.searchResults,
      isSearching: isSearching ?? this.isSearching,
      chunksUploaded: chunksUploaded ?? this.chunksUploaded,
      isUploading: isUploading ?? this.isUploading,
    );
  }
}

class RecordingNotifier extends StateNotifier<RecordingState> {
  final _api = api;
  final _uploadService = UploadService();
  Timer? _debounce;

  RecordingNotifier() : super(const RecordingState());

  @override
  void dispose() {
    _debounce?.cancel();
    super.dispose();
  }

  Future<void> selectPatient(String patientId, String patientName) async {
    try {
      final response = await _api.post('/visits', data: {'patient_id': patientId});
      state = RecordingState(
        selectedPatientId: patientId,
        patientName: patientName,
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
          visitId: state.visitId,
          isComplete: true,
          chunksUploaded: state.chunksUploaded,
        );
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
            visitId: state.visitId,
            uploadProgress: progress,
          );
        },
      );
      state = RecordingState(
        selectedPatientId: state.selectedPatientId,
        patientName: state.patientName,
        visitId: state.visitId,
        isComplete: true,
      );
    } catch (e) {
      state = RecordingState(
        selectedPatientId: state.selectedPatientId,
        patientName: state.patientName,
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
