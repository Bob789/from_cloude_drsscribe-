import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/app_theme.dart';

class EmptyState extends StatelessWidget {
  final IconData icon;
  final String message;
  final String? hint;

  const EmptyState({super.key, required this.icon, required this.message, this.hint});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 48, color: AppColors.textMuted.withValues(alpha: 0.4)),
          const SizedBox(height: 16),
          Text(message, style: GoogleFonts.heebo(fontSize: 16, color: AppColors.textSecondary)),
          if (hint != null) ...[
            const SizedBox(height: 8),
            Text(hint!, style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
          ],
        ],
      ),
    );
  }
}
