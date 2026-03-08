import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class UrgencySelector extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;

  const UrgencySelector({super.key, required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final options = [('low', 'urgency.low'.tr(), Colors.green), ('medium', 'urgency.medium'.tr(), Colors.orange), ('high', 'urgency.high'.tr(), Colors.deepOrange), ('critical', 'urgency.critical'.tr(), Colors.red)];
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('visit.urgency_label'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        const SizedBox(height: 12),
        Wrap(spacing: 10, runSpacing: 8, children: options.map((o) {
          final isSelected = value == o.$1;
          return Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => onChanged(o.$1),
              borderRadius: BorderRadius.circular(10),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? o.$3.withValues(alpha: 0.15) : Colors.transparent,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: isSelected ? o.$3 : AppColors.cardBorder, width: isSelected ? 1.5 : 1),
                ),
                child: Text(o.$2, style: GoogleFonts.heebo(fontSize: 13, fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400, color: isSelected ? o.$3 : AppColors.textSecondary)),
              ),
            ),
          );
        }).toList()),
      ]),
    );
  }
}

class NoteTextField extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final int maxLines;

  const NoteTextField({super.key, required this.label, required this.controller, this.maxLines = 3});

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        const SizedBox(height: 10),
        TextField(
          controller: controller,
          maxLines: maxLines,
          style: GoogleFonts.heebo(color: AppColors.textPrimary, fontSize: 14, height: 1.6),
          decoration: InputDecoration(
            filled: true, fillColor: AppColors.background,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
            contentPadding: const EdgeInsets.all(14),
          ),
        ),
      ]),
    );
  }
}

class NoteSaveButton extends StatelessWidget {
  final bool isLoading;
  final VoidCallback? onPressed;

  const NoteSaveButton({super.key, required this.isLoading, this.onPressed});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: isLoading ? null : onPressed,
          borderRadius: BorderRadius.circular(14),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 16),
            decoration: BoxDecoration(gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]), borderRadius: BorderRadius.circular(14)),
            child: Center(
              child: isLoading
                  ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : Text('common.save'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white)),
            ),
          ),
        ),
      ),
    );
  }
}
