class PatientModel {
  final String id;
  final int displayId;
  final String name;
  final String? idNumber;
  final String? dob;
  final String? phone;
  final String? email;
  final String? bloodType;
  final List<String>? allergies;
  final String? insuranceInfo;
  final String? notes;
  final DateTime createdAt;

  PatientModel({
    required this.id,
    required this.displayId,
    required this.name,
    this.idNumber,
    this.dob,
    this.phone,
    this.email,
    this.bloodType,
    this.allergies,
    this.insuranceInfo,
    this.notes,
    required this.createdAt,
  });

  factory PatientModel.fromJson(Map<String, dynamic> json) {
    return PatientModel(
      id: json['id'],
      displayId: (json['display_id'] as num?)?.toInt() ?? 0,
      name: json['name'],
      idNumber: json['id_number'],
      dob: json['dob'],
      phone: json['phone'],
      email: json['email'],
      bloodType: json['blood_type'],
      allergies: json['allergies'] != null ? List<String>.from(json['allergies']) : null,
      insuranceInfo: json['insurance_info'],
      notes: json['notes'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'id_number': idNumber,
    'dob': dob,
    'phone': phone,
    'email': email,
    'blood_type': bloodType,
    'allergies': allergies,
    'insurance_info': insuranceInfo,
    'notes': notes,
  };
}
