import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/models/dashboard_models.dart';
import 'package:medscribe_ai/providers/dashboard_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class VisitsChart extends StatefulWidget {
  final DashboardState stats;

  const VisitsChart({super.key, required this.stats});

  @override
  State<VisitsChart> createState() => _VisitsChartState();
}

class _VisitsChartState extends State<VisitsChart> {
  int? _hoveredBarIndex;

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final days = widget.stats.visitsByDay;
    final maxCount = days.isEmpty ? 1 : days.map((d) => d.count).reduce((a, b) => a > b ? a : b).clamp(1, 999);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('dashboard.weekly_visits_chart'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 20),
        days.isEmpty
            ? Expanded(child: Center(child: Text('dashboard.no_data'.tr())))
            : Expanded(child: _buildChart(days, maxCount, ext)),
      ]),
    );
  }

  Widget _buildChart(List<ChartDay> days, int maxCount, MedScribeThemeExtension ext) {
    return LayoutBuilder(builder: (context, constraints) {
      final barWidth = ((constraints.maxWidth - 6 * 10) / 7).clamp(40.0, 120.0);
      return Column(
        children: [
          SizedBox(
            height: 200,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(days.length, (i) => _buildBar(days[i], i, maxCount, barWidth, ext)),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(days.length, (i) => _buildDayLabel(days[i], i, barWidth)),
            ),
          ),
        ],
      );
    });
  }

  Widget _buildBar(ChartDay day, int index, int maxCount, double barWidth, MedScribeThemeExtension ext) {
    final ratio = day.count / maxCount;
    final barHeight = (ratio * 150).clamp(8.0, 150.0);
    final isHovered = _hoveredBarIndex == index;
    final dayName = day.dayName.isNotEmpty ? day.dayName : _dayLabel(day.date);

    return MouseRegion(
      onEnter: (_) => setState(() => _hoveredBarIndex = index),
      onExit: (_) => setState(() => _hoveredBarIndex = null),
      child: Tooltip(
        message: '$dayName - ${day.count} ${'dashboard.visits'.tr()}',
        child: SizedBox(
          width: barWidth,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('${day.count}', style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w700, color: isHovered ? AppColors.primary : AppColors.textSecondary)),
              const SizedBox(height: 6),
              AnimatedContainer(duration: const Duration(milliseconds: 200), height: barHeight, width: barWidth * 0.7, decoration: ext.chartBarDecoration(isHovered)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDayLabel(ChartDay day, int index, double barWidth) {
    final isHovered = _hoveredBarIndex == index;
    final dayName = day.dayName.isNotEmpty ? day.dayName : _dayLabel(day.date);

    return Expanded(
      child: Column(
        children: [
          Text(dayName, style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: isHovered ? AppColors.primary : AppColors.textSecondary)),
          if (day.patients.isNotEmpty) ...[
            const SizedBox(height: 4),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: day.patients.map<Widget>((patient) => Padding(
                    padding: const EdgeInsets.only(bottom: 2),
                    child: GestureDetector(
                      onTap: patient.patientDisplayId != null ? () => context.push('/patients/${patient.patientDisplayId}') : null,
                      child: Text(
                        patient.name,
                        style: GoogleFonts.heebo(fontSize: 10, fontWeight: FontWeight.w600, color: AppColors.primary, decoration: TextDecoration.underline, decorationColor: AppColors.primary.withValues(alpha: 0.3)),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.center,
                      ),
                    ),
                  )).toList(),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _dayLabel(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final days = [
        'date.day_a'.tr(),
        'date.day_b'.tr(),
        'date.day_c'.tr(),
        'date.day_d'.tr(),
        'date.day_e'.tr(),
        'date.day_f'.tr(),
        'date.day_s'.tr()
      ];
      return days[date.weekday % 7];
    } catch (_) {
      return '';
    }
  }
}
