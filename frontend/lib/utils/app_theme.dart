import 'package:flutter/material.dart';
import 'package:medscribe_ai/utils/themes/aurora_theme.dart';
import 'package:medscribe_ai/utils/themes/ember_theme.dart';
import 'package:medscribe_ai/utils/themes/ocean_theme.dart';

enum AppThemeStyle { aurora, ember, ocean }

class AppColorScheme {
  final Color background;
  final Color card;
  final Color primary;
  final Color primaryLight;
  final Color secondary;
  final Color accent;
  final Color success;
  final Color warning;
  final Color textPrimary;
  final Color textSecondary;
  final Color textMuted;
  final Color border;
  final Color cardBorder;

  const AppColorScheme({
    required this.background,
    required this.card,
    required this.primary,
    required this.primaryLight,
    required this.secondary,
    required this.accent,
    required this.success,
    required this.warning,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.border,
    required this.cardBorder,
  });
}

class AppColors {
  static AppColorScheme _current = _aurora;

  static const _aurora = AppColorScheme(
    background: Color(0xFF0A0A0F),
    card: Color(0xFF12121A),
    primary: Color(0xFF00F0FF),
    primaryLight: Color(0xFF66F3FF),
    secondary: Color(0xFFBF5AF2),
    accent: Color(0xFFFF375F),
    success: Color(0xFF30D158),
    warning: Color(0xFFFFD60A),
    textPrimary: Color(0xFFFFFFFF),
    textSecondary: Color(0xFFB4B4C4),
    textMuted: Color(0xFF6B6B7F),
    border: Color(0x26FFFFFF),
    cardBorder: Color(0x2600F0FF),
  );

  static const _ember = AppColorScheme(
    background: Color(0xFF0D0B0E),
    card: Color(0xFF1A1620),
    primary: Color(0xFFF5A623),
    primaryLight: Color(0xFFF8C05C),
    secondary: Color(0xFFE8735A),
    accent: Color(0xFFCF4655),
    success: Color(0xFF7EC699),
    warning: Color(0xFFF5C842),
    textPrimary: Color(0xFFF2E8DC),
    textSecondary: Color(0xFFC5B8A8),
    textMuted: Color(0xFF8A7F72),
    border: Color(0x1AF5A623),
    cardBorder: Color(0x1AF5A623),
  );

  static const _ocean = AppColorScheme(
    background: Color(0xFF09090B),
    card: Color(0xFF18181B),
    primary: Color(0xFF3B82F6),
    primaryLight: Color(0xFF60A5FA),
    secondary: Color(0xFF8B5CF6),
    accent: Color(0xFFEF4444),
    success: Color(0xFF22C55E),
    warning: Color(0xFFF59E0B),
    textPrimary: Color(0xFFFAFAFA),
    textSecondary: Color(0xFFA1A1AA),
    textMuted: Color(0xFF71717A),
    border: Color(0x0FFFFFFF),
    cardBorder: Color(0x0FFFFFFF),
  );

  static void setTheme(AppThemeStyle style) {
    switch (style) {
      case AppThemeStyle.aurora:
        _current = _aurora;
      case AppThemeStyle.ember:
        _current = _ember;
      case AppThemeStyle.ocean:
        _current = _ocean;
    }
  }

  static Color get background => _current.background;
  static Color get card => _current.card;
  static Color get primary => _current.primary;
  static Color get primaryLight => _current.primaryLight;
  static Color get secondary => _current.secondary;
  static Color get accent => _current.accent;
  static Color get success => _current.success;
  static Color get warning => _current.warning;
  static Color get textPrimary => _current.textPrimary;
  static Color get textSecondary => _current.textSecondary;
  static Color get textMuted => _current.textMuted;
  static Color get border => _current.border;
  static Color get cardBorder => _current.cardBorder;

  static AppColorScheme schemeFor(AppThemeStyle style) {
    switch (style) {
      case AppThemeStyle.aurora:
        return _aurora;
      case AppThemeStyle.ember:
        return _ember;
      case AppThemeStyle.ocean:
        return _ocean;
    }
  }
}

class AppTheme {
  static ThemeData buildTheme(AppThemeStyle style) {
    AppColors.setTheme(style);
    switch (style) {
      case AppThemeStyle.aurora:
        return AuroraTheme.buildTheme();
      case AppThemeStyle.ember:
        return EmberTheme.buildTheme();
      case AppThemeStyle.ocean:
        return OceanTheme.buildTheme();
    }
  }
}
