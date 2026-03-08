import 'summary_model.dart';

class TranscriptionModel {
  final String id;
  final String? fullText;
  final String? status;
  final double? confidenceScore;

  TranscriptionModel({required this.id, this.fullText, this.status, this.confidenceScore});

  factory TranscriptionModel.fromJson(Map<String, dynamic> json) => TranscriptionModel(
    id: json['id'],
    fullText: json['full_text'],
    status: json['status'],
    confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
  );

  Map<String, dynamic> toMap() => {'id': id, 'full_text': fullText, 'status': status, 'confidence_score': confidenceScore};
}

class VisitModel {
  final String id;
  final int? displayId;
  final String doctorId;
  final String? startTime;
  final String? endTime;
  final String status;
  final String? source;
  final SummaryModel? summary;
  final TranscriptionModel? transcription;

  VisitModel({
    required this.id,
    this.displayId,
    required this.doctorId,
    this.startTime,
    this.endTime,
    required this.status,
    this.source,
    this.summary,
    this.transcription,
  });

  factory VisitModel.fromJson(Map<String, dynamic> json) => VisitModel(
    id: json['id'],
    displayId: json['display_id'],
    doctorId: json['doctor_id'],
    startTime: json['start_time'],
    endTime: json['end_time'],
    status: json['status'],
    source: json['source'],
    summary: json['summary'] != null ? SummaryModel.fromJson(json['summary']) : null,
    transcription: json['transcription'] != null ? TranscriptionModel.fromJson(json['transcription']) : null,
  );

  Map<String, dynamic> toMap() => {
    'id': id, 'display_id': displayId, 'doctor_id': doctorId, 'start_time': startTime,
    'end_time': endTime, 'status': status, 'source': source,
    'summary': summary?.toMap(), 'transcription': transcription?.toMap(),
  };
}
