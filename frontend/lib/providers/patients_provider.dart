import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/services/api_client.dart';

class PatientsState {
  final bool isLoading;
  final List<PatientModel> patients;
  final String? error;
  final int page;
  final int totalPages;

  const PatientsState({
    this.isLoading = false,
    this.patients = const [],
    this.error,
    this.page = 1,
    this.totalPages = 1,
  });

  T when<T>({
    required T Function() loading,
    required T Function(String error) error,
    required T Function(List<PatientModel> patients) data,
  }) {
    if (isLoading) return loading();
    if (this.error != null) return error(this.error!);
    return data(patients);
  }
}

class PatientsNotifier extends StateNotifier<PatientsState> {
  final _api = api;

  PatientsNotifier() : super(const PatientsState(isLoading: true)) {
    loadPatients();
  }

  Future<void> loadPatients({int page = 1}) async {
    state = PatientsState(isLoading: true, patients: state.patients);
    try {
      final response = await _api.get('/patients', queryParameters: {'page': page, 'per_page': 20});
      final data = response.data;
      final patients = (data['items'] as List).map((e) => PatientModel.fromJson(e)).toList();
      state = PatientsState(patients: patients, page: data['page'], totalPages: data['pages']);
    } catch (e) {
      state = PatientsState(error: e.toString());
    }
  }

  Future<void> search(String query) async {
    if (query.isEmpty) {
      await loadPatients();
      return;
    }
    state = PatientsState(isLoading: true, patients: state.patients);
    try {
      final response = await _api.get('/patients/search', queryParameters: {'q': query});
      final patients = (response.data as List).map((e) => PatientModel.fromJson(e)).toList();
      state = PatientsState(patients: patients);
    } catch (e) {
      state = PatientsState(error: e.toString());
    }
  }
}

final patientsProvider = StateNotifierProvider<PatientsNotifier, PatientsState>((ref) {
  return PatientsNotifier();
});
