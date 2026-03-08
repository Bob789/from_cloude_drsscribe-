import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';

class PatientFileModel {
  final int id;
  final String patientId;
  final String fileName;
  final int? fileSize;
  final String? mimeType;
  final String category;
  final String? description;
  final DateTime createdAt;

  PatientFileModel({
    required this.id,
    required this.patientId,
    required this.fileName,
    this.fileSize,
    this.mimeType,
    required this.category,
    this.description,
    required this.createdAt,
  });

  factory PatientFileModel.fromJson(Map<String, dynamic> json) {
    return PatientFileModel(
      id: json['id'],
      patientId: json['patient_id']?.toString() ?? '',
      fileName: json['file_name'] ?? '',
      fileSize: json['file_size'],
      mimeType: json['mime_type'],
      category: json['category'] ?? 'other',
      description: json['description'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  String get fileSizeFormatted {
    if (fileSize == null) return '';
    if (fileSize! < 1024) return '$fileSize B';
    if (fileSize! < 1024 * 1024) return '${(fileSize! / 1024).toStringAsFixed(1)} KB';
    return '${(fileSize! / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  String get categoryLabel {
    switch (category) {
      case 'lab_results': return 'upload.category_lab'.tr();
      case 'imaging': return 'upload.category_imaging'.tr();
      case 'discharge': return 'upload.category_discharge'.tr();
      case 'referral': return 'upload.category_referral'.tr();
      case 'prescription': return 'upload.category_prescription'.tr();
      case 'insurance': return 'upload.category_insurance'.tr();
      case 'consent': return 'upload.category_consent'.tr();
      case 'other': return 'upload.category_other'.tr();
      default: return category;
    }
  }

  IconData get categoryIcon {
    switch (category) {
      case 'lab_results': return Icons.biotech_rounded;
      case 'imaging': return Icons.image_rounded;
      case 'discharge': return Icons.description_rounded;
      case 'referral': return Icons.send_rounded;
      case 'prescription': return Icons.medication_rounded;
      case 'insurance': return Icons.shield_rounded;
      case 'consent': return Icons.handshake_rounded;
      case 'other': return Icons.attach_file_rounded;
      default: return Icons.insert_drive_file_rounded;
    }
  }

  bool get isImage => mimeType != null && mimeType!.startsWith('image/');
  bool get isPdf => mimeType == 'application/pdf';
}
