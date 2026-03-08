import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/models/search_result_model.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class SearchResultCard extends StatelessWidget {
  final SearchResultModel result;

  const SearchResultCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final chiefComplaint = _strip(result.displayChiefComplaint ?? '');
    final findings = _strip(result.displayFindings ?? '');
    final fullText = _strip(result.displayFullText ?? '');
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            if (result.patientDisplayId != null) {
              context.go('/patients/${result.patientDisplayId}');
            }
          },
          borderRadius: BorderRadius.circular(ext.cardRadius),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: ext.cardDecoration,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    if (result.urgency != null) ...[
                      _buildUrgencyBadge(result.urgency!),
                      const SizedBox(width: 8),
                    ],
                    Expanded(
                      child: Text(result.patientName ?? 'search.patient_label'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w700, fontSize: 15, color: AppColors.textPrimary)),
                    ),
                    if (result.createdAt != null)
                      Text(_formatDate(result.createdAt!), style: GoogleFonts.heebo(color: AppColors.textMuted, fontSize: 11)),
                  ],
                ),
                if (chiefComplaint.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('search.complaint_label'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                      Expanded(child: Text(chiefComplaint, maxLines: 2, overflow: TextOverflow.ellipsis, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary, height: 1.4))),
                    ],
                  ),
                ],
                if (findings.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('search.findings_label'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
                      Expanded(child: Text(findings, maxLines: 2, overflow: TextOverflow.ellipsis, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary, height: 1.4))),
                    ],
                  ),
                ],
                if (chiefComplaint.isEmpty && findings.isEmpty && fullText.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Text(fullText, maxLines: 3, overflow: TextOverflow.ellipsis, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary, height: 1.4)),
                ],
                if (result.tags.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 4,
                    runSpacing: 4,
                    children: result.tags.take(6).map((t) => Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
                      ),
                      child: Text(t, style: GoogleFonts.heebo(fontSize: 10, fontWeight: FontWeight.w500, color: AppColors.primary)),
                    )).toList(),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildUrgencyBadge(String urgency) {
    final urgencyConfig = {
      'low': (Colors.green, 'urgency.low'.tr()),
      'medium': (Colors.orange, 'urgency.medium'.tr()),
      'high': (Colors.deepOrange, 'urgency.high'.tr()),
      'critical': (Colors.red, 'urgency.critical'.tr()),
    };
    final (color, label) = urgencyConfig[urgency] ?? (Colors.grey, urgency);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(4)),
      child: Text(label, style: GoogleFonts.heebo(fontSize: 10, fontWeight: FontWeight.w600, color: color)),
    );
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}/${date.year}';
    } catch (_) {
      return dateStr;
    }
  }

  String _strip(String text) => text.replaceAll(RegExp(r'<em>|</em>'), '');
}
