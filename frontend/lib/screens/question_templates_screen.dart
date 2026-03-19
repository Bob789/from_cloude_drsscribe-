import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/models/question_template_model.dart';
import 'package:medscribe_ai/providers/question_templates_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class QuestionTemplatesScreen extends ConsumerStatefulWidget {
  const QuestionTemplatesScreen({super.key});

  @override
  ConsumerState<QuestionTemplatesScreen> createState() => _QuestionTemplatesScreenState();
}

class _QuestionTemplatesScreenState extends ConsumerState<QuestionTemplatesScreen> {
  @override
  void initState() {
    super.initState();
    Future(() => ref.read(questionTemplatesProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(questionTemplatesProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: EdgeInsets.all(MediaQuery.of(context).size.width < 500 ? 12 : 24),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _buildHeader(),
              const SizedBox(height: 24),
              if (state.isLoading)
                const Center(child: Padding(padding: EdgeInsets.all(40), child: CircularProgressIndicator()))
              else if (state.templates.isEmpty)
                _buildEmptyState(ext)
              else
                ...state.templates.map((t) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: _TemplateCard(template: t),
                )),
            ]),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(children: [
      Expanded(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('templates.title'.tr(), style: GoogleFonts.heebo(fontSize: 24, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
          Text('templates.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
        ]),
      ),
      Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => _showTemplateDialog(),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: BoxDecoration(
              gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.add_rounded, color: Colors.white, size: 20),
              const SizedBox(width: 8),
              Text('templates.new'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white)),
            ]),
          ),
        ),
      ),
    ]);
  }

  Widget _buildEmptyState(MedScribeThemeExtension ext) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(48),
      decoration: ext.cardDecoration,
      child: Column(children: [
        Icon(Icons.quiz_outlined, size: 56, color: AppColors.textMuted),
        const SizedBox(height: 16),
        Text('templates.empty'.tr(), style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 8),
        Text('templates.empty_hint'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted), textAlign: TextAlign.center),
        const SizedBox(height: 20),
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => _showTemplateDialog(),
            borderRadius: BorderRadius.circular(10),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text('templates.create_first'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white)),
            ),
          ),
        ),
      ]),
    );
  }

  void _showTemplateDialog({QuestionTemplateModel? existing}) {
    showDialog(
      context: context,
      builder: (ctx) => _TemplateFormDialog(
        existing: existing,
        onSaved: (name, description, icon, color, questions, isShared) async {
          if (existing != null) {
            await ref.read(questionTemplatesProvider.notifier).update(existing.id, {
              'name': name,
              'description': description,
              'icon': icon,
              'color': color,
              'questions': questions,
              'is_shared': isShared,
            });
          } else {
            await ref.read(questionTemplatesProvider.notifier).create(
              name: name,
              description: description,
              icon: icon,
              color: color,
              questions: questions,
              isShared: isShared,
            );
          }
        },
      ),
    );
  }
}

class _TemplateCard extends ConsumerWidget {
  final QuestionTemplateModel template;
  const _TemplateCard({required this.template});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    Color templateColor;
    try {
      templateColor = Color(int.parse(template.color.replaceFirst('#', '0xFF')));
    } catch (_) {
      templateColor = AppColors.primary;
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            width: 42, height: 42,
            decoration: BoxDecoration(
              color: templateColor.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(_getIcon(template.icon), color: templateColor, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(template.name, style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
              if (template.description != null)
                Text(template.description!, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted), maxLines: 1, overflow: TextOverflow.ellipsis),
            ]),
          ),
          if (template.isShared)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(6)),
              child: Text('templates.shared'.tr(), style: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.primary)),
            ),
          const SizedBox(width: 8),
          _PopupMenu(
            onEdit: () {
              final screen = context.findAncestorStateOfType<_QuestionTemplatesScreenState>();
              screen?._showTemplateDialog(existing: template);
            },
            onDuplicate: () => ref.read(questionTemplatesProvider.notifier).duplicate(template.id),
            onDelete: () => _confirmDelete(context, ref),
          ),
        ]),
        const SizedBox(height: 14),
        Wrap(spacing: 8, runSpacing: 6, children: [
          _InfoChip(icon: Icons.quiz_outlined, label: 'templates.questions_count'.tr(namedArgs: {'count': template.questions.length.toString()})),
          _InfoChip(icon: Icons.bar_chart_rounded, label: 'templates.usage_count'.tr(namedArgs: {'count': template.usageCount.toString()})),
        ]),
      ]),
    );
  }

  void _confirmDelete(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('templates.delete_title'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w700)),
        content: Text('templates.delete_confirm'.tr(namedArgs: {'name': template.name}), style: GoogleFonts.heebo()),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text('common.cancel'.tr(), style: GoogleFonts.heebo())),
          TextButton(
            onPressed: () { Navigator.pop(ctx); ref.read(questionTemplatesProvider.notifier).delete(template.id); },
            child: Text('common.delete'.tr(), style: GoogleFonts.heebo(color: Colors.red)),
          ),
        ],
      ),
    );
  }

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

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(color: AppColors.background, borderRadius: BorderRadius.circular(6)),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Icon(icon, size: 14, color: AppColors.textMuted),
        const SizedBox(width: 5),
        Text(label, style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textSecondary)),
      ]),
    );
  }
}

