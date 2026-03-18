import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/models/question_template_model.dart';
import 'package:medscribe_ai/providers/question_templates_provider.dart';
import 'package:medscribe_ai/screens/manual_note_screen.dart';

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

  void reset() => setState(() { _selected = null; _fields = []; });

  List<Map<String, dynamic>> getData() {
    if (_selected == null || _fields.isEmpty) return [];
    final answers = _fields.where((f) => f.value.isNotEmpty).map((f) => f.toAnswerJson()).toList();
    if (answers.isEmpty) return [];
    return [{'template_id': _selected!.id, 'template_name': _selected!.name, 'answers': answers}];
  }

  void _notifyParent() => widget.onChanged(getData());

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(questionTemplatesProvider);
    if (state.templates.isEmpty && !state.isLoading) return const SizedBox.shrink();

    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        const Icon(Icons.quiz_rounded, size: 20, color: kNavy),
        const SizedBox(width: 10),
        Text('manual_note.questionnaire_title'.tr(), style: GoogleFonts.rubik(fontSize: 20, fontWeight: FontWeight.w800, color: kNavy)),
        if (_selected != null) ...[
          const Spacer(),
          TextButton(
            onPressed: () => setState(() { _selected = null; _fields = []; _notifyParent(); }),
            child: Text('common.clear'.tr(), style: GoogleFonts.heebo(fontSize: 12, color: kMutedText)),
          ),
        ],
      ]),
      const SizedBox(height: 14),
      if (_selected == null) _buildTemplateSelector(state.templates) else _buildQuestionFields(),
    ]);
  }

  Widget _buildTemplateSelector(List<QuestionTemplateModel> templates) {
    return Wrap(spacing: 8, runSpacing: 8, children: templates.map((t) {
      Color templateColor;
      try { templateColor = Color(int.parse(t.color.replaceFirst('#', '0xFF'))); } catch (_) { templateColor = kNavy; }
      return Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => setState(() {
            _selected = t;
            _fields = t.questions.map((q) => QuestionField(label: q.label, type: q.type, required: q.required, options: q.options)).toList();
          }),
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: templateColor.withValues(alpha: 0.06),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: templateColor.withValues(alpha: 0.3)),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(_getIcon(t.icon), size: 18, color: templateColor),
              const SizedBox(width: 8),
              Text(t.name, style: GoogleFonts.rubik(fontSize: 13, fontWeight: FontWeight.w500, color: const Color(0xFF111111))),
            ]),
          ),
        ),
      );
    }).toList());
  }

  Widget _buildQuestionFields() {
    return Column(children: _fields.asMap().entries.map((e) => Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: _buildField(e.key, e.value),
    )).toList());
  }

  Widget _buildField(int index, QuestionField field) {
    final label = '${field.label}${field.required ? ' *' : ''}';
    const textColor = Color(0xFF111111);

    switch (field.type) {
      case 'boolean':
        return Row(children: [
          Expanded(child: Text(label, style: GoogleFonts.heebo(fontSize: 13, color: textColor))),
          Switch(value: field.value == 'true', onChanged: (v) { setState(() => field.value = v.toString()); _notifyParent(); }, activeColor: kNavy),
        ]);
      case 'select':
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: textColor)),
          const SizedBox(height: 6),
          Wrap(spacing: 8, runSpacing: 6, children: (field.options ?? []).map((opt) {
            final selected = field.value == opt;
            return GestureDetector(
              onTap: () { setState(() => field.value = opt); _notifyParent(); },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: selected ? kNavy.withValues(alpha: 0.12) : Colors.white.withValues(alpha: 0.65),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: selected ? kNavy : kInputBorder),
                ),
                child: Text(opt, style: GoogleFonts.heebo(fontSize: 12, fontWeight: selected ? FontWeight.w600 : FontWeight.w400, color: selected ? kNavy : const Color(0xFF555555))),
              ),
            );
          }).toList()),
        ]);
      case 'number':
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: textColor)),
          const SizedBox(height: 6),
          TextField(keyboardType: TextInputType.number, onChanged: (v) { field.value = v; _notifyParent(); }, style: GoogleFonts.heebo(fontSize: 13, color: textColor), decoration: _inputDeco()),
        ]);
      case 'textarea':
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: textColor)),
          const SizedBox(height: 6),
          TextField(maxLines: 4, onChanged: (v) { field.value = v; _notifyParent(); }, style: GoogleFonts.heebo(fontSize: 13, color: textColor), decoration: _inputDeco()),
        ]);
      default:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: textColor)),
          const SizedBox(height: 6),
          TextField(onChanged: (v) { field.value = v; _notifyParent(); }, style: GoogleFonts.heebo(fontSize: 13, color: textColor), decoration: _inputDeco()),
        ]);
    }
  }

  InputDecoration _inputDeco() => InputDecoration(
    filled: true,
    fillColor: Colors.white.withValues(alpha: 0.65),
    isDense: true,
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kNavy)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
  );

  IconData _getIcon(String name) {
    const map = {
      'clipboard': Icons.assignment_rounded, 'heart': Icons.favorite_rounded, 'baby': Icons.child_care_rounded,
      'bone': Icons.accessibility_new_rounded, 'eye': Icons.visibility_rounded, 'brain': Icons.psychology_rounded,
      'lungs': Icons.air_rounded, 'tooth': Icons.medical_services_rounded, 'skin': Icons.face_rounded, 'general': Icons.local_hospital_rounded,
    };
    return map[name] ?? Icons.assignment_rounded;
  }
}
