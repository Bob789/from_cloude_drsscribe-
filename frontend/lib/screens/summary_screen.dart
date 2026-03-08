import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/widgets/tags_widget.dart';

class SummaryScreen extends ConsumerStatefulWidget {
  final String summaryId;
  const SummaryScreen({super.key, required this.summaryId});

  @override
  ConsumerState<SummaryScreen> createState() => _SummaryScreenState();
}

class _SummaryScreenState extends ConsumerState<SummaryScreen> {
  Map<String, dynamic>? _data;
  bool _isLoading = true;
  bool _isEditing = false;
  final _complaintController = TextEditingController();
  final _findingsController = TextEditingController();
  final _treatmentController = TextEditingController();
  final _recommendationsController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final response = await ApiClient().dio.get('/summaries/${widget.summaryId}');
      setState(() {
        _data = response.data;
        _complaintController.text = _data?['chief_complaint'] ?? '';
        _findingsController.text = _data?['findings'] ?? '';
        _treatmentController.text = _data?['treatment_plan'] ?? '';
        _recommendationsController.text = _data?['recommendations'] ?? '';
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _save() async {
    try {
      await ApiClient().dio.put('/summaries/${widget.summaryId}', data: {
        'chief_complaint': _complaintController.text,
        'findings': _findingsController.text,
        'treatment_plan': _treatmentController.text,
        'recommendations': _recommendationsController.text,
      });
      setState(() => _isEditing = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.check_circle_rounded, color: AppColors.success, size: 18),
                const SizedBox(width: 10),
                Text('common.saved_success'.tr(), style: GoogleFonts.heebo(color: AppColors.textPrimary)),
              ],
            ),
            backgroundColor: AppColors.card,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.error_outline_rounded, color: AppColors.accent, size: 18),
                const SizedBox(width: 10),
                Text('common.save_error'.tr(), style: GoogleFonts.heebo(color: AppColors.textPrimary)),
              ],
            ),
            backgroundColor: AppColors.card,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        );
      }
    }
  }

  @override
  void dispose() {
    _complaintController.dispose();
    _findingsController.dispose();
    _treatmentController.dispose();
    _recommendationsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    if (_isLoading) {
      return Scaffold(
        backgroundColor: AppColors.background,
        body: Center(child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5)),
      );
    }
    if (_data == null) {
      return Scaffold(
        backgroundColor: AppColors.background,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.description_rounded, size: 48, color: AppColors.textMuted.withValues(alpha: 0.4)),
              const SizedBox(height: 16),
              Text('summary.not_found'.tr(), style: GoogleFonts.heebo(fontSize: 16, color: AppColors.textSecondary)),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(ext),
            const SizedBox(height: 20),
            _buildUrgencyBadge(_data!['urgency'] ?? 'low', ext),
            const SizedBox(height: 16),
            _buildSection('summary.chief_complaint'.tr(), _complaintController, Icons.report_problem_rounded, ext),
            _buildSection('summary.findings'.tr(), _findingsController, Icons.search_rounded, ext),
            _buildDiagnosisSection(ext),
            _buildSection('summary.treatment_plan'.tr(), _treatmentController, Icons.medical_services_rounded, ext),
            _buildSection('summary.recommendations'.tr(), _recommendationsController, Icons.recommend_rounded, ext),
            if (_data!['diagnosis'] != null) ...[
              const SizedBox(height: 8),
              TagsWidget(tags: _data!['diagnosis']),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(MedScribeThemeExtension ext) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('summary.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
              const SizedBox(height: 4),
              Text('summary.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
            ],
          ),
        ),
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: _isEditing ? _save : () => setState(() => _isEditing = true),
            borderRadius: BorderRadius.circular(12),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                gradient: _isEditing ? LinearGradient(colors: ext.gradientColors) : null,
                color: _isEditing ? null : AppColors.card,
                borderRadius: BorderRadius.circular(12),
                border: _isEditing ? null : Border.all(color: AppColors.cardBorder),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    _isEditing ? Icons.save_rounded : Icons.edit_rounded,
                    size: 18,
                    color: _isEditing ? Colors.white : AppColors.textSecondary,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    _isEditing ? 'common.save'.tr() : 'common.edit'.tr(),
                    style: GoogleFonts.heebo(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: _isEditing ? Colors.white : AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildUrgencyBadge(String urgency, MedScribeThemeExtension ext) {
    final color = ext.urgencyColors[urgency] ?? AppColors.textMuted;
    final labelMap = {
      'low': 'summary.urgency_low'.tr(),
      'medium': 'summary.urgency_medium'.tr(),
      'high': 'summary.urgency_high'.tr(),
      'critical': 'summary.urgency_critical'.tr(),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.flag_rounded, size: 14, color: color),
          const SizedBox(width: 6),
          Text(labelMap[urgency] ?? urgency, style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
        ],
      ),
    );
  }

  Widget _buildSection(String title, TextEditingController controller, IconData icon, MedScribeThemeExtension ext) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(
              width: 28,
              height: 28,
              decoration: ext.iconContainer(AppColors.primary),
              child: Icon(icon, size: 14, color: AppColors.primary),
            ),
            const SizedBox(width: 10),
            Text(title, style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          ]),
          const SizedBox(height: 12),
          _isEditing
              ? TextField(
                  controller: controller,
                  maxLines: null,
                  style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary, height: 1.6),
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: AppColors.background,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
                    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
                    contentPadding: const EdgeInsets.all(14),
                  ),
                )
              : SelectableText(
                  controller.text.isEmpty ? 'summary.not_available'.tr() : controller.text,
                  style: GoogleFonts.heebo(
                    fontSize: 13,
                    color: controller.text.isEmpty ? AppColors.textMuted : AppColors.textSecondary,
                    height: 1.6,
                  ),
                ),
        ],
      ),
    );
  }

  Widget _buildDiagnosisSection(MedScribeThemeExtension ext) {
    final diagnoses = _data!['diagnosis'] as List? ?? [];
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(
              width: 28,
              height: 28,
              decoration: ext.iconContainer(AppColors.accent),
              child: Icon(Icons.local_hospital_rounded, size: 14, color: AppColors.accent),
            ),
            const SizedBox(width: 10),
            Text('summary.diagnoses'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          ]),
          const SizedBox(height: 12),
          if (diagnoses.isEmpty)
            Text('summary.no_diagnoses'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted))
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: diagnoses.map((d) {
                final code = d['code'] ?? '';
                final desc = d['description'] ?? d['label'] ?? '';
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.06),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppColors.primary.withValues(alpha: 0.12)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(code.toString(), style: GoogleFonts.heebo(fontSize: 10, fontWeight: FontWeight.w700, color: AppColors.primary)),
                      ),
                      const SizedBox(width: 8),
                      Text(desc.toString(), style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textSecondary)),
                    ],
                  ),
                );
              }).toList(),
            ),
        ],
      ),
    );
  }
}