class _PopupMenu extends StatelessWidget {
  final VoidCallback onEdit;
  final VoidCallback onDuplicate;
  final VoidCallback onDelete;
  const _PopupMenu({required this.onEdit, required this.onDuplicate, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      icon: Icon(Icons.more_vert_rounded, color: AppColors.textMuted, size: 20),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      onSelected: (v) {
        if (v == 'edit') onEdit();
        if (v == 'duplicate') onDuplicate();
        if (v == 'delete') onDelete();
      },
      itemBuilder: (_) => [
        PopupMenuItem(value: 'edit', child: Row(children: [Icon(Icons.edit_rounded, size: 18, color: AppColors.textSecondary), const SizedBox(width: 10), Text('templates.editing'.tr(), style: GoogleFonts.heebo(fontSize: 13))])),
        PopupMenuItem(value: 'duplicate', child: Row(children: [Icon(Icons.copy_rounded, size: 18, color: AppColors.textSecondary), const SizedBox(width: 10), Text('templates.duplicate'.tr(), style: GoogleFonts.heebo(fontSize: 13))])),
        PopupMenuItem(value: 'delete', child: Row(children: [Icon(Icons.delete_rounded, size: 18, color: Colors.red), const SizedBox(width: 10), Text('templates.deleting'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: Colors.red))])),
      ],
    );
  }
}

class _TemplateFormDialog extends StatefulWidget {
  final QuestionTemplateModel? existing;
  final Future<void> Function(String name, String? description, String icon, String color, List<Map<String, dynamic>> questions, bool isShared) onSaved;

  const _TemplateFormDialog({this.existing, required this.onSaved});

  @override
  State<_TemplateFormDialog> createState() => _TemplateFormDialogState();
}

class _TemplateFormDialogState extends State<_TemplateFormDialog> {
  late final TextEditingController _nameCtrl;
  late final TextEditingController _descCtrl;
  late String _icon;
  late String _color;
  late bool _isShared;
  late List<_QuestionDraft> _questions;
  bool _saving = false;

