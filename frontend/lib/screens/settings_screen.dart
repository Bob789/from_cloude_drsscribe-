import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/logout_dialog.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/widgets/settings/theme_selector.dart';
import 'package:medscribe_ai/widgets/settings/preferences_card.dart';
import 'package:medscribe_ai/widgets/settings/patient_key_selector.dart';
import 'package:medscribe_ai/widgets/settings/language_selector.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 600),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('settings.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
              const SizedBox(height: 4),
              Text('settings.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
              const SizedBox(height: 24),
              _buildProfileCard(user, ext),
              const SizedBox(height: 16),
              const ThemeSelector(),
              const SizedBox(height: 16),
              const LanguageSelector(),
              const SizedBox(height: 16),
              const PreferencesCard(),
              const SizedBox(height: 16),
              const PatientKeySelector(),
              const SizedBox(height: 24),
              _buildLogoutButton(context, ref),
            ]),
          ),
        ),
      ),
    );
  }

  Widget _buildProfileCard(dynamic user, MedScribeThemeExtension ext) {
    final name = user?.name ?? '';
    final initials = name.isNotEmpty ? name[0].toUpperCase() : '?';
    final hasAvatar = user?.avatarUrl != null;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('settings.profile'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 14),
        Row(children: [
          Container(
            width: 48, height: 48,
            decoration: BoxDecoration(gradient: LinearGradient(colors: ext.gradientColors, begin: Alignment.topLeft, end: Alignment.bottomRight), shape: BoxShape.circle),
            child: hasAvatar
                ? ClipOval(child: Image.network(user!.avatarUrl!, fit: BoxFit.cover, errorBuilder: (_, __, ___) => Center(child: Text(initials, style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: Colors.white)))))
                : Center(child: Text(initials, style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: Colors.white))),
          ),
          const SizedBox(width: 14),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(name, style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
            Text(user?.email ?? '', style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
          ]),
        ]),
      ]),
    );
  }

  Widget _buildLogoutButton(BuildContext context, WidgetRef ref) {
    return Center(
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => showLogoutDialog(context, ref),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            decoration: BoxDecoration(border: Border.all(color: AppColors.accent.withValues(alpha: 0.3)), borderRadius: BorderRadius.circular(12)),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.logout_rounded, size: 18, color: AppColors.accent),
              const SizedBox(width: 8),
              Text('settings.logout'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w500, color: AppColors.accent)),
            ]),
          ),
        ),
      ),
    );
  }
}
