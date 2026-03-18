import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class PatientInfoCard extends StatelessWidget {
  final Map<String, dynamic> patient;

  const PatientInfoCard({super.key, required this.patient});

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
    final fields = <MapEntry<String, String>>[];
    if (patient['id_number'] != null) fields.add(MapEntry('patient_form.id_number'.tr(), patient['id_number']));
    if (patient['phone'] != null) fields.add(MapEntry('patient_form.phone'.tr(), patient['phone']));
    if (patient['email'] != null) fields.add(MapEntry('patient_form.email'.tr(), patient['email']));
    if (patient['dob'] != null) {
      final age = _calculateAge(patient['dob']);
      final dobDisplay = age.isNotEmpty ? '${patient['dob']}  (${'patient.age'.tr()} $age)' : patient['dob'];
      fields.add(MapEntry('patient_form.dob'.tr(), dobDisplay));
    }
    if (patient['profession'] != null) fields.add(MapEntry('patient_form.profession'.tr(), patient['profession']));
    if (patient['address'] != null) fields.add(MapEntry('patient_form.address'.tr(), patient['address']));
    final hasAllergies = patient['allergies'] != null && (patient['allergies'] as List).isNotEmpty;
    if (fields.isEmpty && !hasAllergies) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (fields.isNotEmpty)
          Container(
            padding: const EdgeInsets.all(20),
            decoration: ext.cardDecoration,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('patient.personal_details'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                const SizedBox(height: 14),
                ...fields.map((f) => _infoRow(f.key, f.value)),
              ],
            ),
          ),
        if (hasAllergies) ...[
          if (fields.isNotEmpty) const SizedBox(height: 16),
          _buildAllergies(ext),
        ],
      ],
    );
  }

  Widget _buildAllergies(MedScribeThemeExtension ext) {
    final allergies = patient['allergies'] as List;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.accent.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(ext.cardRadius),
        border: Border.all(color: AppColors.accent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(Icons.warning_amber_rounded, size: 18, color: AppColors.accent),
            const SizedBox(width: 8),
            Text('patient.allergies'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.accent)),
          ]),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8, runSpacing: 8,
            children: allergies.map((a) => Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(color: AppColors.accent.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)),
              child: Text(a.toString(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500, color: AppColors.accent)),
            )).toList(),
          ),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(children: [
        Flexible(flex: 2, child: Text(label, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textMuted))),
        const SizedBox(width: 8),
        Flexible(flex: 3, child: SelectableText(value, style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary))),
      ]),
    );
  }
}
