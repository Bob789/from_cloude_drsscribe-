class UserModel {
  final String id;
  final String email;
  final String name;
  final String role;
  final String? avatarUrl;
  final bool isActive;
  final String patientKeyType;
  final String preferredLanguage;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    this.avatarUrl,
    required this.isActive,
    this.patientKeyType = 'national_id',
    this.preferredLanguage = 'he',
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      name: json['name'],
      role: json['role'],
      avatarUrl: json['avatar_url'],
      isActive: json['is_active'] ?? true,
      patientKeyType: json['patient_key_type'] ?? 'national_id',
      preferredLanguage: json['preferred_language'] ?? 'he',
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'name': name,
    'role': role,
    'avatar_url': avatarUrl,
    'is_active': isActive,
    'patient_key_type': patientKeyType,
    'preferred_language': preferredLanguage,
    'created_at': createdAt.toIso8601String(),
  };
}
