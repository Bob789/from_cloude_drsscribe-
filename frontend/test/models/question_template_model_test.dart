import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/models/question_template_model.dart';

void main() {
  group('QuestionField', () {
    test('fromJson parses all fields', () {
      final json = {
        'label': 'לחץ דם',
        'type': 'number',
        'required': true,
        'options': null,
      };

      final field = QuestionField.fromJson(json);

      expect(field.label, 'לחץ דם');
      expect(field.type, 'number');
      expect(field.required, true);
      expect(field.options, isNull);
      expect(field.value, '');
    });

    test('fromJson with select options', () {
      final json = {
        'label': 'דחיפות',
        'type': 'select',
        'required': false,
        'options': ['נמוכה', 'בינונית', 'גבוהה'],
      };

      final field = QuestionField.fromJson(json);

      expect(field.type, 'select');
      expect(field.options, hasLength(3));
      expect(field.options!.first, 'נמוכה');
    });

    test('defaults for missing fields', () {
      final field = QuestionField.fromJson({'label': 'test'});

      expect(field.type, 'text');
      expect(field.required, false);
      expect(field.value, '');
    });

    test('toJson creates correct map', () {
      final field = QuestionField(label: 'BP', type: 'number', required: true);
      final json = field.toJson();

      expect(json['label'], 'BP');
      expect(json['type'], 'number');
      expect(json['required'], true);
      expect(json.containsKey('options'), isFalse);
    });

    test('toAnswerJson includes value', () {
      final field = QuestionField(label: 'BP', type: 'number');
      field.value = '120/80';

      final answer = field.toAnswerJson();

      expect(answer['label'], 'BP');
      expect(answer['value'], '120/80');
    });
  });

  group('QuestionTemplateModel', () {
    test('fromJson parses complete template', () {
      final json = {
        'id': 1,
        'name': 'קרדיולוגיה',
        'description': 'שאלון לב',
        'icon': 'heart',
        'color': '#FF0000',
        'questions': [
          {'label': 'לחץ דם', 'type': 'number', 'required': true},
          {'label': 'כאבים', 'type': 'boolean'},
        ],
        'is_shared': true,
        'usage_count': 42,
        'created_at': '2026-03-01T00:00:00Z',
      };

      final template = QuestionTemplateModel.fromJson(json);

      expect(template.id, 1);
      expect(template.name, 'קרדיולוגיה');
      expect(template.icon, 'heart');
      expect(template.color, '#FF0000');
      expect(template.questions, hasLength(2));
      expect(template.questions[0].label, 'לחץ דם');
      expect(template.questions[0].required, true);
      expect(template.isShared, true);
      expect(template.usageCount, 42);
    });

    test('handles empty questions list', () {
      final json = {
        'id': 2,
        'name': 'ריק',
        'created_at': '2026-01-01T00:00:00Z',
      };

      final template = QuestionTemplateModel.fromJson(json);

      expect(template.questions, isEmpty);
      expect(template.icon, 'clipboard');
      expect(template.color, '#3B82F6');
    });
  });
}
