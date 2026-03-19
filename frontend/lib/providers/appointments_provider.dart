import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/models/appointment_model.dart';
import 'package:medscribe_ai/services/api_client.dart';

enum CalendarViewMode { weekly, monthly }

class AppointmentsState {
  final List<AppointmentModel> appointments;
  final List<HolidayModel> holidays;
  final List<Map<String, dynamic>> googleEvents;
  final bool calendarConnected;
  final bool isLoading;
  final String? error;
  final DateTime selectedDate;
  final DateTime weekStart;
  final CalendarViewMode viewMode;
  final DateTime selectedMonth;

  AppointmentsState({
    this.appointments = const [],
    this.holidays = const [],
    this.googleEvents = const [],
    this.calendarConnected = false,
    this.isLoading = true,
    this.error,
    DateTime? selectedDate,
    DateTime? weekStart,
    this.viewMode = CalendarViewMode.weekly,
    DateTime? selectedMonth,
  })  : selectedDate = selectedDate ?? DateTime.now(),
        weekStart = weekStart ?? _calcWeekStart(DateTime.now()),
        selectedMonth = selectedMonth ?? DateTime(DateTime.now().year, DateTime.now().month);

  static DateTime _calcWeekStart(DateTime date) {
    final diff = (date.weekday % 7);
    return DateTime(date.year, date.month, date.day).subtract(Duration(days: diff));
  }

  AppointmentsState copyWith({
    List<AppointmentModel>? appointments,
    List<HolidayModel>? holidays,
    List<Map<String, dynamic>>? googleEvents,
    bool? calendarConnected,
    bool? isLoading,
    String? error,
    DateTime? selectedDate,
    DateTime? weekStart,
    CalendarViewMode? viewMode,
    DateTime? selectedMonth,
  }) {
    return AppointmentsState(
      appointments: appointments ?? this.appointments,
      holidays: holidays ?? this.holidays,
      googleEvents: googleEvents ?? this.googleEvents,
      calendarConnected: calendarConnected ?? this.calendarConnected,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      selectedDate: selectedDate ?? this.selectedDate,
      weekStart: weekStart ?? this.weekStart,
      viewMode: viewMode ?? this.viewMode,
      selectedMonth: selectedMonth ?? this.selectedMonth,
    );
  }
}

class AppointmentsNotifier extends StateNotifier<AppointmentsState> {
  final _api = api;

  AppointmentsNotifier() : super(AppointmentsState()) {
    _init();
  }

  Future<void> _init() async {
    await Future.wait([loadWeek(state.weekStart), _loadCalendarStatus()]);
  }

  Future<void> _loadCalendarStatus() async {
    try {
      final res = await _api.get('/appointments/calendar/status');
      state = state.copyWith(calendarConnected: res.data['connected'] ?? false);
    } catch (_) {}
  }

  void setViewMode(CalendarViewMode mode) {
    state = state.copyWith(viewMode: mode);
    if (mode == CalendarViewMode.monthly) {
      loadMonth(state.selectedMonth);
    } else {
      loadWeek(state.weekStart);
    }
  }

  Future<void> loadWeek(DateTime weekStart) async {
    state = state.copyWith(isLoading: true, weekStart: weekStart);
    try {
      final weekEnd = weekStart.add(const Duration(days: 6));
      final from = _fmt(weekStart);
      final to = _fmt(weekEnd);

      final results = await Future.wait([
        _api.get('/appointments', queryParameters: {'date_from': from, 'date_to': to}),
        _api.get('/appointments/holidays', queryParameters: {'from': from, 'to': to}),
      ]);

      final appts = (results[0].data as List).map((j) => AppointmentModel.fromJson(j)).toList();
      final holidays = (results[1].data as List).map((j) => HolidayModel.fromJson(j)).toList();

      state = state.copyWith(appointments: appts, holidays: holidays, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadMonth(DateTime month) async {
    final monthStart = DateTime(month.year, month.month, 1);
    final monthEnd = DateTime(month.year, month.month + 1, 0);
    state = state.copyWith(isLoading: true, selectedMonth: monthStart);
    try {
      final from = _fmt(monthStart);
      final to = _fmt(monthEnd);

      final results = await Future.wait([
        _api.get('/appointments', queryParameters: {'date_from': from, 'date_to': to}),
        _api.get('/appointments/holidays', queryParameters: {'from': from, 'to': to}),
      ]);

      final appts = (results[0].data as List).map((j) => AppointmentModel.fromJson(j)).toList();
      final holidays = (results[1].data as List).map((j) => HolidayModel.fromJson(j)).toList();

      state = state.copyWith(appointments: appts, holidays: holidays, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void selectDate(DateTime date) {
    final newWeekStart = AppointmentsState._calcWeekStart(date);
    state = state.copyWith(selectedDate: date, weekStart: newWeekStart);
  }

  void previousWeek() {
    final newStart = state.weekStart.subtract(const Duration(days: 7));
    loadWeek(newStart);
  }

  void nextWeek() {
    final newStart = state.weekStart.add(const Duration(days: 7));
    loadWeek(newStart);
  }

  void previousMonth() {
    final m = state.selectedMonth;
    loadMonth(DateTime(m.year, m.month - 1));
  }

  void nextMonth() {
    final m = state.selectedMonth;
    loadMonth(DateTime(m.year, m.month + 1));
  }

  Future<void> createAppointment({
    String? patientId,
    required String title,
    String? description,
    required DateTime startTime,
    int durationMinutes = 20,
    int reminderMinutes = 60,
    bool syncToGoogle = true,
  }) async {
    await _api.post('/appointments', data: {
      'patient_id': patientId,
      'title': title,
      'description': description,
      'start_time': startTime.toIso8601String(),
      'duration_minutes': durationMinutes,
      'reminder_minutes': reminderMinutes,
      'sync_to_google': syncToGoogle,
    });
    if (state.viewMode == CalendarViewMode.monthly) {
      await loadMonth(state.selectedMonth);
    } else {
      await loadWeek(state.weekStart);
    }
  }

  Future<void> updateAppointment(int id, Map<String, dynamic> data) async {
    await _api.put('/appointments/$id', data: data);
    if (state.viewMode == CalendarViewMode.monthly) {
      await loadMonth(state.selectedMonth);
    } else {
      await loadWeek(state.weekStart);
    }
  }

  Future<void> deleteAppointment(int id) async {
    await _api.delete('/appointments/$id');
    if (state.viewMode == CalendarViewMode.monthly) {
      await loadMonth(state.selectedMonth);
    } else {
      await loadWeek(state.weekStart);
    }
  }

  Future<String?> getCalendarAuthUrl() async {
    try {
      final res = await _api.get('/appointments/calendar/auth-url');
      return res.data['auth_url'];
    } catch (_) {
      return null;
    }
  }

  Future<void> loadGoogleEvents() async {
    if (!state.calendarConnected) return;
    try {
      final res = await _api.get('/appointments/google/today');
      state = state.copyWith(googleEvents: List<Map<String, dynamic>>.from(res.data));
    } catch (_) {}
  }

  String _fmt(DateTime d) => '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
}

final appointmentsProvider = StateNotifierProvider<AppointmentsNotifier, AppointmentsState>(
  (ref) => AppointmentsNotifier(),
);
