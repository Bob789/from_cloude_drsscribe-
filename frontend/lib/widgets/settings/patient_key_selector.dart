import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class _KeyOption {
  final String value;
  final String labelKey;
  final String descKey;
  final IconData icon;
  const _KeyOption(this.value, this.labelKey, this.descKey, this.icon);
}

const _options = [
  _KeyOption('national_id', 'settings.patient_key_national_id', 'settings.patient_key_national_id_desc', Icons.badge_rounded),
  _KeyOption('phone', 'settings.patient_key_phone', 'settings.patient_key_phone_desc', Icons.phone_rounded),
  _KeyOption('email', 'settings.patient_key_email', 'settings.patient_key_email_desc', Icons.email_rounded),
];

class PatientKeySelector extends ConsumerStatefulWidget {
  const PatientKeySelector({super.key});

  @override
  ConsumerState<PatientKeySelector> createState() => _PatientKeySelectorState();
}

class _PatientKeySelectorState extends ConsumerState<PatientKeySelector> {
  bool _saving = false;

  Future<void> _updateKeyType(String value) async {
    setState(() => _saving = true);
    try {
      await api.put('/auth/me/patient-key-type', data: {'patient_key_type': value});
      ref.invalidate(authProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('settings.patient_key_updated'.tr(), style: GoogleFonts.heebo()), backgroundColor: AppColors.success),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('common.update_error'.tr(), style: GoogleFonts.heebo()), backgroundColor: Colors.red),
        );
      }
    }
    setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(currentUserProvider);
    final current = user?.patientKeyType ?? 'national_id';
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(Icons.key_rounded, size: 18, color: AppColors.primary),
          const SizedBox(width: 8),
          Text('settings.patient_key_title'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
          if (_saving) ...[
            const SizedBox(width: 12),
            SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary)),
          ],
        ]),
        const SizedBox(height: 4),
        Text('settings.patient_key_subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
        const SizedBox(height: 14),
        ..._options.map((opt) => _buildOption(opt, current)),
      ]),
    );
  }

  Widget _buildOption(_KeyOption opt, String current) {
    final isSelected = opt.value == current;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: _saving ? null : () => _updateKeyType(opt.value),
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: isSelected ? AppColors.primary.withValues(alpha: 0.1) : Colors.transparent,
              border: Border.all(color: isSelected ? AppColors.primary : AppColors.cardBorder, width: isSelected ? 2 : 1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(children: [
              Icon(opt.icon, size: 20, color: isSelected ? AppColors.primary : AppColors.textMuted),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(opt.labelKey.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: isSelected ? AppColors.primary : AppColors.textPrimary)),
                Text(opt.descKey.tr(), style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textMuted)),
              ])),
              if (isSelected)
                Icon(Icons.check_circle_rounded, size: 20, color: AppColors.primary),
            ]),
          ),
        ),
      ),
    );
  }
}
