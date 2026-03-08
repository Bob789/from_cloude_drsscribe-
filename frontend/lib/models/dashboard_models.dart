class ChartPatient {
  final String name;
  final String? time;
  final dynamic patientDisplayId;

  ChartPatient({required this.name, this.time, this.patientDisplayId});

  factory ChartPatient.fromJson(Map<String, dynamic> json) => ChartPatient(
    name: json['name'] ?? '',
    time: json['time'],
    patientDisplayId: json['patient_display_id'],
  );
}

class ChartDay {
  final String date;
  final String dayName;
  final int count;
  final List<ChartPatient> patients;

  ChartDay({required this.date, required this.dayName, required this.count, this.patients = const []});

  factory ChartDay.fromJson(Map<String, dynamic> json) => ChartDay(
    date: json['date'] ?? '',
    dayName: json['day_name'] ?? '',
    count: json['count'] ?? 0,
    patients: (json['patients'] as List?)?.map((p) => ChartPatient.fromJson(p)).toList() ?? [],
  );
}
