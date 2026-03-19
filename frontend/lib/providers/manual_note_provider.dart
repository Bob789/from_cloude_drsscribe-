import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/services/api_client.dart';

class DiagnosisEntry {
  String code;
  String label;
  DiagnosisEntry({this.code = '', this.label = ''});
  Map<String, dynamic> toJson() => {'code': code, 'label': label};
}

class TagEntry {
  String? id;
  String tagType;
  String tagCode;
  String tagLabel;
  TagEntry({this.id, this.tagType = 'diagnosis', this.tagCode = '', this.tagLabel = ''});
  Map<String, dynamic> toJson() => {'tag_type': tagType, 'tag_code': tagCode, 'tag_label': tagLabel};
}

class CustomFieldDef {
  final int id;
  final String fieldName;
  final int fieldOrder;
  CustomFieldDef({required this.id, required this.fieldName, this.fieldOrder = 0});
  factory CustomFieldDef.fromJson(Map<String, dynamic> json) => CustomFieldDef(
    id: json['id'] is int ? json['id'] : int.parse(json['id'].toString()),
    fieldName: json['field_name']?.toString() ?? '',
    fieldOrder: json['field_order'] is int ? json['field_order'] : 0,
  );
}

class CustomFieldValue {
  final String fieldName;
  String value;
  CustomFieldValue({required this.fieldName, this.value = ''});
  Map<String, dynamic> toJson() => {'field_name': fieldName, 'value': value};
}

class ManualNoteState {
  final bool isLoading;
  final bool isSaved;
  final String? error;
  final List<DiagnosisEntry> diagnoses;
  final List<TagEntry> tags;
  final List<CustomFieldDef> fieldDefinitions;
  final List<CustomFieldValue> customFieldValues;

  const ManualNoteState({
    this.isLoading = false,
    this.isSaved = false,
    this.error,
    this.diagnoses = const [],
    this.tags = const [],
    this.fieldDefinitions = const [],
    this.customFieldValues = const [],
  });

  ManualNoteState copyWith({
    bool? isLoading,
    bool? isSaved,
    String? error,
    List<DiagnosisEntry>? diagnoses,
    List<TagEntry>? tags,
    List<CustomFieldDef>? fieldDefinitions,
    List<CustomFieldValue>? customFieldValues,
  }) {
    return ManualNoteState(
      isLoading: isLoading ?? this.isLoading,
      isSaved: isSaved ?? this.isSaved,
      error: error,
      diagnoses: diagnoses ?? this.diagnoses,
      tags: tags ?? this.tags,
      fieldDefinitions: fieldDefinitions ?? this.fieldDefinitions,
      customFieldValues: customFieldValues ?? this.customFieldValues,
    );
  }
}

class ManualNoteNotifier extends StateNotifier<ManualNoteState> {
  final _api = api;

  ManualNoteNotifier() : super(const ManualNoteState());

  Future<void> loadCustomFields() async {
    try {
      final response = await _api.get('/custom-fields');
      final rawList = response.data as List;
      final defs = rawList
          .map((e) => CustomFieldDef.fromJson(Map<String, dynamic>.from(e)))
          .toList();
      final values = defs.map((d) => CustomFieldValue(fieldName: d.fieldName)).toList();
      state = state.copyWith(fieldDefinitions: defs, customFieldValues: values);
      debugPrint('loadCustomFields OK: ${defs.length} fields');
    } catch (e) {
      debugPrint('loadCustomFields ERROR: $e');
    }
  }

  Future<void> addFieldDefinition(String fieldName) async {
    try {
      final response = await _api.post('/custom-fields', data: {
        'field_name': fieldName,
        'field_order': state.fieldDefinitions.length,
      });
      final newDef = CustomFieldDef.fromJson(Map<String, dynamic>.from(response.data));
      state = state.copyWith(
        fieldDefinitions: [...state.fieldDefinitions, newDef],
        customFieldValues: [...state.customFieldValues, CustomFieldValue(fieldName: newDef.fieldName)],
      );
      debugPrint('addFieldDefinition OK: ${newDef.fieldName}');
    } catch (e) {
      debugPrint('addFieldDefinition ERROR: $e');
    }
  }

