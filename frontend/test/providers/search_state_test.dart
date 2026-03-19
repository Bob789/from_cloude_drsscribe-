import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/providers/search_provider.dart';
import 'package:medscribe_ai/models/search_result_model.dart';

void main() {
  group('SearchState', () {
    test('default state is empty and not loading', () {
      const state = SearchState();
      expect(state.isLoading, false);
      expect(state.results, isEmpty);
      expect(state.total, 0);
      expect(state.error, isNull);
    });

    test('holds results correctly', () {
      final results = [
        SearchResultModel.fromJson({'chief_complaint': 'כאב ראש', 'tags': []}),
        SearchResultModel.fromJson({'chief_complaint': 'כאב גב', 'tags': ['גב']}),
      ];

      final state = SearchState(results: results, total: 2);

      expect(state.results, hasLength(2));
      expect(state.total, 2);
      expect(state.results[0].chiefComplaint, 'כאב ראש');
    });
  });

  group('TagsState', () {
    test('default state is empty and not loading', () {
      const state = TagsState();
      expect(state.isLoading, false);
      expect(state.tags, isEmpty);
    });
  });
}
