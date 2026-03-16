import 'tag_model.dart';

class SummaryModel {
  final String id;
  final int? displayId;
  final String? chiefComplaint;
  final String? findings;
  final dynamic diagnosis;
  final String? treatmentPlan;
  final String? recommendations;
  final String? urgency;
  final String? source;
  final String? notes;
  final List<dynamic>? customFields;
  final List<TagModel> tags;

  SummaryModel({
    required this.id,
    this.displayId,
    this.chiefComplaint,
    this.findings,
    this.diagnosis,
    this.treatmentPlan,
    this.recommendations,
    this.urgency,
    this.source,
    this.notes,
    this.customFields,
    this.tags = const [],
  });

  factory SummaryModel.fromJson(Map<String, dynamic> json) => SummaryModel(
    id: json['id'],
    displayId: (json['display_id'] as num?)?.toInt(),
    chiefComplaint: json['chief_complaint'],
    findings: json['findings'],
    diagnosis: json['diagnosis'],
    treatmentPlan: json['treatment_plan'],
    recommendations: json['recommendations'],
    urgency: json['urgency'],
    source: json['source'],
    notes: json['notes'],
    customFields: json['custom_fields'] as List?,
    tags: (json['tags'] as List?)?.map((t) => TagModel.fromJson(t)).toList() ?? [],
  );

  Map<String, dynamic> toMap() => {
    'id': id, 'display_id': displayId, 'chief_complaint': chiefComplaint, 'findings': findings,
    'diagnosis': diagnosis, 'treatment_plan': treatmentPlan, 'recommendations': recommendations,
    'urgency': urgency, 'source': source, 'notes': notes, 'custom_fields': customFields,
    'tags': tags.map((t) => {'id': t.id, 'tag_type': t.tagType, 'tag_code': t.tagCode, 'tag_label': t.tagLabel}).toList(),
  };
}
