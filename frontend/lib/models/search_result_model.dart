class SearchResultModel {
  final String? chiefComplaint;
  final String? findings;
  final String? fullText;
  final String? urgency;
  final String? patientName;
  final dynamic patientDisplayId;
  final List<String> tags;
  final String? createdAt;
  final String? formattedChiefComplaint;
  final String? formattedFindings;
  final String? formattedFullText;

  SearchResultModel({
    this.chiefComplaint,
    this.findings,
    this.fullText,
    this.urgency,
    this.patientName,
    this.patientDisplayId,
    this.tags = const [],
    this.createdAt,
    this.formattedChiefComplaint,
    this.formattedFindings,
    this.formattedFullText,
  });

  factory SearchResultModel.fromJson(Map<String, dynamic> json) {
    final formatted = json['_formatted'] as Map<String, dynamic>?;
    return SearchResultModel(
      chiefComplaint: json['chief_complaint'],
      findings: json['findings'],
      fullText: json['full_text'],
      urgency: json['urgency']?.toString(),
      patientName: json['patient_name']?.toString(),
      patientDisplayId: json['patient_display_id'],
      tags: (json['tags'] as List?)?.map((t) => t.toString()).toList() ?? [],
      createdAt: json['created_at']?.toString(),
      formattedChiefComplaint: formatted?['chief_complaint'],
      formattedFindings: formatted?['findings'],
      formattedFullText: formatted?['full_text'],
    );
  }

  String? get displayChiefComplaint => formattedChiefComplaint ?? chiefComplaint;
  String? get displayFindings => formattedFindings ?? findings;
  String? get displayFullText => formattedFullText ?? fullText;
}
