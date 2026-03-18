class QuestionField {
  final String label;
  final String type;
  final bool required;
  final List<String>? options;
  String value;

  QuestionField({
    required this.label,
    this.type = 'text',
    this.required = false,
    this.options,
    this.value = '',
  });

  factory QuestionField.fromJson(Map<String, dynamic> json) => QuestionField(
    label: json['label'] ?? '',
    type: json['type'] ?? 'text',
    required: json['required'] == true,
    options: json['options'] != null ? List<String>.from(json['options']) : null,
    value: json['value'] ?? '',
  );

  Map<String, dynamic> toJson() => {
    'label': label,
    'type': type,
    'required': required,
    if (options != null) 'options': options,
  };

  Map<String, dynamic> toAnswerJson() => {
    'label': label,
    'type': type,
    'value': value,
  };
}

class QuestionTemplateModel {
  final int id;
  final String name;
  final String? description;
  final String icon;
  final String color;
  final List<QuestionField> questions;
  final bool isShared;
  final int usageCount;
  final DateTime createdAt;

  QuestionTemplateModel({
    required this.id,
    required this.name,
    this.description,
    this.icon = 'clipboard',
    this.color = '#3B82F6',
    required this.questions,
    this.isShared = false,
    this.usageCount = 0,
    required this.createdAt,
  });

  factory QuestionTemplateModel.fromJson(Map<String, dynamic> json) => QuestionTemplateModel(
    id: (json['id'] as num?)?.toInt() ?? 0,
    name: json['name'] ?? '',
    description: json['description'],
    icon: json['icon'] ?? 'clipboard',
    color: json['color'] ?? '#3B82F6',
    questions: (json['questions'] as List?)
        ?.map((q) => QuestionField.fromJson(Map<String, dynamic>.from(q)))
        .toList() ?? [],
    isShared: json['is_shared'] == true,
    usageCount: (json['usage_count'] as num?)?.toInt() ?? 0,
    createdAt: DateTime.parse(json['created_at']),
  );
}
