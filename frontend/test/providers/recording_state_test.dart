import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/providers/recording_provider.dart';

void main() {
  group('RecordingState', () {
    test('default state has correct values', () {
      const state = RecordingState();

      expect(state.selectedPatientId, isNull);
      expect(state.patientName, isNull);
      expect(state.patientDisplayId, isNull);
      expect(state.visitId, isNull);
      expect(state.isComplete, false);
      expect(state.error, isNull);
      expect(state.searchResults, isEmpty);
      expect(state.isSearching, false);
      expect(state.chunksUploaded, 0);
      expect(state.isUploading, false);
      expect(state.transcriptionStatus, isNull);
      expect(state.summaryStatus, isNull);
    });

    test('copyWith preserves unmodified fields', () {
      const state = RecordingState(
        selectedPatientId: 'p-1',
        patientName: 'דני',
        patientDisplayId: 5,
        visitId: 'v-1',
      );

      final updated = state.copyWith(isComplete: true);

      expect(updated.selectedPatientId, 'p-1');
      expect(updated.patientName, 'דני');
      expect(updated.patientDisplayId, 5);
      expect(updated.visitId, 'v-1');
      expect(updated.isComplete, true);
    });

    test('copyWith updates transcription/summary status', () {
      const state = RecordingState(transcriptionStatus: 'processing');

      final updated = state.copyWith(
        transcriptionStatus: 'done',
        summaryStatus: 'processing',
      );

      expect(updated.transcriptionStatus, 'done');
      expect(updated.summaryStatus, 'processing');
    });

    test('copyWith updates chunk count', () {
      const state = RecordingState(chunksUploaded: 3);
      final updated = state.copyWith(chunksUploaded: 4);
      expect(updated.chunksUploaded, 4);
    });
  });
}