  Future<void> removeFieldDefinition(int defId) async {
    try {
      await _api.delete('/custom-fields/$defId');
      final idx = state.fieldDefinitions.indexWhere((d) => d.id == defId);
      final defs = List<CustomFieldDef>.from(state.fieldDefinitions)..removeWhere((d) => d.id == defId);
      final vals = List<CustomFieldValue>.from(state.customFieldValues);
      if (idx >= 0 && idx < vals.length) vals.removeAt(idx);
      state = state.copyWith(fieldDefinitions: defs, customFieldValues: vals);
    } catch (e) {
      debugPrint('removeFieldDefinition ERROR: $e');
    }
  }

  void updateCustomFieldValue(int index, String value) {
    if (index < state.customFieldValues.length) {
      state.customFieldValues[index].value = value;
    }
  }

  void addDiagnosis() {
    state = state.copyWith(diagnoses: [...state.diagnoses, DiagnosisEntry()]);
  }

  void updateDiagnosis(int index, {String? code, String? label}) {
    final list = List<DiagnosisEntry>.from(state.diagnoses);
    if (index < list.length) {
      if (code != null) list[index].code = code;
      if (label != null) list[index].label = label;
      state = state.copyWith(diagnoses: list);
    }
  }

  void removeDiagnosis(int index) {
    final list = List<DiagnosisEntry>.from(state.diagnoses);
    if (index < list.length) {
      list.removeAt(index);
      state = state.copyWith(diagnoses: list);
    }
  }

  void addTag() {
    state = state.copyWith(tags: [...state.tags, TagEntry()]);
  }

  void updateTag(int index, {String? tagType, String? tagCode, String? tagLabel}) {
    final list = List<TagEntry>.from(state.tags);
    if (index < list.length) {
      if (tagType != null) list[index].tagType = tagType;
      if (tagCode != null) list[index].tagCode = tagCode;
      if (tagLabel != null) list[index].tagLabel = tagLabel;
      state = state.copyWith(tags: list);
    }
  }

  void removeTag(int index) {
    final list = List<TagEntry>.from(state.tags);
    if (index < list.length) {
      list.removeAt(index);
      state = state.copyWith(tags: list);
    }
  }

  Future<void> save({
    required String patientId,
    required String chiefComplaint,
    required String findings,
    required String treatmentPlan,
    required String recommendations,
    required String urgency,
    required String notes,
    List<Map<String, dynamic>>? questionnaireData,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final diagnosisList = state.diagnoses
          .where((d) => d.label.isNotEmpty)
          .map((d) => d.toJson())
          .toList();

      final tagsList = state.tags
          .where((t) => t.tagLabel.isNotEmpty)
          .map((t) => t.toJson())
          .toList();

      final customFieldsList = state.customFieldValues
          .where((f) => f.value.isNotEmpty)
          .map((f) => f.toJson())
          .toList();

      await _api.post('/visits/manual', data: {
        'patient_id': patientId,
        'chief_complaint': chiefComplaint.isNotEmpty ? chiefComplaint : null,
        'findings': findings.isNotEmpty ? findings : null,
        'diagnosis': diagnosisList.isNotEmpty ? diagnosisList : null,
        'treatment_plan': treatmentPlan.isNotEmpty ? treatmentPlan : null,
        'recommendations': recommendations.isNotEmpty ? recommendations : null,
        'urgency': urgency,
        'notes': notes.isNotEmpty ? notes : null,
        'tags': tagsList.isNotEmpty ? tagsList : null,
        'custom_fields': customFieldsList.isNotEmpty ? customFieldsList : null,
        'questionnaire_data': questionnaireData,
      });
      state = state.copyWith(isLoading: false, isSaved: true);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void reset() {
    final defs = state.fieldDefinitions;
    final freshValues = defs.map((d) => CustomFieldValue(fieldName: d.fieldName)).toList();
    state = ManualNoteState(fieldDefinitions: defs, customFieldValues: freshValues);
  }
}

final manualNoteProvider = StateNotifierProvider<ManualNoteNotifier, ManualNoteState>((ref) {
  return ManualNoteNotifier();
});
