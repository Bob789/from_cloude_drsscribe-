import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class NoteSuccessView extends StatelessWidget {
  final VoidCallback onNewNote;
  final VoidCallback onGoToPatients;

  const NoteSuccessView({super.key, required this.onNewNote, required this.onGoToPatients});

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 440),
          child: Container(
            padding: const EdgeInsets.all(40),
            decoration: ext.cardDecoration,
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Container(
                width: 64, height: 64,
                decoration: BoxDecoration(color: ext.success.withValues(alpha: 0.12), shape: BoxShape.circle),
                child: Icon(Icons.check_rounded, size: 32, color: ext.success),
              ),
              const SizedBox(height: 20),
              Text('common.saved_success'.tr(), style: GoogleFonts.heebo(fontSize: 20, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
              const SizedBox(height: 8),
              Text('manual_note.success_subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
              const SizedBox(height: 28),
              Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                OutlinedButton(onPressed: onNewNote, child: Text('manual_note.new_summary'.tr(), style: GoogleFonts.heebo(fontSize: 14))),
                const SizedBox(width: 12),
                FilledButton(onPressed: onGoToPatients, child: Text('common.back'.tr(), style: GoogleFonts.heebo(fontSize: 14))),
              ]),
            ]),
          ),
        ),
      ),
    );
  }
}
