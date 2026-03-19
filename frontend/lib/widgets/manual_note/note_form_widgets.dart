import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/screens/manual_note_screen.dart';

class UrgencySelector extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;

  const UrgencySelector({super.key, required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final options = [
      ('low', 'urgency.low'.tr(), const Color(0xFF16A34A)),
      ('medium', 'urgency.medium'.tr(), const Color(0xFFEA580C)),
      ('high', 'urgency.high'.tr(), const Color(0xFFDC2626)),
      ('critical', 'urgency.critical'.tr(), const Color(0xFF9F1239)),
    ];
    return Wrap(spacing: 8, runSpacing: 8, children: options.map((o) {
      final isSelected = value == o.$1;
      return Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => onChanged(o.$1),
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
            decoration: BoxDecoration(
              color: isSelected ? o.$3.withValues(alpha: 0.15) : Colors.transparent,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: isSelected ? o.$3.withValues(alpha: 0.5) : const Color(0xFFC3C9D4)),
            ),
            child: Text(o.$2, style: GoogleFonts.rubik(fontSize: 13, fontWeight: isSelected ? FontWeight.w700 : FontWeight.w400, color: isSelected ? o.$3 : const Color(0xFF555555))),
          ),
        ),
      );
    }).toList());
  }
}

class NoteTextField extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final int maxLines;

  const NoteTextField({super.key, required this.label, required this.controller, this.maxLines = 3});

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: GoogleFonts.rubik(fontSize: 20, fontWeight: FontWeight.w800, color: kNavy)),
      const SizedBox(height: 8),
      TextField(
        controller: controller,
        maxLines: maxLines,
        style: GoogleFonts.heebo(color: const Color(0xFF111111), fontSize: 14, height: 1.6),
        decoration: InputDecoration(
          filled: true,
          fillColor: Colors.white.withValues(alpha: 0.65),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kNavy, width: 1.5)),
          contentPadding: const EdgeInsets.all(12),
        ),
      ),
    ]);
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
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 15),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [kNavyLight, kNavy]),
              borderRadius: BorderRadius.circular(10),
              boxShadow: [BoxShadow(color: kNavyLight.withValues(alpha: 0.3), blurRadius: 20)],
            ),
            child: Center(
              child: isLoading
                  ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : Row(mainAxisSize: MainAxisSize.min, children: [
                      const Icon(Icons.save_rounded, color: Colors.white, size: 18),
                      const SizedBox(width: 8),
                      Text('common.save'.tr(), style: GoogleFonts.rubik(fontSize: 16, fontWeight: FontWeight.w800, color: Colors.white)),
                    ]),
            ),
          ),
        ),
      ),
    );
  }
}
