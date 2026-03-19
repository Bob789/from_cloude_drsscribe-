import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class OceanTheme {
  static const background = Color(0xFF09090B);
  static const surface = Color(0xFF18181B);
  static const primary = Color(0xFF3B82F6);
  static const secondary = Color(0xFF8B5CF6);
  static const accent = Color(0xFFEF4444);
  static const success = Color(0xFF22C55E);
  static const warning = Color(0xFFF59E0B);
  static const textPrimary = Color(0xFFFAFAFA);
  static const textSecondary = Color(0xFFA1A1AA);
  static const textMuted = Color(0xFF71717A);

  static MedScribeThemeExtension get extension => MedScribeThemeExtension(
        cardDecoration: BoxDecoration(
          color: surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
        ),
        statCardDecoration: BoxDecoration(
          color: surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
        ),
        sidebarDecoration: BoxDecoration(color: background),
        selectedNavDecoration: BoxDecoration(
          color: primary,
          borderRadius: BorderRadius.circular(12),
        ),
        avatarRingDecoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: primary, width: 2),
        ),
        chartBarDefault: BoxDecoration(
          color: primary,
          borderRadius: BorderRadius.circular(6),
        ),
        chartBarHovered: BoxDecoration(
          color: secondary,
          borderRadius: BorderRadius.circular(6),
          boxShadow: [
            BoxShadow(
              color: secondary.withValues(alpha: 0.3),
              blurRadius: 12,
            ),
          ],
        ),
        buildIconContainer: (Color color) => BoxDecoration(
          color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(12),
        ),
        statCardLayout: StatCardLayout.verticalMinimal,
        statCardAspectRatio: 1.8,
        cardRadius: 16,
        navItemRadius: 12,
        selectedNavIconColor: Colors.white,
        selectedNavTextColor: Colors.white,
        success: success,
        dividerColor: Colors.white.withValues(alpha: 0.06),
        gradientColors: [primary, secondary],
        urgencyColors: {
          'critical': accent,
          'high': warning,
          'medium': secondary,
          'low': success,
        },
        statusColors: {
          'active': success,
          'pending': warning,
          'completed': primary,
          'cancelled': textMuted,
        },
      );

  static ThemeData buildTheme() {
    final base = GoogleFonts.heeboTextTheme(ThemeData.dark().textTheme);
    final heeboText = base.copyWith(
      displayLarge: GoogleFonts.heebo(fontSize: 48, fontWeight: FontWeight.w900, color: textPrimary),
      displayMedium: GoogleFonts.heebo(fontSize: 36, fontWeight: FontWeight.w900, color: textPrimary),
      headlineLarge: GoogleFonts.heebo(fontSize: 28, fontWeight: FontWeight.w800, color: textPrimary),
      headlineMedium: GoogleFonts.heebo(fontSize: 22, fontWeight: FontWeight.w700, color: textPrimary),
      titleLarge: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w600, color: textPrimary),
      titleMedium: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: textPrimary),
      titleSmall: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: textPrimary),
      bodyLarge: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w400, color: textPrimary),
      bodyMedium: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w400, color: textPrimary),
      bodySmall: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: textMuted),
      labelLarge: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: textPrimary),
      labelMedium: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: textMuted),
      labelSmall: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w500, color: textMuted),
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      colorScheme: ColorScheme.dark(
        primary: primary,
        secondary: secondary,
        error: accent,
        surface: surface,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: textPrimary,
        onError: Colors.white,
      ),
      textTheme: heeboText,
      appBarTheme: AppBarTheme(
        centerTitle: true,
        elevation: 0,
        backgroundColor: background,
        foregroundColor: textPrimary,
        titleTextStyle: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: textPrimary),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.06)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
        enabledBorder: UnderlineInputBorder(
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
        ),
        focusedBorder: UnderlineInputBorder(
          borderSide: BorderSide(color: primary, width: 2),
        ),
        filled: false,
        hintStyle: GoogleFonts.heebo(color: textMuted, fontSize: 14, fontWeight: FontWeight.w500),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          minimumSize: const Size(0, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          minimumSize: const Size(0, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
          textStyle: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w600),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        side: BorderSide(color: Colors.white.withValues(alpha: 0.08)),
        labelStyle: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: textPrimary),
      ),
      dividerTheme: DividerThemeData(color: Colors.white.withValues(alpha: 0.06), thickness: 1),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: surface,
        contentTextStyle: GoogleFonts.heebo(color: textPrimary),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        behavior: SnackBarBehavior.floating,
      ),
      extensions: [extension],
    );
  }
}
