import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/providers/patients_provider.dart';
import 'package:medscribe_ai/models/patient_model.dart';

void main() {
  group('PatientsState', () {
    test('default state is loading', () {
      const state = PatientsState(isLoading: true);
      expect(state.isLoading, true);
      expect(state.patients, isEmpty);
      expect(state.error, isNull);
    });

    test('when() returns loading callback when isLoading', () {
      const state = PatientsState(isLoading: true);
      final result = state.when(
        loading: () => 'LOADING',
        error: (e) => 'ERROR: $e',
        data: (p) => 'DATA: ${p.length}',
      );
      expect(result, 'LOADING');
    });

    test('when() returns error callback when error exists', () {
      const state = PatientsState(error: 'network error');
      final result = state.when(
        loading: () => 'LOADING',
        error: (e) => 'ERROR: $e',
        data: (p) => 'DATA',
      );
      expect(result, 'ERROR: network error');
    });

    test('when() returns data callback with patients', () {
      final patients = [
        PatientModel(id: '1', displayId: 1, name: 'Test', createdAt: DateTime.now()),
      ];
      final state = PatientsState(patients: patients);

      final result = state.when(
        loading: () => 'LOADING',
        error: (e) => 'ERROR',
        data: (p) => 'DATA: ${p.length}',
      );
      expect(result, 'DATA: 1');
    });
  });
}
