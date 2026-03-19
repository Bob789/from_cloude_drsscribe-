import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class EmberTheme {
  static const background = Color(0xFF0D0B0E);
  static const surface = Color(0xFF1A1620);
  static const primary = Color(0xFFF5A623);
  static const secondary = Color(0xFFE8735A);
  static const accent = Color(0xFFCF4655);
  static const success = Color(0xFF7EC699);
  static const warning = Color(0xFFF5C842);
  static const textPrimary = Color(0xFFF2E8DC);
  static const textSecondary = Color(0xFFC5B8A8);
  static const textMuted = Color(0xFF8A7F72);

  static MedScribeThemeExtension get extension => MedScribeThemeExtension(
        cardDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topRight,
            end: Alignment.bottomLeft,
            colors: [
              Color(0xFF241C2E),
              Color(0xFF1A1620),
              Color(0xFF18121E),
            ],
          ),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: primary.withValues(alpha: 0.2), width: 1.2),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.5),
              blurRadius: 40,
              offset: const Offset(0, 10),
            ),
            BoxShadow(
              color: primary.withValues(alpha: 0.06),
              blurRadius: 60,
              spreadRadius: -5,
            ),
          ],
        ),
        statCardDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topRight,
            end: Alignment.bottomLeft,
            colors: [
              Color(0xFF2A1F32),
              Color(0xFF1E1828),
              Color(0xFF1A1420),
            ],
          ),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: primary.withValues(alpha: 0.25), width: 1.2),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.55),
              blurRadius: 45,
              offset: const Offset(0, 12),
            ),
            BoxShadow(
              color: primary.withValues(alpha: 0.1),
              blurRadius: 35,
              spreadRadius: -2,
            ),
          ],
        ),
        sidebarDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF1A1620),
              background,
            ],
          ),
          border: Border(
            left: BorderSide(color: primary.withValues(alpha: 0.15), width: 1.2),
          ),
        ),
        selectedNavDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.centerRight,
            end: Alignment.centerLeft,
            colors: [
              primary.withValues(alpha: 0.25),
              secondary.withValues(alpha: 0.12),
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: primary.withValues(alpha: 0.4), width: 1.2),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.2),
              blurRadius: 18,
              spreadRadius: 1,
            ),
          ],
        ),
        avatarRingDecoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: LinearGradient(
            colors: [primary, secondary],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.35),
              blurRadius: 18,
              spreadRadius: 2,
            ),
          ],
        ),
        chartBarDefault: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.bottomCenter,
            end: Alignment.topCenter,
            colors: [primary, Color(0xFFF8C05C)],
          ),
          borderRadius: BorderRadius.vertical(top: Radius.circular(8)),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.3),
              blurRadius: 12,
              spreadRadius: 1,
            ),
          ],
        ),
        chartBarHovered: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.bottomCenter,
            end: Alignment.topCenter,
            colors: [secondary, primary],
          ),
          borderRadius: BorderRadius.vertical(top: Radius.circular(8)),
          boxShadow: [
            BoxShadow(
              color: secondary.withValues(alpha: 0.45),
              blurRadius: 20,
              spreadRadius: 2,
            ),
          ],
        ),
        buildIconContainer: (Color color) => BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              color.withValues(alpha: 0.25),
              color.withValues(alpha: 0.10),
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha: 0.2),
              blurRadius: 15,
              spreadRadius: 1,
            ),
          ],
        ),
        statCardLayout: StatCardLayout.horizontalLuxury,
        statCardAspectRatio: 2.2,
        cardRadius: 24,
        navItemRadius: 16,
        selectedNavIconColor: primary,
        selectedNavTextColor: primary,
        success: success,
        dividerColor: primary.withValues(alpha: 0.08),
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
      displayLarge: GoogleFonts.heebo(fontSize: 36, fontWeight: FontWeight.w800, color: textPrimary),
      displayMedium: GoogleFonts.heebo(fontSize: 32, fontWeight: FontWeight.w800, color: textPrimary),
      headlineLarge: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w700, color: textPrimary),
      headlineMedium: GoogleFonts.heebo(fontSize: 20, fontWeight: FontWeight.w700, color: textPrimary),
      titleLarge: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w600, color: textPrimary),
      titleMedium: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: textPrimary),
      titleSmall: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: textPrimary),
      bodyLarge: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w400, color: textPrimary),
      bodyMedium: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w400, color: textPrimary),
      bodySmall: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w400, color: textSecondary),
      labelLarge: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w500, color: textPrimary, letterSpacing: 0.4),
      labelMedium: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500, color: textMuted, letterSpacing: 0.8),
      labelSmall: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w400, color: textMuted, letterSpacing: 0.6),
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
        onPrimary: Color(0xFF000000),
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
          borderRadius: BorderRadius.circular(24),
          side: BorderSide(color: primary.withValues(alpha: 0.1)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
        enabledBorder: UnderlineInputBorder(
          borderSide: BorderSide(color: textMuted.withValues(alpha: 0.3)),
        ),
        focusedBorder: UnderlineInputBorder(
          borderSide: BorderSide(color: primary, width: 2),
        ),
        filled: false,
        hintStyle: GoogleFonts.heebo(color: textMuted, fontSize: 14),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Color(0xFF000000),
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          minimumSize: const Size(0, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          minimumSize: const Size(0, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          side: BorderSide(color: primary.withValues(alpha: 0.3)),
          textStyle: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w600),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        side: BorderSide(color: primary.withValues(alpha: 0.2)),
        labelStyle: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: textPrimary),
      ),
      dividerTheme: DividerThemeData(color: primary.withValues(alpha: 0.08), thickness: 1),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primary,
        foregroundColor: Color(0xFF000000),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: surface,
        contentTextStyle: GoogleFonts.heebo(color: textPrimary),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        behavior: SnackBarBehavior.floating,
      ),
      extensions: [extension],
    );
  }
}
