import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/theme_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class ThemeSelector extends ConsumerWidget {
  const ThemeSelector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentTheme = ref.watch(themeProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(width: 28, height: 28, decoration: ext.iconContainer(AppColors.primary), child: Icon(Icons.palette_rounded, size: 14, color: AppColors.primary)),
          const SizedBox(width: 10),
          Text('settings.theme_title'.tr(), style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        ]),
        const SizedBox(height: 6),
        Text('settings.theme_subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
        const SizedBox(height: 16),
        LayoutBuilder(builder: (context, constraints) {
          final cards = [
            _themeCard(ref, AppThemeStyle.aurora, 'settings.theme_aurora'.tr(), 'Aurora Neon', currentTheme == AppThemeStyle.aurora, AppColors.schemeFor(AppThemeStyle.aurora)),
            _themeCard(ref, AppThemeStyle.ember, 'settings.theme_ember'.tr(), 'Ember Warm', currentTheme == AppThemeStyle.ember, AppColors.schemeFor(AppThemeStyle.ember)),
            _themeCard(ref, AppThemeStyle.ocean, 'settings.theme_ocean'.tr(), 'Ocean Clean', currentTheme == AppThemeStyle.ocean, AppColors.schemeFor(AppThemeStyle.ocean)),
          ];
          if (constraints.maxWidth < 380) {
            // Narrow: stack vertically
            return Column(children: cards.map((c) => Padding(padding: const EdgeInsets.only(bottom: 10), child: c)).toList());
          }
          return Row(children: [
            Expanded(child: cards[0]),
            const SizedBox(width: 10),
            Expanded(child: cards[1]),
            const SizedBox(width: 10),
            Expanded(child: cards[2]),
          ]);
        }),
      ]),
    );
  }

  Widget _themeCard(WidgetRef ref, AppThemeStyle style, String label, String subtitle, bool isSelected, AppColorScheme scheme) {
    final isAurora = style == AppThemeStyle.aurora;
    final isEmber = style == AppThemeStyle.ember;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => ref.read(themeProvider.notifier).setTheme(style),
        borderRadius: BorderRadius.circular(16),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: scheme.background, borderRadius: BorderRadius.circular(16),
            border: Border.all(color: isSelected ? scheme.primary : scheme.cardBorder, width: isSelected ? 2.5 : 1),
            boxShadow: isSelected ? [BoxShadow(color: scheme.primary.withValues(alpha: 0.35), blurRadius: 20, spreadRadius: 2)] : [],
          ),
          child: Column(children: [
            _miniPreview(scheme, isAurora, isEmber),
            const SizedBox(height: 10),
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              _dot(scheme.primary, 12, isAurora ? scheme.primary.withValues(alpha: 0.4) : null),
              const SizedBox(width: 5),
              _dot(scheme.secondary, 10, null),
              const SizedBox(width: 5),
              _dot(scheme.accent, 10, null),
            ]),
            const SizedBox(height: 8),
            Text(label, style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w700, color: isSelected ? scheme.primary : AppColors.textPrimary), overflow: TextOverflow.ellipsis, maxLines: 1),
            Text(subtitle, style: GoogleFonts.heebo(fontSize: 10, color: AppColors.textMuted), overflow: TextOverflow.ellipsis, maxLines: 1),
            if (isSelected) ...[
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                decoration: BoxDecoration(color: scheme.primary.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(6), border: Border.all(color: scheme.primary.withValues(alpha: 0.3))),
                child: Text('settings.active'.tr(), style: GoogleFonts.heebo(fontSize: 10, fontWeight: FontWeight.w700, color: scheme.primary)),
              ),
            ],
          ]),
        ),
      ),
    );
  }

  Widget _miniPreview(AppColorScheme scheme, bool isAurora, bool isEmber) {
    return Container(
      width: double.infinity, padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: scheme.card, borderRadius: BorderRadius.circular(10),
        border: Border.all(color: isAurora ? scheme.primary.withValues(alpha: 0.3) : isEmber ? scheme.primary.withValues(alpha: 0.15) : Colors.white.withValues(alpha: 0.06)),
        boxShadow: isAurora ? [BoxShadow(color: scheme.primary.withValues(alpha: 0.15), blurRadius: 15)] : isEmber ? [BoxShadow(color: Colors.black.withValues(alpha: 0.3), blurRadius: 20, offset: const Offset(0, 4))] : [],
      ),
      child: Column(children: [
        Row(children: [
          Expanded(child: _miniStat(scheme, isAurora, isEmber)),
          const SizedBox(width: 4),
          Expanded(child: _miniStat(scheme, isAurora, isEmber)),
        ]),
        const SizedBox(height: 6),
        SizedBox(
          height: 28,
          child: Row(crossAxisAlignment: CrossAxisAlignment.end, mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [0.6, 0.9, 0.4, 0.7, 0.5].map((h) {
            return Container(
              width: 8, height: 28 * h,
              decoration: BoxDecoration(
                gradient: isAurora ? LinearGradient(begin: Alignment.bottomCenter, end: Alignment.topCenter, colors: [scheme.primary, scheme.secondary])
                    : isEmber ? LinearGradient(begin: Alignment.bottomCenter, end: Alignment.topCenter, colors: [scheme.primary, const Color(0xFFF8C05C)]) : null,
                color: (!isAurora && !isEmber) ? scheme.primary : null,
                borderRadius: BorderRadius.circular(3),
                boxShadow: isAurora ? [BoxShadow(color: scheme.primary.withValues(alpha: 0.3), blurRadius: 6)] : [],
              ),
            );
          }).toList()),
        ),
      ]),
    );
  }

  Widget _miniStat(AppColorScheme scheme, bool isAurora, bool isEmber) {
    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: scheme.background, borderRadius: BorderRadius.circular(6),
        border: Border.all(color: isAurora ? scheme.primary.withValues(alpha: 0.25) : isEmber ? scheme.primary.withValues(alpha: 0.12) : Colors.white.withValues(alpha: 0.06)),
        boxShadow: isAurora ? [BoxShadow(color: scheme.primary.withValues(alpha: 0.1), blurRadius: 8)] : [],
      ),
      child: Column(children: [
        Container(width: 12, height: 3, decoration: BoxDecoration(color: scheme.primary, borderRadius: BorderRadius.circular(2))),
        const SizedBox(height: 3),
        Container(width: 20, height: 3, decoration: BoxDecoration(color: scheme.textMuted, borderRadius: BorderRadius.circular(2))),
      ]),
    );
  }

  Widget _dot(Color color, double size, Color? glow) {
    return Container(
      width: size, height: size,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle, boxShadow: glow != null ? [BoxShadow(color: glow, blurRadius: 8, spreadRadius: 1)] : []),
    );
  }
}
