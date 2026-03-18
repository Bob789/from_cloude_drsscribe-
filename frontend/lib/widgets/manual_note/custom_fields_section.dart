import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/providers/manual_note_provider.dart';
import 'package:medscribe_ai/screens/manual_note_screen.dart';

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

  InputDecoration _deco({String? hint}) => InputDecoration(
    hintText: hint,
    hintStyle: GoogleFonts.heebo(color: kMutedText, fontSize: 13),
    filled: true,
    fillColor: Colors.white.withValues(alpha: 0.65),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kNavy, width: 1.5)),
    contentPadding: const EdgeInsets.all(12),
  );

  @override
  Widget build(BuildContext context) {
    final noteState = ref.watch(manualNoteProvider);
    while (_controllers.length < noteState.fieldDefinitions.length) {
      _controllers.add(TextEditingController());
    }

    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        const Icon(Icons.tune_rounded, size: 18, color: kNavy),
        const SizedBox(width: 8),
        Text('manual_note.custom_fields_title'.tr(), style: GoogleFonts.rubik(fontSize: 20, fontWeight: FontWeight.w800, color: kNavy)),
      ]),
      if (noteState.fieldDefinitions.isEmpty)
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Text('manual_note.custom_fields_empty'.tr(), style: GoogleFonts.heebo(fontSize: 12, color: kMutedText)),
        ),
      const SizedBox(height: 12),
      ...List.generate(noteState.fieldDefinitions.length, (i) {
        final def = noteState.fieldDefinitions[i];
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(def.fieldName, style: GoogleFonts.rubik(fontSize: 13, fontWeight: FontWeight.w700, color: kNavy)),
            const SizedBox(height: 6),
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Expanded(
                child: TextField(
                  controller: _controllers[i],
                  style: GoogleFonts.heebo(fontSize: 13, color: const Color(0xFF111111), height: 1.5),
                  maxLines: 2,
                  decoration: _deco(hint: 'manual_note.custom_field_hint'.tr()),
                  onChanged: (v) => ref.read(manualNoteProvider.notifier).updateCustomFieldValue(i, v),
                ),
              ),
              const SizedBox(width: 4),
              IconButton(
                onPressed: () {
                  ref.read(manualNoteProvider.notifier).removeFieldDefinition(def.id);
                  if (i < _controllers.length) { _controllers[i].dispose(); _controllers.removeAt(i); }
                },
                icon: const Icon(Icons.delete_outline_rounded, size: 20, color: Color(0xFFDC2626)),
              ),
            ]),
          ]),
        );
      }),
      const SizedBox(height: 8),
      Row(children: [
        Expanded(child: TextField(
          controller: _newFieldCtrl,
          style: GoogleFonts.heebo(fontSize: 13, color: const Color(0xFF111111)),
          decoration: _deco(hint: 'manual_note.new_field_name_hint'.tr()),
          onSubmitted: (_) => _addNewField(),
        )),
        const SizedBox(width: 8),
        InkWell(
          onTap: _addNewField,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(color: kNavy.withValues(alpha: 0.07), borderRadius: BorderRadius.circular(8), border: Border.all(color: kNavy.withValues(alpha: 0.3))),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.add_rounded, size: 16, color: kNavy),
              const SizedBox(width: 4),
              Text('common.add'.tr(), style: GoogleFonts.rubik(fontSize: 12, fontWeight: FontWeight.w700, color: kNavy)),
            ]),
          ),
        ),
      ]),
    ]);
  }
}
