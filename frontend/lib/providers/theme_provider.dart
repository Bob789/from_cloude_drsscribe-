import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:medscribe_ai/utils/app_theme.dart';

class ThemeNotifier extends StateNotifier<AppThemeStyle> {
  ThemeNotifier() : super(AppThemeStyle.aurora) {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('app_theme_style');
    if (saved != null) {
      for (final style in AppThemeStyle.values) {
        if (style.name == saved) {
          state = style;
          AppColors.setTheme(style);
          return;
        }
      }
    }
  }

  Future<void> setTheme(AppThemeStyle style) async {
    state = style;
    AppColors.setTheme(style);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('app_theme_style', style.name);
  }
}

final themeProvider = StateNotifierProvider<ThemeNotifier, AppThemeStyle>((ref) {
  return ThemeNotifier();
});
