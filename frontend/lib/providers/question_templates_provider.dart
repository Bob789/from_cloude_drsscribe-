import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/models/question_template_model.dart';
import 'package:medscribe_ai/services/api_client.dart';

class QuestionTemplatesState {
  final bool isLoading;
  final String? error;
  final List<QuestionTemplateModel> templates;

  const QuestionTemplatesState({
    this.isLoading = false,
    this.error,
    this.templates = const [],
  });

  QuestionTemplatesState copyWith({
    bool? isLoading,
    String? error,
    List<QuestionTemplateModel>? templates,
  }) => QuestionTemplatesState(
    isLoading: isLoading ?? this.isLoading,
    error: error,
    templates: templates ?? this.templates,
  );
}

class QuestionTemplatesNotifier extends StateNotifier<QuestionTemplatesState> {
  final _api = api;

  QuestionTemplatesNotifier() : super(const QuestionTemplatesState());

  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _api.get('/question-templates');
      final list = (response.data as List)
          .map((e) => QuestionTemplateModel.fromJson(Map<String, dynamic>.from(e)))
          .toList();
      state = state.copyWith(isLoading: false, templates: list);
    } catch (e) {
      debugPrint('loadTemplates ERROR: $e');
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<QuestionTemplateModel?> create({
    required String name,
    String? description,
    String icon = 'clipboard',
    String color = '#3B82F6',
    required List<Map<String, dynamic>> questions,
    bool isShared = false,
  }) async {
    try {
      final response = await _api.post('/question-templates', data: {
        'name': name,
        'description': description,
        'icon': icon,
        'color': color,
        'questions': questions,
        'is_shared': isShared,
      });
      final created = QuestionTemplateModel.fromJson(Map<String, dynamic>.from(response.data));
      state = state.copyWith(templates: [created, ...state.templates]);
      return created;
    } catch (e) {
      debugPrint('createTemplate ERROR: $e');
      return null;
    }
  }

  Future<bool> update(int id, Map<String, dynamic> data) async {
    try {
      final response = await _api.put('/question-templates/$id', data: data);
      final updated = QuestionTemplateModel.fromJson(Map<String, dynamic>.from(response.data));
      state = state.copyWith(
        templates: state.templates.map((t) => t.id == id ? updated : t).toList(),
      );
      return true;
    } catch (e) {
      debugPrint('updateTemplate ERROR: $e');
      return false;
    }
  }

  Future<bool> delete(int id) async {
    try {
      await _api.delete('/question-templates/$id');
      state = state.copyWith(
        templates: state.templates.where((t) => t.id != id).toList(),
      );
      return true;
    } catch (e) {
      debugPrint('deleteTemplate ERROR: $e');
      return false;
    }
  }

  Future<QuestionTemplateModel?> duplicate(int id) async {
    try {
      final response = await _api.post('/question-templates/$id/duplicate');
      final copy = QuestionTemplateModel.fromJson(Map<String, dynamic>.from(response.data));
      state = state.copyWith(templates: [copy, ...state.templates]);
      return copy;
    } catch (e) {
      debugPrint('duplicateTemplate ERROR: $e');
      return null;
    }
  }
}

final questionTemplatesProvider =
    StateNotifierProvider<QuestionTemplatesNotifier, QuestionTemplatesState>((ref) {
  return QuestionTemplatesNotifier();
});
