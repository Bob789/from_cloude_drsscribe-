import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';

/// Shows a confirmation dialog before logging out the user.
/// 
/// Returns a Future that resolves when the logout process is complete.
/// If the user cancels, the Future completes immediately without action.
Future<void> showLogoutDialog(BuildContext context, WidgetRef ref) async {
  final result = await showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      backgroundColor: AppColors.card,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Text(
        'settings.logout_title'.tr(),
        style: GoogleFonts.heebo(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: AppColors.textPrimary,
        ),
      ),
      content: Text(
        'settings.logout_confirm'.tr(),
        style: GoogleFonts.heebo(
          fontSize: 14,
          color: AppColors.textSecondary,
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(false),
          child: Text(
            'common.cancel'.tr(),
            style: GoogleFonts.heebo(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.textMuted,
            ),
          ),
        ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(true),
          child: Text(
            'settings.logout_button'.tr(),
            style: GoogleFonts.heebo(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppColors.accent,
            ),
          ),
        ),
      ],
    ),
  );

  if (result == true && context.mounted) {
    await ref.read(authProvider.notifier).signOut();
    if (context.mounted) {
      context.go('/login');
    }
  }
}
