class TagModel {
  final String? id;
  final String tagType;
  final String tagCode;
  final String tagLabel;
  final int? count;

  TagModel({this.id, required this.tagType, required this.tagCode, required this.tagLabel, this.count});

  factory TagModel.fromJson(Map<String, dynamic> json) => TagModel(
    id: json['id']?.toString(),
    tagType: json['tag_type'] ?? '',
    tagCode: json['tag_code'] ?? '',
    tagLabel: json['tag_label'] ?? '',
    count: (json['count'] as num?)?.toInt(),
  );

  Map<String, dynamic> toJson() => {'tag_type': tagType, 'tag_code': tagCode, 'tag_label': tagLabel};
}
