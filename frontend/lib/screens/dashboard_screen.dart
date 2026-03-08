import 'dart:async';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:medscribe_ai/providers/dashboard_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/widgets/dashboard/stat_cards.dart';

import 'package:medscribe_ai/widgets/dashboard/visits_chart.dart';
import 'package:medscribe_ai/widgets/treatment_timer.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stats = ref.watch(dashboardProvider);
    return Scaffold(
      backgroundColor: AppColors.background,
      body: stats.isLoading
          ? Center(child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5))
          : Padding(
              padding: const EdgeInsets.all(24),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                _buildHeader(),
                const SizedBox(height: 24),
                StatsGrid(stats: stats),
                const SizedBox(height: 20),
                Expanded(
                  child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    const Expanded(flex: 3, child: TreatmentTimer()),
                    const SizedBox(width: 20),
                    Expanded(flex: 7, child: VisitsChart(stats: stats)),
                  ]),
                ),
              ]),
            ),
    );
  }

  Widget _buildHeader() {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('dashboard.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
      const SizedBox(height: 4),
      const _DateTimeText(),
    ]);
  }
}

class _DateTimeText extends StatefulWidget {
  const _DateTimeText();

  @override
  State<_DateTimeText> createState() => _DateTimeTextState();
}

class _DateTimeTextState extends State<_DateTimeText> {
  late Timer _timer;
  DateTime _now = DateTime.now();

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) setState(() => _now = DateTime.now());
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final locale = context.locale.toString();
    final dateStr = DateFormat('EEEE, d MMMM yyyy', locale).format(_now);
    final timeStr = DateFormat('HH:mm', locale).format(_now);

    return Text('$dateStr  •  $timeStr', style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary));
  }
}
