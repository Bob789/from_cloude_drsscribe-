import 'package:flutter_test/flutter_test.dart';
import 'package:medscribe_ai/models/tag_model.dart';

void main() {
  group('TagModel', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': '123',
        'tag_type': 'medication',
        'tag_code': 'N02BE01',
        'tag_label': 'פרצטמול',
        'count': 15,
      };

      final tag = TagModel.fromJson(json);

      expect(tag.id, '123');
      expect(tag.tagType, 'medication');
      expect(tag.tagCode, 'N02BE01');
      expect(tag.tagLabel, 'פרצטמול');
      expect(tag.count, 15);
    });

    test('handles null count', () {
      final json = {
        'tag_type': 'symptom',
        'tag_code': '',
        'tag_label': 'כאב ראש',
      };

      final tag = TagModel.fromJson(json);
      expect(tag.count, isNull);
      expect(tag.id, isNull);
    });

    test('toJson creates correct map', () {
      final tag = TagModel(tagType: 'condition', tagCode: 'M54', tagLabel: 'כאב גב');
      final json = tag.toJson();

      expect(json['tag_type'], 'condition');
      expect(json['tag_code'], 'M54');
      expect(json['tag_label'], 'כאב גב');
      expect(json.containsKey('id'), isFalse);
      expect(json.containsKey('count'), isFalse);
    });
  });
}