  static const _icons = ['clipboard', 'heart', 'baby', 'bone', 'eye', 'brain', 'lungs', 'tooth', 'skin', 'general'];
  static const _colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#6366F1'];

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(text: widget.existing?.name ?? '');
    _descCtrl = TextEditingController(text: widget.existing?.description ?? '');
    _icon = widget.existing?.icon ?? 'clipboard';
    _color = widget.existing?.color ?? '#3B82F6';
    _isShared = widget.existing?.isShared ?? false;
    _questions = widget.existing?.questions.map((q) =>
      _QuestionDraft(label: q.label, type: q.type, required_: q.required, options: q.options?.join(', ') ?? '')
    ).toList() ?? [_QuestionDraft()];
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        width: MediaQuery.of(context).size.width < 600 ? MediaQuery.of(context).size.width * 0.95 : 560,
        constraints: BoxConstraints(maxHeight: MediaQuery.of(context).size.height * 0.85),
        child: Column(children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
            child: Row(children: [
              Expanded(child: Text(
                widget.existing != null ? 'templates.edit_template'.tr() : 'templates.new'.tr(),
                style: GoogleFonts.heebo(fontSize: 20, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
              )),
              IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.close_rounded)),
            ]),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                _buildTextField('templates.template_name'.tr(), _nameCtrl),
                const SizedBox(height: 14),
                _buildTextField('templates.description'.tr(), _descCtrl),
                const SizedBox(height: 18),
                Text('templates.icon'.tr(), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                const SizedBox(height: 8),
                Wrap(spacing: 8, runSpacing: 8, children: _icons.map((ic) {
                  final selected = _icon == ic;
                  return GestureDetector(
                    onTap: () => setState(() => _icon = ic),
                    child: Container(
                      width: 40, height: 40,
                      decoration: BoxDecoration(
                        color: selected ? AppColors.primary.withValues(alpha: 0.12) : AppColors.background,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: selected ? AppColors.primary : AppColors.cardBorder),
                      ),
                      child: Icon(_iconFromName(ic), size: 20, color: selected ? AppColors.primary : AppColors.textMuted),
                    ),
                  );
                }).toList()),
                const SizedBox(height: 18),
                Text('templates.color'.tr(), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                const SizedBox(height: 8),
                Wrap(spacing: 8, runSpacing: 8, children: _colors.map((c) {
                  final selected = _color == c;
                  Color parsed;
                  try { parsed = Color(int.parse(c.replaceFirst('#', '0xFF'))); } catch (_) { parsed = AppColors.primary; }
                  return GestureDetector(
                    onTap: () => setState(() => _color = c),
                    child: Container(
                      width: 36, height: 36,
                      decoration: BoxDecoration(
                        color: parsed,
                        shape: BoxShape.circle,
                        border: Border.all(color: selected ? AppColors.textPrimary : Colors.transparent, width: 3),
                      ),
                    ),
                  );
                }).toList()),
                const SizedBox(height: 18),
                Row(children: [
                  Switch(value: _isShared, onChanged: (v) => setState(() => _isShared = v), activeColor: AppColors.primary),
                  const SizedBox(width: 8),
                  Text('templates.share_with_all'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textSecondary)),
                ]),
                const SizedBox(height: 24),
                Row(children: [
                  Text('templates.questions'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                  const Spacer(),
                  TextButton.icon(
                    onPressed: () => setState(() => _questions.add(_QuestionDraft())),
                    icon: const Icon(Icons.add_rounded, size: 18),
                    label: Text('templates.add_question'.tr(), style: GoogleFonts.heebo(fontSize: 13)),
                  ),
                ]),
                const SizedBox(height: 8),
                ..._questions.asMap().entries.map((e) => _buildQuestionRow(e.key)),
              ]),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: Row(children: [
              Expanded(child: OutlinedButton(
                onPressed: () => Navigator.pop(context),
                style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))),
                child: Text('common.cancel'.tr(), style: GoogleFonts.heebo(fontSize: 14)),
              )),
              const SizedBox(width: 12),
              Expanded(child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: _saving ? null : _save,
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Center(child: _saving
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : Text('common.save'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white)),
                    ),
                  ),
                ),
              )),
            ]),
          ),
        ]),
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController ctrl) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
      const SizedBox(height: 6),
      TextField(
        controller: ctrl,
        style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textPrimary),
        decoration: InputDecoration(
          filled: true, fillColor: AppColors.background,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.primary)),
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        ),
      ),
    ]);
  }

  Widget _buildQuestionRow(int index) {
    final q = _questions[index];
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: AppColors.background, borderRadius: BorderRadius.circular(10), border: Border.all(color: AppColors.cardBorder)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text('${index + 1}.', style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
          const SizedBox(width: 10),
          Expanded(child: TextField(
            controller: TextEditingController(text: q.label)..selection = TextSelection.collapsed(offset: q.label.length),
            onChanged: (v) => q.label = v,
            style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
            decoration: InputDecoration(
              hintText: 'templates.question_text'.tr(),
              hintStyle: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted),
              isDense: true,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(vertical: 8),
            ),
          )),
          DropdownButton<String>(
            value: q.type,
            underline: const SizedBox(),
            style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textSecondary),
            items: [
              DropdownMenuItem(value: 'text', child: Text('templates.text'.tr())),
              DropdownMenuItem(value: 'textarea', child: Text('templates.long_text'.tr())),
              DropdownMenuItem(value: 'number', child: Text('templates.number'.tr())),
              DropdownMenuItem(value: 'select', child: Text('templates.select'.tr())),
              DropdownMenuItem(value: 'boolean', child: Text('templates.yes_no'.tr())),
            ],
            onChanged: (v) => setState(() => q.type = v!),
          ),
          IconButton(
            icon: Icon(q.required_ ? Icons.star_rounded : Icons.star_border_rounded, size: 18, color: q.required_ ? Colors.amber : AppColors.textMuted),
            tooltip: 'templates.required'.tr(),
            onPressed: () => setState(() => q.required_ = !q.required_),
          ),
          IconButton(
            icon: Icon(Icons.delete_outline_rounded, size: 18, color: AppColors.textMuted),
            onPressed: _questions.length > 1 ? () => setState(() => _questions.removeAt(index)) : null,
          ),
        ]),
        if (q.type == 'select') ...[
          const SizedBox(height: 8),
          TextField(
            controller: TextEditingController(text: q.options),
            onChanged: (v) => q.options = v,
            style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textSecondary),
            decoration: InputDecoration(
              hintText: 'templates.options_hint'.tr(),
              hintStyle: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted),
              isDense: true,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.cardBorder)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            ),
          ),
        ],
      ]),
    );
  }

  Future<void> _save() async {
    if (_nameCtrl.text.trim().isEmpty) return;
    final validQuestions = _questions.where((q) => q.label.trim().isNotEmpty).toList();
    if (validQuestions.isEmpty) return;

    setState(() => _saving = true);
    final questions = validQuestions.map((q) {
      final m = <String, dynamic>{'label': q.label.trim(), 'type': q.type, 'required': q.required_};
      if (q.type == 'select' && q.options.isNotEmpty) {
        m['options'] = q.options.split(',').map((o) => o.trim()).where((o) => o.isNotEmpty).toList();
      }
      return m;
    }).toList();

    await widget.onSaved(_nameCtrl.text.trim(), _descCtrl.text.isEmpty ? null : _descCtrl.text, _icon, _color, questions, _isShared);
    if (mounted) Navigator.pop(context);
  }

  IconData _iconFromName(String name) {
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

class _QuestionDraft {
  String label;
  String type;
  bool required_;
  String options;
  _QuestionDraft({this.label = '', this.type = 'text', this.required_ = false, this.options = ''});
}
