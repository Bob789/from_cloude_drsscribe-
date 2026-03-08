import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/services/api_client.dart';

class LanguageSelector extends ConsumerWidget {
  const LanguageSelector({super.key});

  static const _languages = [
    _Lang('he', 'עברית', '🇮🇱'),
    _Lang('en', 'English', '🇺🇸'),
    _Lang('de', 'Deutsch', '🇩🇪'),
    _Lang('es', 'Español', '🇪🇸'),
    _Lang('fr', 'Français', '🇫🇷'),
    _Lang('pt', 'Português', '🇧🇷'),
    _Lang('ko', '한국어', '🇰🇷'),
    _Lang('it', 'Italiano', '🇮🇹'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final currentCode = context.locale.languageCode;
    final current = _languages.firstWhere((l) => l.code == currentCode, orElse: () => _languages[0]);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(Icons.language_rounded, size: 20, color: AppColors.primary),
          const SizedBox(width: 8),
          Text('settings.language'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        ]),
        const SizedBox(height: 14),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.background,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.cardBorder),
          ),
          child: DropdownButton<String>(
            value: current.code,
            isExpanded: true,
            underline: const SizedBox.shrink(),
            dropdownColor: AppColors.card,
            borderRadius: BorderRadius.circular(12),
            icon: Icon(Icons.expand_more_rounded, size: 20, color: AppColors.textMuted),
            selectedItemBuilder: (context) => _languages.map((lang) => Row(children: [
              Text(lang.flag, style: const TextStyle(fontSize: 20)),
              const SizedBox(width: 10),
              Text(lang.label, style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
            ])).toList(),
            items: _languages.map((lang) {
              final isSelected = lang.code == currentCode;
              return DropdownMenuItem<String>(
                value: lang.code,
                child: Row(children: [
                  Text(lang.flag, style: const TextStyle(fontSize: 20)),
                  const SizedBox(width: 10),
                  Text(lang.label, style: GoogleFonts.heebo(fontSize: 14, fontWeight: isSelected ? FontWeight.w700 : FontWeight.w400, color: isSelected ? AppColors.primary : AppColors.textPrimary)),
                  if (isSelected) ...[
                    const Spacer(),
                    Icon(Icons.check_rounded, size: 18, color: AppColors.primary),
                  ],
                ]),
              );
            }).toList(),
            onChanged: (code) async {
              if (code == null || code == currentCode) return;
              await context.setLocale(Locale(code));
              try {
                await ApiClient().dio.put('/auth/me/language', data: {'language': code});
              } catch (_) {}
            },
          ),
        ),
      ]),
    );
  }
}

class _Lang {
  final String code;
  final String label;
  final String flag;
  const _Lang(this.code, this.label, this.flag);
}
