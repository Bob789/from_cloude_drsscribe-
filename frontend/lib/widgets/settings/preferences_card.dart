import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class PreferencesCard extends StatefulWidget {
  const PreferencesCard({super.key});

  @override
  State<PreferencesCard> createState() => _PreferencesCardState();
}

class _PreferencesCardState extends State<PreferencesCard> {
  bool _notifications = true;
  String _recordingFormat = 'webm';

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('settings.preferences'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 8),
        _switchRow('settings.notifications'.tr(), _notifications, (v) => setState(() => _notifications = v), Icons.notifications_rounded),
        Divider(color: AppColors.cardBorder, height: 1),
        _dropdownRow('settings.recording_format'.tr(), _recordingFormat, {'webm': 'WebM', 'wav': 'WAV'}, (v) => setState(() => _recordingFormat = v ?? 'webm'), Icons.audio_file_rounded),
      ]),
    );
  }

  Widget _switchRow(String label, bool value, ValueChanged<bool> onChanged, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(children: [
        Icon(icon, size: 18, color: AppColors.textMuted),
        const SizedBox(width: 12),
        Expanded(child: Text(label, style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textPrimary))),
        Switch(value: value, onChanged: onChanged, activeColor: AppColors.primary, inactiveTrackColor: AppColors.background),
      ]),
    );
  }

  Widget _dropdownRow(String label, String value, Map<String, String> options, ValueChanged<String?> onChanged, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(children: [
        Icon(icon, size: 18, color: AppColors.textMuted),
        const SizedBox(width: 12),
        Expanded(child: Text(label, style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textPrimary))),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
          decoration: BoxDecoration(color: AppColors.background, borderRadius: BorderRadius.circular(8), border: Border.all(color: AppColors.cardBorder)),
          child: DropdownButton<String>(
            value: value, underline: const SizedBox.shrink(), dropdownColor: AppColors.card,
            style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
            icon: Icon(Icons.expand_more_rounded, size: 18, color: AppColors.textMuted),
            items: options.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
            onChanged: onChanged,
          ),
        ),
      ]),
    );
  }
}
