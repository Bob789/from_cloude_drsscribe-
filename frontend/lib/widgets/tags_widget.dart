import 'package:flutter/material.dart';

class TagsWidget extends StatelessWidget {
  final List<dynamic> tags;
  final void Function(String tag)? onTagTap;

  const TagsWidget({super.key, required this.tags, this.onTagTap});

  @override
  Widget build(BuildContext context) {
    if (tags.isEmpty) return const SizedBox.shrink();

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: tags.map((tag) {
        final type = tag is Map ? (tag['tag_type'] ?? tag['code'] ?? '') : tag.toString();
        final label = tag is Map ? (tag['tag_label'] ?? tag['description'] ?? '') : tag.toString();
        final color = _colorForType(type);

        return ActionChip(
          avatar: Icon(_iconForType(type), size: 16, color: color),
          label: Text(label, style: TextStyle(color: color, fontSize: 13)),
          backgroundColor: color.withValues(alpha: 0.1),
          side: BorderSide(color: color.withValues(alpha: 0.3)),
          onPressed: onTagTap != null ? () => onTagTap!(label) : null,
        );
      }).toList(),
    );
  }

  Color _colorForType(String type) {
    switch (type.toLowerCase()) {
      case 'diagnosis':
        return Colors.red;
      case 'treatment':
        return Colors.blue;
      case 'symptom':
        return Colors.amber.shade800;
      case 'urgency':
        return Colors.deepOrange;
      default:
        return Colors.grey;
    }
  }

  IconData _iconForType(String type) {
    switch (type.toLowerCase()) {
      case 'diagnosis':
        return Icons.local_hospital;
      case 'treatment':
        return Icons.medical_services;
      case 'symptom':
        return Icons.sick;
      case 'urgency':
        return Icons.warning;
      default:
        return Icons.label;
    }
  }
}
