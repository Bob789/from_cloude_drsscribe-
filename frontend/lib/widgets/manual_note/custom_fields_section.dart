import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/providers/manual_note_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class CustomFieldsSection extends ConsumerStatefulWidget {
  const CustomFieldsSection({super.key});

  @override
  ConsumerState<CustomFieldsSection> createState() => _CustomFieldsSectionState();
}

class _CustomFieldsSectionState extends ConsumerState<CustomFieldsSection> {
  List<TextEditingController> _controllers = [];
  final _newFieldCtrl = TextEditingController();

  @override
  void dispose() {
    for (final c in _controllers) { c.dispose(); }
    _newFieldCtrl.dispose();
    super.dispose();
  }

  void _addNewField() async {
    final name = _newFieldCtrl.text.trim();
    if (name.isNotEmpty) {
      _newFieldCtrl.clear();
      await ref.read(manualNoteProvider.notifier).addFieldDefinition(name);
      _controllers.add(TextEditingController());
      if (mounted) setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final noteState = ref.watch(manualNoteProvider);
    while (_controllers.length < noteState.fieldDefinitions.length) {
      _controllers.add(TextEditingController());
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(Icons.tune_rounded, size: 18, color: AppColors.primary),
          const SizedBox(width: 8),
          Text('manual_note.custom_fields_title'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        ]),
        if (noteState.fieldDefinitions.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text('manual_note.custom_fields_empty'.tr(), style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
          ),
        const SizedBox(height: 12),
        ...List.generate(noteState.fieldDefinitions.length, (i) {
          final def = noteState.fieldDefinitions[i];
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(def.fieldName, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
              const SizedBox(height: 6),
              Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Expanded(
                  child: TextField(
                    controller: _controllers[i],
                    style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary, height: 1.5),
                    maxLines: 2,
                    decoration: InputDecoration(
                      hintText: 'manual_note.custom_field_hint'.tr(), hintStyle: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted),
                      filled: true, fillColor: AppColors.background,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
                      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
                      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
                      contentPadding: const EdgeInsets.all(12),
                    ),
                    onChanged: (v) => ref.read(manualNoteProvider.notifier).updateCustomFieldValue(i, v),
                  ),
                ),
                const SizedBox(width: 4),
                IconButton(
                  onPressed: () {
                    ref.read(manualNoteProvider.notifier).removeFieldDefinition(def.id);
                    if (i < _controllers.length) {
                      _controllers[i].dispose();
                      _controllers.removeAt(i);
                    }
                  },
                  icon: Icon(Icons.delete_outline_rounded, size: 20, color: AppColors.accent),
                  tooltip: 'manual_note.delete_field'.tr(),
                ),
              ]),
            ]),
          );
        }),
        const SizedBox(height: 8),
        Row(children: [
          Expanded(
            child: TextField(
              controller: _newFieldCtrl,
              style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
              decoration: InputDecoration(
                hintText: 'manual_note.new_field_name_hint'.tr(), hintStyle: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted),
                filled: true, fillColor: AppColors.background,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              ),
              onSubmitted: (_) => _addNewField(),
            ),
          ),
          const SizedBox(width: 8),
          TextButton.icon(
            onPressed: _addNewField,
            icon: Icon(Icons.add_rounded, size: 18, color: AppColors.primary),
            label: Text('common.add'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.primary)),
          ),
        ]),
      ]),
    );
  }
}
