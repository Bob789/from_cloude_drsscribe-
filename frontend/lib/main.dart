import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/flutter_web_plugins.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/providers/theme_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/router.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'dart:html' as html;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EasyLocalization.ensureInitialized();
  usePathUrlStrategy();

  runApp(
    EasyLocalization(
      supportedLocales: const [
        Locale('he'),
        Locale('en'),
        Locale('de'),
        Locale('es'),
        Locale('fr'),
        Locale('pt'),
        Locale('ko'),
        Locale('it'),
      ],
      path: 'assets/translations',
      saveLocale: true,
      fallbackLocale: const Locale('he'),
      child: const ProviderScope(child: MedScribeApp()),
    ),
  );
}

class MedScribeApp extends ConsumerStatefulWidget {
  const MedScribeApp({super.key});

  @override
  ConsumerState<MedScribeApp> createState() => _MedScribeAppState();
}

class _MedScribeAppState extends ConsumerState<MedScribeApp> {
  bool _geoChecked = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_geoChecked) {
      _geoChecked = true;
      _detectGeoLocale();
    }
  }

  Future<void> _detectGeoLocale() async {
    // Only detect on first ever visit (no saved locale in localStorage)
    final hasStoredLocale = html.window.localStorage.containsKey('locale');
    if (hasStoredLocale) return;

    try {
      final dio = ApiClient().dio;
      final res = await dio.get('/geo-locale');
      final locale = res.data['locale'] as String? ?? 'he';
      final supportedCodes = ['he', 'en', 'de', 'es', 'fr', 'pt', 'ko', 'it'];
      if (supportedCodes.contains(locale) && mounted) {
        await context.setLocale(Locale(locale));
        html.window.localStorage['locale'] = locale;
      }
    } catch (_) {
      // Silently fail — fallback locale (he) will be used
    }
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(routerProvider);
    final themeStyle = ref.watch(themeProvider);
    final theme = AppTheme.buildTheme(themeStyle);
    final isRtl = context.locale.languageCode == 'he';

    return MaterialApp.router(
      title: 'Doctor Scribe AI',
      debugShowCheckedModeBanner: false,
      theme: theme,
      darkTheme: theme,
      themeMode: ThemeMode.dark,
      routerConfig: router,
      locale: context.locale,
      supportedLocales: context.supportedLocales,
      localizationsDelegates: [
        ...context.localizationDelegates,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      builder: (context, child) {
        return Directionality(
          textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
          child: child!,
        );
      },
    );
  }
}
