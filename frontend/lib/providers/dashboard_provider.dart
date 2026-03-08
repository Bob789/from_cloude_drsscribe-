import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/models/dashboard_models.dart';

class DashboardState {
  final bool isLoading;
  final int todayVisits;
  final int pendingTranscriptions;
  final int totalPatients;
  final int visitsThisWeek;
  final int monthlyTranscriptions;
  final List<ChartDay> visitsByDay;
  final String? error;

  const DashboardState({
    this.isLoading = true,
    this.todayVisits = 0,
    this.pendingTranscriptions = 0,
    this.totalPatients = 0,
    this.visitsThisWeek = 0,
    this.monthlyTranscriptions = 0,
    this.visitsByDay = const [],
    this.error,
  });
}

class DashboardNotifier extends StateNotifier<DashboardState> {
  final _api = api;
  Timer? _refreshTimer;

  DashboardNotifier() : super(const DashboardState()) {
    _load();
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  Future<void> _load() async {
    try {
      final response = await _api.get('/dashboard/stats');
      final data = response.data;
      state = DashboardState(
        isLoading: false,
        todayVisits: data['today_visits'] ?? 0,
        pendingTranscriptions: data['pending_transcriptions'] ?? 0,
        totalPatients: data['total_patients'] ?? 0,
        visitsThisWeek: data['visits_this_week'] ?? 0,
        monthlyTranscriptions: data['monthly_transcriptions'] ?? 0,
        visitsByDay: (data['visits_by_day'] as List?)?.map((d) => ChartDay.fromJson(d)).toList() ?? [],
      );
    } catch (e) {
      if (state.isLoading) {
        state = DashboardState(isLoading: false, error: e.toString());
      }
    }
  }

  Future<void> refresh() => _load();

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}

final dashboardProvider = StateNotifierProvider<DashboardNotifier, DashboardState>((ref) => DashboardNotifier());
