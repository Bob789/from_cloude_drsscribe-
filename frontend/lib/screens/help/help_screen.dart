import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  static final _categories = [
    _HelpCategory('dashboard', 'help.cat_dashboard_title'.tr(), 'help.cat_dashboard_desc'.tr(), Icons.dashboard_rounded, const Color(0xFF00F0FF)),
    _HelpCategory('patients', 'help.cat_patients_title'.tr(), 'help.cat_patients_desc'.tr(), Icons.people_rounded, const Color(0xFFBF5AF2)),
    _HelpCategory('recording', 'help.cat_recording_title'.tr(), 'help.cat_recording_desc'.tr(), Icons.mic_rounded, const Color(0xFFFF375F)),
    _HelpCategory('summary', 'help.cat_summary_title'.tr(), 'help.cat_summary_desc'.tr(), Icons.description_rounded, const Color(0xFF30D158)),
    _HelpCategory('search', 'help.cat_search_title'.tr(), 'help.cat_search_desc'.tr(), Icons.search_rounded, const Color(0xFFF5A623)),
    _HelpCategory('editing', 'help.cat_editing_title'.tr(), 'help.cat_editing_desc'.tr(), Icons.edit_note_rounded, const Color(0xFF14B8A6)),
    _HelpCategory('settings', 'help.cat_settings_title'.tr(), 'help.cat_settings_desc'.tr(), Icons.settings_rounded, const Color(0xFF60A5FA)),
    _HelpCategory('admin', 'help.cat_admin_title'.tr(), 'help.cat_admin_desc'.tr(), Icons.admin_panel_settings_rounded, const Color(0xFFE8735A)),
  ];

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('help.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
          const SizedBox(height: 4),
          Text('help.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
          const SizedBox(height: 24),
          LayoutBuilder(builder: (context, constraints) {
            final cols = constraints.maxWidth >= 1200 ? 4 : constraints.maxWidth >= 800 ? 3 : constraints.maxWidth >= 500 ? 2 : 1;
            return GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: cols, crossAxisSpacing: 16, mainAxisSpacing: 16, childAspectRatio: 1.4),
              itemCount: _categories.length,
              itemBuilder: (context, i) => _buildCard(_categories[i], ext, context),
            );
          }),
        ]),
      ),
    );
  }

  Widget _buildCard(_HelpCategory cat, MedScribeThemeExtension ext, BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => context.go('/help/${cat.id}'),
        borderRadius: BorderRadius.circular(ext.cardRadius),
        child: Container(
          padding: const EdgeInsets.all(18),
          decoration: ext.cardDecoration,
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Container(
              width: 44, height: 44,
              decoration: ext.iconContainer(cat.color),
              child: Icon(cat.icon, size: 22, color: cat.color),
            ),
            const SizedBox(height: 12),
            Text(cat.title, style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
            const SizedBox(height: 4),
            Expanded(
              child: Text(cat.subtitle, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted), maxLines: 2, overflow: TextOverflow.ellipsis),
            ),
            Row(children: [
              Text('help.more_info'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primary)),
              const SizedBox(width: 4),
              Icon(Icons.arrow_back_rounded, size: 14, color: AppColors.primary),
            ]),
          ]),
        ),
      ),
    );
  }
}

class _HelpCategory {
  final String id;
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  const _HelpCategory(this.id, this.title, this.subtitle, this.icon, this.color);
}
