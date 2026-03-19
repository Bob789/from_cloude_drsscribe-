import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class PatientHeader extends StatelessWidget {
  final Map<String, dynamic> patient;
  final String patientId;

  const PatientHeader({super.key, required this.patient, required this.patientId});

  String _calculateAge(String dobStr) {
    try {
      final dob = DateTime.parse(dobStr);
      final now = DateTime.now();
      int age = now.year - dob.year;
      if (now.month < dob.month || (now.month == dob.month && now.day < dob.day)) age--;
      return '$age';
    } catch (_) {
      return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final name = patient['name'] ?? '';
    final initials = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return Row(
      children: [
        IconButton(
          onPressed: () => context.go('/patients'),
          icon: Icon(Icons.arrow_forward_rounded, color: AppColors.textSecondary),
          style: IconButton.styleFrom(
            backgroundColor: AppColors.card,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        ),
        const SizedBox(width: 14),
        Container(
          width: 48, height: 48,
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: ext.gradientColors, begin: Alignment.topLeft, end: Alignment.bottomRight),
            borderRadius: BorderRadius.circular(ext.cardRadius * 0.7),
          ),
          child: Center(child: Text(initials, style: GoogleFonts.heebo(fontSize: 20, fontWeight: FontWeight.w700, color: Colors.white))),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SelectableText(name, style: GoogleFonts.heebo(fontSize: 22, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
              if (patient['phone'] != null)
                SelectableText(patient['phone'], style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
            ],
          ),
        ),
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => context.go('/patients/$patientId/edit'),
            borderRadius: BorderRadius.circular(10),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(border: Border.all(color: AppColors.cardBorder), borderRadius: BorderRadius.circular(10)),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.edit_rounded, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 6),
                  Text('common.edit'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textSecondary)),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
