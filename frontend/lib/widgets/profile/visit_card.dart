import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/models/visit_model.dart';
import 'package:medscribe_ai/models/summary_model.dart';
import 'package:medscribe_ai/models/tag_model.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:dio/dio.dart';
import 'dart:html' as html;

class VisitCard extends ConsumerWidget {
  final VisitModel visit;
  final Future<void> Function(String tagId) onDeleteTag;
  final Future<void> Function(String tagId, TagModel tag) onEditTag;
  final Future<void> Function(String visitId, VisitModel visit) onEditVisit;

  const VisitCard({super.key, required this.visit, required this.onDeleteTag, required this.onEditTag, required this.onEditVisit});

  String _formatDate(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    } catch (_) { return dateStr; }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final summary = visit.summary;
    final transcription = visit.transcription;
    final urgency = summary?.urgency ?? 'low';
    final urgencyColor = ext.urgencyColors[urgency] ?? AppColors.textMuted;
    final isCompleted = visit.status == 'completed';
    final summarySource = summary?.source ?? 'ai';
    final currentUser = ref.watch(currentUserProvider);
    final canEdit = currentUser != null && (visit.doctorId == currentUser.id || currentUser.role == 'admin');

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: ext.cardDecoration,
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
          childrenPadding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
          leading: Container(width: 10, height: 10, decoration: BoxDecoration(color: urgencyColor, shape: BoxShape.circle)),
          title: _buildTitle(summarySource, canEdit),
          subtitle: Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Text(summary?.chiefComplaint ?? (isCompleted ? 'visit.completed'.tr() : 'visit.active'.tr()), maxLines: 2, overflow: TextOverflow.ellipsis, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
          ),
          trailing: _buildStatusBadge(isCompleted),
          children: _buildContent(context, summary, transcription, canEdit),
        ),
      ),
    );
  }

  Widget _buildTitle(String summarySource, bool canEdit) {
    return Row(children: [
      Expanded(child: Row(children: [
        Flexible(child: Text(_formatDate(visit.startTime), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary), overflow: TextOverflow.ellipsis)),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(color: (summarySource == 'manual' ? Colors.amber : AppColors.primary).withValues(alpha: 0.12), borderRadius: BorderRadius.circular(6)),
          child: Text(summarySource == 'manual' ? 'visit.manual'.tr() : 'AI', style: GoogleFonts.heebo(fontSize: 10, fontWeight: FontWeight.w600, color: summarySource == 'manual' ? Colors.amber.shade800 : AppColors.primary)),
        ),
      ])),
      if (visit.summary != null)
        IconButton(icon: Icon(Icons.print_rounded, size: 18, color: AppColors.primary), padding: const EdgeInsets.all(4), constraints: const BoxConstraints(), onPressed: () => _downloadPdf(visit.summary!.id), tooltip: 'הדפס סיכום'),
      if (canEdit)
        IconButton(icon: Icon(Icons.edit_rounded, size: 18, color: AppColors.textSecondary), padding: const EdgeInsets.all(4), constraints: const BoxConstraints(), onPressed: () => onEditVisit(visit.id, visit), tooltip: 'visit.edit'.tr()),
    ]);
  }

  void _downloadPdf(String summaryId) async {
    try {
      final dio = ApiClient().dio;
      final response = await dio.get(
        '/summaries/$summaryId/pdf',
        options: Options(responseType: ResponseType.bytes),
      );
      final blob = html.Blob([response.data], 'application/pdf');
      final url = html.Url.createObjectUrlFromBlob(blob);
      html.window.open(url, '_blank');
      html.Url.revokeObjectUrl(url);
    } catch (_) {}
  }

  Widget _buildStatusBadge(bool isCompleted) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: (isCompleted ? AppColors.secondary : AppColors.primary).withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)),
      child: Text(isCompleted ? 'status.completed'.tr() : 'status.active'.tr(), style: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w600, color: isCompleted ? AppColors.secondary : AppColors.primary)),
    );
  }

  List<Widget> _buildContent(BuildContext context, SummaryModel? summary, TranscriptionModel? transcription, bool canEdit) {
    return [
      if (summary != null) ...[
        _summarySection('visit.chief_complaint'.tr(), summary.chiefComplaint),
        _summarySection('visit.findings'.tr(), summary.findings),
        if (summary.diagnosis != null) _buildDiagnoses(summary.diagnosis),
        _summarySection('visit.treatment_plan'.tr(), summary.treatmentPlan),
        if (summary.recommendations != null) _buildRecommendations(summary.recommendations!),
      ] else
        Text('visit.no_summary'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
      if (summary != null && summary.tags.isNotEmpty) ...[
        const SizedBox(height: 10),
        _buildTags(summary.tags, canEdit),
      ],
      if (summary?.notes != null && summary!.notes!.isNotEmpty) ...[
        const SizedBox(height: 10),
        _buildNotes(summary.notes!),
      ],
      if (summary?.customFields != null && summary!.customFields!.isNotEmpty) ...[
        const SizedBox(height: 10),
        _buildCustomFields(summary.customFields!),
      ],
      if (transcription != null) ...[
        Padding(padding: const EdgeInsets.symmetric(vertical: 14), child: Divider(color: AppColors.cardBorder, height: 1)),
        _buildTranscription(context, transcription),
      ],
    ];
  }

  Widget _summarySection(String title, String? content) {
    if (content == null || content.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
        const SizedBox(height: 4),
        SelectableText(content, style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary, height: 1.5)),
      ]),
    );
  }

  Widget _buildDiagnoses(dynamic diagnosis) {
    final List items = diagnosis is List ? diagnosis : [];
    if (items.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('visit.diagnoses'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
        const SizedBox(height: 6),
        Wrap(spacing: 8, runSpacing: 6, children: items.map((d) {
          final code = d['code'] ?? '';
          final label = d['label'] ?? '';
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.08), borderRadius: BorderRadius.circular(8), border: Border.all(color: AppColors.primary.withValues(alpha: 0.12))),
            child: Text('$code - $label', style: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w500, color: AppColors.primary)),
          );
        }).toList()),
      ]),
    );
  }

  Widget _buildRecommendations(String recommendations) {
    return Container(
      width: double.infinity, margin: const EdgeInsets.only(top: 10), padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.06), borderRadius: BorderRadius.circular(10), border: Border.all(color: AppColors.primary.withValues(alpha: 0.1))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('visit.recommendations'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primary)),
        const SizedBox(height: 6),
        SelectableText(recommendations, style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textSecondary, height: 1.5)),
      ]),
    );
  }

  Widget _buildTags(List<TagModel> tags, bool canEdit) {
    return Wrap(spacing: 6, runSpacing: 6, children: tags.map((tag) {
      final color = tag.tagType == 'diagnosis' ? Colors.red : tag.tagType == 'symptom' ? Colors.amber.shade800 : tag.tagType == 'treatment' ? Colors.blue : Colors.grey;
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(6), border: Border.all(color: color.withValues(alpha: 0.25))),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Text(tag.tagLabel, style: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w500, color: color)),
          if (tag.id != null && canEdit) ...[
            const SizedBox(width: 4),
            InkWell(onTap: () => onEditTag(tag.id!, tag), child: Icon(Icons.edit_rounded, size: 13, color: color.withValues(alpha: 0.6))),
            const SizedBox(width: 2),
            InkWell(onTap: () => onDeleteTag(tag.id!), child: Icon(Icons.close_rounded, size: 13, color: color.withValues(alpha: 0.6))),
          ],
        ]),
      );
    }).toList());
  }

  Widget _buildNotes(String notes) {
    return Container(
      width: double.infinity, padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: AppColors.background, borderRadius: BorderRadius.circular(8)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('visit.notes'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
        const SizedBox(height: 4),
        SelectableText(notes, style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textSecondary, height: 1.5)),
      ]),
    );
  }

  Widget _buildCustomFields(List customFields) {
    return Container(
      width: double.infinity, padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: AppColors.secondary.withValues(alpha: 0.05), borderRadius: BorderRadius.circular(8), border: Border.all(color: AppColors.secondary.withValues(alpha: 0.1))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(Icons.tune_rounded, size: 14, color: AppColors.secondary),
          const SizedBox(width: 6),
          Text('visit.custom_fields'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.secondary)),
        ]),
        const SizedBox(height: 8),
        ...customFields.map((cf) => Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            SizedBox(width: 180, child: Text('${cf['field_name']}:', style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500, color: AppColors.textMuted))),
            Expanded(child: SelectableText(cf['value'] ?? '', style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary, height: 1.4))),
          ]),
        )),
      ]),
    );
  }

  Widget _buildTranscription(BuildContext context, TranscriptionModel transcription) {
    return Theme(
      data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        tilePadding: EdgeInsets.zero,
        title: Row(children: [
          Icon(Icons.description_rounded, size: 18, color: AppColors.textMuted),
          const SizedBox(width: 8),
          Text('visit.full_transcription'.tr(), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textSecondary)),
          const SizedBox(width: 8),
          Text('(${'visit.accuracy'.tr()}: ${((transcription.confidenceScore ?? 0) * 100).toStringAsFixed(0)}%)', style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textMuted)),
        ]),
        children: [
          Container(
            width: double.infinity, padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(color: AppColors.background, borderRadius: BorderRadius.circular(10)),
            child: SelectableText(transcription.fullText ?? '', style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textSecondary, height: 1.7)),
          ),
        ],
      ),
    );
  }
}
