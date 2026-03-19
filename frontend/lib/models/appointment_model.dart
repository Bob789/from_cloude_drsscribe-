class AppointmentModel {
  final int id;
  final String? patientId;
  final String? patientName;
  final String title;
  final String? description;
  final DateTime startTime;
  final DateTime endTime;
  final int durationMinutes;
  final String status;
  final int reminderMinutes;
  final bool syncedToGoogle;
  final String? googleEventId;
  final DateTime createdAt;

  AppointmentModel({
    required this.id,
    this.patientId,
    this.patientName,
    required this.title,
    this.description,
    required this.startTime,
    required this.endTime,
    required this.durationMinutes,
    required this.status,
    required this.reminderMinutes,
    required this.syncedToGoogle,
    this.googleEventId,
    required this.createdAt,
  });

  factory AppointmentModel.fromJson(Map<String, dynamic> json) {
    return AppointmentModel(
      id: (json['id'] as num?)?.toInt() ?? 0,
      patientId: json['patient_id'],
      patientName: json['patient_name'],
      title: json['title'] ?? '',
      description: json['description'],
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      durationMinutes: (json['duration_minutes'] as num?)?.toInt() ?? 20,
      status: json['status'] ?? 'scheduled',
      reminderMinutes: (json['reminder_minutes'] as num?)?.toInt() ?? 60,
      syncedToGoogle: json['synced_to_google'] ?? false,
      googleEventId: json['google_event_id'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class HolidayModel {
  final String date;
  final String name;

  HolidayModel({required this.date, required this.name});

  factory HolidayModel.fromJson(Map<String, dynamic> json) {
    return HolidayModel(date: json['date'], name: json['name']);
  }
}
