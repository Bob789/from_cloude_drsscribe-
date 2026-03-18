import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/manual_note_provider.dart';
import 'package:medscribe_ai/screens/manual_note_screen.dart';

InputDecoration _fieldDeco({String? hint}) => InputDecoration(
  hintText: hint,
  hintStyle: GoogleFonts.heebo(color: kMutedText),
  filled: true,
  fillColor: Colors.white.withValues(alpha: 0.65),
  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
  enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
  focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kNavy, width: 1.5)),
  contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
);

class DiagnosesSection extends ConsumerWidget {
  const DiagnosesSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final noteState = ref.watch(manualNoteProvider);
    final isNarrow = MediaQuery.of(context).size.width < 500;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Text('summary.diagnoses'.tr(), style: GoogleFonts.rubik(fontSize: 20, fontWeight: FontWeight.w800, color: kNavy)),
        const Spacer(),
        InkWell(
          onTap: () => ref.read(manualNoteProvider.notifier).addDiagnosis(),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: kNavy.withValues(alpha: 0.07),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: kNavy.withValues(alpha: 0.3)),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.add_rounded, size: 16, color: kNavy),
              const SizedBox(width: 4),
              Text('manual_note.add_diagnosis'.tr(), style: GoogleFonts.rubik(fontSize: 12, fontWeight: FontWeight.w700, color: kNavy)),
            ]),
          ),
        ),
      ]),
      ...List.generate(noteState.diagnoses.length, (i) => Padding(
        padding: const EdgeInsets.only(top: 8),
        child: Row(children: [
          SizedBox(
            width: isNarrow ? 70 : 100,
            child: TextField(
              style: GoogleFonts.heebo(fontSize: 13, color: const Color(0xFF111111)),
              decoration: _fieldDeco(hint: 'manual_note.icd_code'.tr()),
              onChanged: (v) => ref.read(manualNoteProvider.notifier).updateDiagnosis(i, code: v),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              style: GoogleFonts.heebo(fontSize: 13, color: const Color(0xFF111111)),
              decoration: _fieldDeco(hint: 'manual_note.diagnosis_name'.tr()),
              onChanged: (v) => ref.read(manualNoteProvider.notifier).updateDiagnosis(i, label: v),
            ),
          ),
          IconButton(
            onPressed: () => ref.read(manualNoteProvider.notifier).removeDiagnosis(i),
            icon: const Icon(Icons.delete_outline_rounded, size: 20, color: Color(0xFFDC2626)),
          ),
        ]),
      )),
    ]);
  }
}

class TagsSection extends ConsumerWidget {
  const TagsSection({super.key});

  static const _typeOptions = ['diagnosis', 'symptom', 'treatment', 'procedure'];
  static final _typeLabels = {'diagnosis': 'manual_note.type_diagnosis', 'symptom': 'manual_note.type_symptom', 'treatment': 'manual_note.type_treatment', 'procedure': 'manual_note.type_procedure'};

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final noteState = ref.watch(manualNoteProvider);
    final isNarrow = MediaQuery.of(context).size.width < 500;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Text('manual_note.tags'.tr(), style: GoogleFonts.rubik(fontSize: 20, fontWeight: FontWeight.w800, color: kNavy)),
        const Spacer(),
        InkWell(
          onTap: () => ref.read(manualNoteProvider.notifier).addTag(),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: kNavy.withValues(alpha: 0.07),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: kNavy.withValues(alpha: 0.3)),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.add_rounded, size: 16, color: kNavy),
              const SizedBox(width: 4),
              Text('manual_note.add_tag'.tr(), style: GoogleFonts.rubik(fontSize: 12, fontWeight: FontWeight.w700, color: kNavy)),
            ]),
          ),
        ),
      ]),
      ...List.generate(noteState.tags.length, (i) {
        final tag = noteState.tags[i];
        final deco = _fieldDeco();
        return Padding(
          padding: const EdgeInsets.only(top: 8),
          child: isNarrow
              ? Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                  Row(children: [
                    Expanded(child: DropdownButtonFormField<String>(
                      value: tag.tagType,
                      style: GoogleFonts.heebo(fontSize: 12, color: const Color(0xFF111111)),
                      decoration: deco,
                      items: _typeOptions.map((t) => DropdownMenuItem(value: t, child: Text(_typeLabels[t]!.tr(), style: GoogleFonts.heebo(fontSize: 12)))).toList(),
                      onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagType: v),
                    )),
                    IconButton(onPressed: () => ref.read(manualNoteProvider.notifier).removeTag(i), icon: const Icon(Icons.delete_outline_rounded, size: 20, color: Color(0xFFDC2626))),
                  ]),
                  const SizedBox(height: 6),
                  Row(children: [
                    SizedBox(width: 70, child: TextField(style: GoogleFonts.heebo(fontSize: 12, color: const Color(0xFF111111)), decoration: _fieldDeco(hint: 'profile.tag_code'.tr()), onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagCode: v))),
                    const SizedBox(width: 8),
                    Expanded(child: TextField(style: GoogleFonts.heebo(fontSize: 12, color: const Color(0xFF111111)), decoration: _fieldDeco(hint: 'profile.tag_name'.tr()), onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagLabel: v))),
                  ]),
                ])
              : Row(children: [
                  SizedBox(width: 110, child: DropdownButtonFormField<String>(
                    value: tag.tagType,
                    style: GoogleFonts.heebo(fontSize: 12, color: const Color(0xFF111111)),
                    decoration: deco,
                    items: _typeOptions.map((t) => DropdownMenuItem(value: t, child: Text(_typeLabels[t]!.tr(), style: GoogleFonts.heebo(fontSize: 12)))).toList(),
                    onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagType: v),
                  )),
                  const SizedBox(width: 8),
                  SizedBox(width: 80, child: TextField(style: GoogleFonts.heebo(fontSize: 12, color: const Color(0xFF111111)), decoration: _fieldDeco(hint: 'profile.tag_code'.tr()), onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagCode: v))),
                  const SizedBox(width: 8),
                  Expanded(child: TextField(style: GoogleFonts.heebo(fontSize: 12, color: const Color(0xFF111111)), decoration: _fieldDeco(hint: 'profile.tag_name'.tr()), onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagLabel: v))),
                  IconButton(onPressed: () => ref.read(manualNoteProvider.notifier).removeTag(i), icon: const Icon(Icons.delete_outline_rounded, size: 20, color: Color(0xFFDC2626))),
                ]),
        );
      }),
    ]);
  }
}
