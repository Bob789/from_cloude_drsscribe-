import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/manual_note_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class DiagnosesSection extends ConsumerWidget {
  const DiagnosesSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final noteState = ref.watch(manualNoteProvider);
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text('summary.diagnoses'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          const Spacer(),
          TextButton.icon(
            onPressed: () => ref.read(manualNoteProvider.notifier).addDiagnosis(),
            icon: Icon(Icons.add_rounded, size: 18, color: AppColors.primary),
            label: Text('manual_note.add_diagnosis'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.primary)),
          ),
        ]),
        ...List.generate(noteState.diagnoses.length, (i) => Padding(
          padding: const EdgeInsets.only(top: 10),
          child: Row(children: [
            SizedBox(
              width: MediaQuery.of(context).size.width < 500 ? 70 : 100,
              child: TextField(
                style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
                decoration: InputDecoration(
                  hintText: 'manual_note.icd_code'.tr(), filled: true, fillColor: AppColors.background,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
                  enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                ),
                onChanged: (v) => ref.read(manualNoteProvider.notifier).updateDiagnosis(i, code: v),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: TextField(
                style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
                decoration: InputDecoration(
                  hintText: 'manual_note.diagnosis_name'.tr(), filled: true, fillColor: AppColors.background,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
                  enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                ),
                onChanged: (v) => ref.read(manualNoteProvider.notifier).updateDiagnosis(i, label: v),
              ),
            ),
            IconButton(
              onPressed: () => ref.read(manualNoteProvider.notifier).removeDiagnosis(i),
              icon: Icon(Icons.delete_outline_rounded, size: 20, color: AppColors.accent),
            ),
          ]),
        )),
      ]),
    );
  }
}

class TagsSection extends ConsumerWidget {
  const TagsSection({super.key});

  static const _typeOptions = ['diagnosis', 'symptom', 'treatment', 'procedure'];
  static final _typeLabels = {'diagnosis': 'manual_note.type_diagnosis', 'symptom': 'manual_note.type_symptom', 'treatment': 'manual_note.type_treatment', 'procedure': 'manual_note.type_procedure'};

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final noteState = ref.watch(manualNoteProvider);
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text('manual_note.tags'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          const Spacer(),
          TextButton.icon(
            onPressed: () => ref.read(manualNoteProvider.notifier).addTag(),
            icon: Icon(Icons.add_rounded, size: 18, color: AppColors.primary),
            label: Text('manual_note.add_tag'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.primary)),
          ),
        ]),
        ...List.generate(noteState.tags.length, (i) {
          final tag = noteState.tags[i];
          final isNarrow = MediaQuery.of(context).size.width < 500;
          final inputDeco = InputDecoration(
            filled: true, fillColor: AppColors.background,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
            contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          );
          return Padding(
            padding: const EdgeInsets.only(top: 10),
            child: isNarrow
                ? Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                    Row(children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: tag.tagType,
                          style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary),
                          decoration: inputDeco,
                          items: _typeOptions.map((t) => DropdownMenuItem(value: t, child: Text(_typeLabels[t]!.tr(), style: GoogleFonts.heebo(fontSize: 12)))).toList(),
                          onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagType: v),
                        ),
                      ),
                      IconButton(
                        onPressed: () => ref.read(manualNoteProvider.notifier).removeTag(i),
                        icon: Icon(Icons.delete_outline_rounded, size: 20, color: AppColors.accent),
                      ),
                    ]),
                    const SizedBox(height: 6),
                    Row(children: [
                      SizedBox(width: 70, child: TextField(
                        style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary),
                        decoration: inputDeco.copyWith(hintText: 'profile.tag_code'.tr()),
                        onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagCode: v),
                      )),
                      const SizedBox(width: 8),
                      Expanded(child: TextField(
                        style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary),
                        decoration: inputDeco.copyWith(hintText: 'profile.tag_name'.tr()),
                        onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagLabel: v),
                      )),
                    ]),
                  ])
                : Row(children: [
                    SizedBox(
                      width: 110,
                      child: DropdownButtonFormField<String>(
                        value: tag.tagType,
                        style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary),
                        decoration: inputDeco,
                        items: _typeOptions.map((t) => DropdownMenuItem(value: t, child: Text(_typeLabels[t]!.tr(), style: GoogleFonts.heebo(fontSize: 12)))).toList(),
                        onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagType: v),
                      ),
                    ),
                    const SizedBox(width: 8),
                    SizedBox(width: 80, child: TextField(
                      style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary),
                      decoration: inputDeco.copyWith(hintText: 'profile.tag_code'.tr()),
                      onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagCode: v),
                    )),
                    const SizedBox(width: 8),
                    Expanded(child: TextField(
                      style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary),
                      decoration: inputDeco.copyWith(hintText: 'profile.tag_name'.tr()),
                      onChanged: (v) => ref.read(manualNoteProvider.notifier).updateTag(i, tagLabel: v),
                    )),
                    IconButton(
                      onPressed: () => ref.read(manualNoteProvider.notifier).removeTag(i),
                      icon: Icon(Icons.delete_outline_rounded, size: 20, color: AppColors.accent),
                    ),
                  ]),
          );
        }),
      ]),
    );
  }
}
