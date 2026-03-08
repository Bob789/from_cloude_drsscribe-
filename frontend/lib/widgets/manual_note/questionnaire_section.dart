import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/models/question_template_model.dart';
import 'package:medscribe_ai/providers/question_templates_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class QuestionnaireSection extends ConsumerStatefulWidget {
  final ValueChanged<List<Map<String, dynamic>>> onChanged;
  const QuestionnaireSection({super.key, required this.onChanged});

  @override
  ConsumerState<QuestionnaireSection> createState() => QuestionnaireSectionState();
}

class QuestionnaireSectionState extends ConsumerState<QuestionnaireSection> {
  QuestionTemplateModel? _selected;
  List<QuestionField> _fields = [];

  @override
  void initState() {
    super.initState();
    Future(() => ref.read(questionTemplatesProvider.notifier).load());
  }

  void reset() {
    setState(() {
      _selected = null;
      _fields = [];
    });
  }

  List<Map<String, dynamic>> getData() {
    if (_selected == null || _fields.isEmpty) return [];
    final answers = _fields.where((f) => f.value.isNotEmpty).map((f) => f.toAnswerJson()).toList();
    if (answers.isEmpty) return [];
    return [{'template_id': _selected!.id, 'template_name': _selected!.name, 'answers': answers}];
  }

  void _notifyParent() {
    widget.onChanged(getData());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(questionTemplatesProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    if (state.templates.isEmpty && !state.isLoading) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(Icons.quiz_rounded, size: 20, color: AppColors.primary),
          const SizedBox(width: 10),
          Text('manual_note.questionnaire_title'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          if (_selected != null) ...[
            const Spacer(),
            TextButton(
              onPressed: () => setState(() { _selected = null; _fields = []; _notifyParent(); }),
              child: Text('common.clear'.tr(), style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
            ),
          ],
        ]),
        const SizedBox(height: 14),
        if (_selected == null)
          _buildTemplateSelector(state.templates)
        else
          _buildQuestionFields(),
      ]),
    );
  }

  Widget _buildTemplateSelector(List<QuestionTemplateModel> templates) {
    return Wrap(spacing: 10, runSpacing: 10, children: templates.map((t) {
      Color templateColor;
      try {
        templateColor = Color(int.parse(t.color.replaceFirst('#', '0xFF')));
      } catch (_) {
        templateColor = AppColors.primary;
      }

      return Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            setState(() {
              _selected = t;
              _fields = t.questions.map((q) => QuestionField(
                label: q.label, type: q.type, required: q.required, options: q.options,
              )).toList();
            });
          },
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: templateColor.withValues(alpha: 0.06),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: templateColor.withValues(alpha: 0.3)),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(_getIcon(t.icon), size: 18, color: templateColor),
              const SizedBox(width: 8),
              Text(t.name, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
            ]),
          ),
        ),
      );
    }).toList());
  }

  Widget _buildQuestionFields() {
    return Column(children: _fields.asMap().entries.map((e) {
      final idx = e.key;
      final field = e.value;
      return Padding(
        padding: const EdgeInsets.only(bottom: 14),
        child: _buildField(idx, field),
      );
    }).toList());
  }

  Widget _buildField(int index, QuestionField field) {
    final label = '${field.label}${field.required ? ' *' : ''}';

    switch (field.type) {
      case 'boolean':
        return Row(children: [
          Expanded(child: Text(label, style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary))),
          Switch(
            value: field.value == 'true',
            onChanged: (v) { setState(() => field.value = v.toString()); _notifyParent(); },
            activeColor: AppColors.primary,
          ),
        ]);

      case 'select':
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
          const SizedBox(height: 6),
          Wrap(spacing: 8, runSpacing: 6, children: (field.options ?? []).map((opt) {
            final selected = field.value == opt;
            return GestureDetector(
              onTap: () { setState(() => field.value = opt); _notifyParent(); },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: selected ? AppColors.primary.withValues(alpha: 0.12) : AppColors.background,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: selected ? AppColors.primary : AppColors.cardBorder),
                ),
                child: Text(opt, style: GoogleFonts.heebo(fontSize: 12, fontWeight: selected ? FontWeight.w600 : FontWeight.w400, color: selected ? AppColors.primary : AppColors.textSecondary)),
              ),
            );
          }).toList()),
        ]);

      case 'number':
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
          const SizedBox(height: 6),
          TextField(
            keyboardType: TextInputType.number,
            onChanged: (v) { field.value = v; _notifyParent(); },
            style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
            decoration: _inputDecoration(),
          ),
        ]);

      case 'textarea':
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
          const SizedBox(height: 6),
          TextField(
            maxLines: 4,
            onChanged: (v) { field.value = v; _notifyParent(); },
            style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
            decoration: _inputDecoration(),
          ),
        ]);

      default:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
          const SizedBox(height: 6),
          TextField(
            onChanged: (v) { field.value = v; _notifyParent(); },
            style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
            decoration: _inputDecoration(),
          ),
        ]);
    }
  }

  InputDecoration _inputDecoration() => InputDecoration(
    filled: true, fillColor: AppColors.background,
    isDense: true,
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.primary)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
  );

  IconData _getIcon(String name) {
    const map = {
      'clipboard': Icons.assignment_rounded,
      'heart': Icons.favorite_rounded,
      'baby': Icons.child_care_rounded,
      'bone': Icons.accessibility_new_rounded,
      'eye': Icons.visibility_rounded,
      'brain': Icons.psychology_rounded,
      'lungs': Icons.air_rounded,
      'tooth': Icons.medical_services_rounded,
      'skin': Icons.face_rounded,
      'general': Icons.local_hospital_rounded,
    };
    return map[name] ?? Icons.assignment_rounded;
  }
}
