import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/providers/dashboard_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class StatData {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final String? route;
  const StatData(this.title, this.value, this.icon, this.color, {this.route});
}

class StatsGrid extends StatelessWidget {
  final DashboardState stats;

  const StatsGrid({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final items = [
      StatData('dashboard.visits_today'.tr(), '${stats.todayVisits}', Icons.calendar_today_rounded, AppColors.primary, route: '/appointments'),
      StatData('dashboard.pending_transcriptions'.tr(), '${stats.pendingTranscriptions}', Icons.pending_rounded, AppColors.warning),
      StatData('dashboard.total_patients'.tr(), '${stats.totalPatients}', Icons.people_rounded, AppColors.secondary, route: '/patients'),
      StatData('dashboard.weekly_visits'.tr(), '${stats.visitsThisWeek}', Icons.trending_up_rounded, AppColors.success),
      StatData('dashboard.monthly_transcriptions'.tr(), '${stats.monthlyTranscriptions}', Icons.mic_rounded, const Color(0xFF14B8A6)),
    ];
    return LayoutBuilder(builder: (context, constraints) {
      if (constraints.maxWidth < 500) {
        // Narrow: use Wrap instead of Row
        return Wrap(
          spacing: 10,
          runSpacing: 10,
          children: items.map((item) => SizedBox(
            width: (constraints.maxWidth - 10) / 2,
            child: _buildCompactCard(context, item, ext),
          )).toList(),
        );
      }
      final children = <Widget>[];
      for (var i = 0; i < items.length; i++) {
        if (i > 0) children.add(const SizedBox(width: 12));
        children.add(Expanded(child: _buildCompactCard(context, items[i], ext)));
      }
      return Row(children: children);
    });
  }

  Widget _buildCompactCard(BuildContext context, StatData data, MedScribeThemeExtension ext) {
    final card = Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 14),
      decoration: ext.statCardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
        Row(children: [
          Container(
            width: 36, height: 36,
            decoration: ext.iconContainer(data.color),
            child: Icon(data.icon, color: data.color, size: 18),
          ),
          const Spacer(),
          Text(data.value, style: GoogleFonts.heebo(fontSize: 28, fontWeight: FontWeight.w900, color: AppColors.textPrimary, height: 1.0)),
        ]),
        const SizedBox(height: 8),
        Text(data.title, style: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w500, color: AppColors.textMuted), maxLines: 1, overflow: TextOverflow.ellipsis),
      ]),
    );

    if (data.route != null) {
      return MouseRegion(
        cursor: SystemMouseCursors.click,
        child: GestureDetector(onTap: () => context.go(data.route!), child: card),
      );
    }
    return card;
  }
}
