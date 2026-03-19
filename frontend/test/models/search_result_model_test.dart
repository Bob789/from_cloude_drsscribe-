import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/models/search_result_model.dart';

void main() {
  group('SearchResultModel.fromJson', () {
    test('parses complete result with formatted fields', () {
      final json = {
        'chief_complaint': 'כאבי גב',
        'findings': 'רגישות L4-L5',
        'full_text': 'תמלול מלא',
        'urgency': 'high',
        'patient_name': 'דני כהן',
        'patient_display_id': 5,
        'tags': ['כאב', 'גב'],
        'created_at': '2026-03-18T10:00:00Z',
        '_formatted': {
          'chief_complaint': '<em>כאבי</em> גב',
          'findings': 'רגישות <em>L4-L5</em>',
          'full_text': null,
        },
      };

      final result = SearchResultModel.fromJson(json);

      expect(result.chiefComplaint, 'כאבי גב');
      expect(result.urgency, 'high');
      expect(result.patientName, 'דני כהן');
      expect(result.tags, hasLength(2));
      expect(result.displayChiefComplaint, '<em>כאבי</em> גב');
      expect(result.displayFindings, 'רגישות <em>L4-L5</em>');
      expect(result.displayFullText, 'תמלול מלא'); // fallback to non-formatted
    });

    test('handles missing _formatted', () {
      final json = {
        'chief_complaint': 'כאב ראש',
        'tags': [],
      };

      final result = SearchResultModel.fromJson(json);

      expect(result.displayChiefComplaint, 'כאב ראש');
      expect(result.formattedChiefComplaint, isNull);
    });

    test('handles null tags as empty list', () {
      final json = <String, dynamic>{
        'chief_complaint': 'test',
      };

      final result = SearchResultModel.fromJson(json);
      expect(result.tags, isEmpty);
    });
  });
}
