import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class AuroraTheme {
  static const background = Color(0xFF0A0A0F);
  static const surface = Color(0xFF12121A);
  static const primary = Color(0xFF00F0FF);
  static const secondary = Color(0xFFBF5AF2);
  static const accent = Color(0xFFFF375F);
  static const success = Color(0xFF30D158);
  static const warning = Color(0xFFFFD60A);
  static const textPrimary = Color(0xFFFFFFFF);
  static const textSecondary = Color(0xFFB4B4C4);
  static const textMuted = Color(0xFF6B6B7F);

  static MedScribeThemeExtension get extension => MedScribeThemeExtension(
        cardDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              primary.withValues(alpha: 0.12),
              secondary.withValues(alpha: 0.08),
            ],
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: primary.withValues(alpha: 0.35), width: 1.5),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.15),
              blurRadius: 30,
              spreadRadius: 1,
            ),
            BoxShadow(
              color: secondary.withValues(alpha: 0.08),
              blurRadius: 50,
              spreadRadius: -5,
            ),
          ],
        ),
        statCardDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              primary.withValues(alpha: 0.15),
              secondary.withValues(alpha: 0.10),
              accent.withValues(alpha: 0.05),
            ],
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: primary.withValues(alpha: 0.4), width: 1.5),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.25),
              blurRadius: 35,
              spreadRadius: 2,
            ),
            BoxShadow(
              color: secondary.withValues(alpha: 0.12),
              blurRadius: 60,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        sidebarDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              surface,
              background,
              Color(0xFF08081A),
            ],
          ),
          border: Border(
            left: BorderSide(
              color: primary.withValues(alpha: 0.25),
              width: 1.5,
            ),
          ),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.08),
              blurRadius: 40,
              spreadRadius: -10,
            ),
          ],
        ),
        selectedNavDecoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.centerRight,
            end: Alignment.centerLeft,
            colors: [
              primary.withValues(alpha: 0.35),
              secondary.withValues(alpha: 0.20),
            ],
          ),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: primary.withValues(alpha: 0.6), width: 1.5),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.35),
              blurRadius: 20,
              spreadRadius: 1,
            ),
          ],
        ),
        avatarRingDecoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: LinearGradient(
            colors: [primary, secondary, accent],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.5),
              blurRadius: 20,
              spreadRadius: 3,
            ),
            BoxShadow(
              color: secondary.withValues(alpha: 0.3),
              blurRadius: 30,
              spreadRadius: 1,
            ),
          ],
        ),
        chartBarDefault: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.bottomCenter,
            end: Alignment.topCenter,
            colors: [primary, secondary],
          ),
          borderRadius: BorderRadius.vertical(top: Radius.circular(10)),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.3),
              blurRadius: 15,
              spreadRadius: 1,
            ),
          ],
        ),
        chartBarHovered: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.bottomCenter,
            end: Alignment.topCenter,
            colors: [primary, secondary, accent],
          ),
          borderRadius: BorderRadius.vertical(top: Radius.circular(10)),
          boxShadow: [
            BoxShadow(
              color: primary.withValues(alpha: 0.6),
              blurRadius: 25,
              spreadRadius: 3,
            ),
          ],
        ),
        buildIconContainer: (Color color) => BoxDecoration(
          color: color.withValues(alpha: 0.2),
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha: 0.4),
              blurRadius: 25,
              spreadRadius: 1,
            ),
          ],
        ),
        statCardLayout: StatCardLayout.verticalGlow,
        statCardAspectRatio: 1.8,
        cardRadius: 20,
        navItemRadius: 14,
        selectedNavIconColor: Colors.white,
        selectedNavTextColor: Colors.white,
        success: success,
        dividerColor: primary.withValues(alpha: 0.1),
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
      displayLarge: GoogleFonts.heebo(fontSize: 42, fontWeight: FontWeight.w900, color: textPrimary),
      displayMedium: GoogleFonts.heebo(fontSize: 32, fontWeight: FontWeight.w900, color: textPrimary),
      headlineLarge: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: textPrimary),
      headlineMedium: GoogleFonts.heebo(fontSize: 20, fontWeight: FontWeight.w700, color: textPrimary),
      titleLarge: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: textPrimary),
      titleMedium: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: textPrimary),
      titleSmall: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: textPrimary),
      bodyLarge: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w400, color: textPrimary),
      bodyMedium: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w400, color: textPrimary),
      bodySmall: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w400, color: textSecondary),
      labelLarge: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w500, color: textPrimary, letterSpacing: 0.5),
      labelMedium: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: textMuted, letterSpacing: 1.2),
      labelSmall: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w400, color: textMuted, letterSpacing: 0.8),
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
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(color: primary.withValues(alpha: 0.15)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: primary.withValues(alpha: 0.15)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: primary, width: 1.5),
        ),
        filled: true,
        fillColor: surface,
        hintStyle: GoogleFonts.heebo(color: textMuted, fontSize: 14),
        contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Color(0xFF000000),
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
          minimumSize: const Size(0, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, letterSpacing: 0.5),
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
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        side: BorderSide(color: primary.withValues(alpha: 0.2)),
        labelStyle: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: textPrimary),
      ),
      dividerTheme: DividerThemeData(color: primary.withValues(alpha: 0.1), thickness: 1),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primary,
        foregroundColor: Color(0xFF000000),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: surface,
        contentTextStyle: GoogleFonts.heebo(color: textPrimary),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        behavior: SnackBarBehavior.floating,
      ),
      extensions: [extension],
    );
  }
}
