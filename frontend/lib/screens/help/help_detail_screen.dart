import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class HelpDetailScreen extends StatelessWidget {
  final String category;
  const HelpDetailScreen({super.key, required this.category});

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final content = _helpContent[category];

    if (content == null) {
      return Scaffold(
        backgroundColor: AppColors.background,
        body: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
          Text('help.category_not_found'.tr(), style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          const SizedBox(height: 16),
          GestureDetector(
            onTap: () => context.go('/help'),
            child: Text('help.back_to_help'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.primary)),
          ),
        ])),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _buildBackLink(context),
              const SizedBox(height: 20),
              _buildHeader(content, ext),
              const SizedBox(height: 20),
              _buildOverview(content, ext),
              const SizedBox(height: 16),
              _buildSteps(content, ext),
              const SizedBox(height: 16),
              _buildTips(content, ext),
              const SizedBox(height: 24),
            ]),
          ),
        ),
      ),
    );
  }

  Widget _buildBackLink(BuildContext context) {
    return GestureDetector(
      onTap: () => context.go('/help'),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Icon(Icons.arrow_forward_rounded, size: 16, color: AppColors.primary),
        const SizedBox(width: 6),
        Text('help.back_to_help'.tr(), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.primary)),
      ]),
    );
  }

  Widget _buildHeader(_HelpContent content, MedScribeThemeExtension ext) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Row(children: [
        Container(
          width: 56, height: 56,
          decoration: ext.iconContainer(content.color),
          child: Icon(content.icon, size: 28, color: content.color),
        ),
        const SizedBox(width: 16),
        Text(content.title, style: GoogleFonts.heebo(fontSize: 24, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
      ]),
    );
  }

  Widget _buildOverview(_HelpContent content, MedScribeThemeExtension ext) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('help.overview'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 12),
        Text(content.overview, style: GoogleFonts.heebo(fontSize: 14, height: 1.7, color: AppColors.textSecondary)),
      ]),
    );
  }

  Widget _buildSteps(_HelpContent content, MedScribeThemeExtension ext) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('help.step_guide'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(height: 16),
        ...content.steps.asMap().entries.map((e) => _buildStep(e.key + 1, e.value, content.color, ext)),
      ]),
    );
  }

  Widget _buildStep(int num, _HelpStep step, Color color, MedScribeThemeExtension ext) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Container(
          width: 28, height: 28,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(colors: [color, color.withValues(alpha: 0.6)], begin: Alignment.topLeft, end: Alignment.bottomRight),
          ),
          child: Center(child: Text('$num', style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white))),
        ),
        const SizedBox(width: 12),
        Icon(step.icon, size: 20, color: AppColors.textMuted),
        const SizedBox(width: 10),
        Expanded(child: Padding(
          padding: const EdgeInsets.only(top: 3),
          child: Text(step.text, style: GoogleFonts.heebo(fontSize: 13.5, height: 1.5, color: AppColors.textSecondary)),
        )),
      ]),
    );
  }

  Widget _buildTips(_HelpContent content, MedScribeThemeExtension ext) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: ext.success.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(ext.cardRadius),
        border: Border.all(color: ext.success.withValues(alpha: 0.15)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(Icons.lightbulb_rounded, size: 20, color: ext.success),
          const SizedBox(width: 8),
          Text('help.tips'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        ]),
        const SizedBox(height: 12),
        ...content.tips.map((tip) => Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Padding(padding: const EdgeInsets.only(top: 2), child: Icon(Icons.check_circle_rounded, size: 16, color: ext.success)),
            const SizedBox(width: 10),
            Expanded(child: Text(tip, style: GoogleFonts.heebo(fontSize: 13.5, height: 1.5, color: AppColors.textSecondary))),
          ]),
        )),
      ]),
    );
  }

  static final _helpContent = <String, _HelpContent>{
    'dashboard': _HelpContent(
      title: 'help.cat_dashboard_title'.tr(),
      icon: Icons.dashboard_rounded,
      color: const Color(0xFF00F0FF),
      overview: 'help.cat_dashboard_overview'.tr(),
      steps: [
        _HelpStep(Icons.login_rounded, 'help.cat_dashboard_step1'.tr()),
        _HelpStep(Icons.analytics_rounded, 'help.cat_dashboard_step2'.tr()),
        _HelpStep(Icons.bar_chart_rounded, 'help.cat_dashboard_step3'.tr()),
        _HelpStep(Icons.timer_rounded, 'help.cat_dashboard_step4'.tr()),
        _HelpStep(Icons.touch_app_rounded, 'help.cat_dashboard_step5'.tr()),
      ],
      tips: [
        'help.cat_dashboard_tip1'.tr(),
        'help.cat_dashboard_tip2'.tr(),
        'help.cat_dashboard_tip3'.tr(),
      ],
    ),
    'patients': _HelpContent(
      title: 'help.cat_patients_title'.tr(),
      icon: Icons.people_rounded,
      color: const Color(0xFFBF5AF2),
      overview: 'help.cat_patients_overview'.tr(),
      steps: [
        _HelpStep(Icons.people_rounded, 'help.cat_patients_step1'.tr()),
        _HelpStep(Icons.person_add_rounded, 'help.cat_patients_step2'.tr()),
        _HelpStep(Icons.search_rounded, 'help.cat_patients_step3'.tr()),
        _HelpStep(Icons.folder_open_rounded, 'help.cat_patients_step4'.tr()),
        _HelpStep(Icons.edit_rounded, 'help.cat_patients_step5'.tr()),
      ],
      tips: [
        'help.cat_patients_tip1'.tr(),
        'help.cat_patients_tip2'.tr(),
        'help.cat_patients_tip3'.tr(),
      ],
    ),
    'recording': _HelpContent(
      title: 'help.cat_recording_title'.tr(),
      icon: Icons.mic_rounded,
      color: const Color(0xFFFF375F),
      overview: 'help.cat_recording_overview'.tr(),
      steps: [
        _HelpStep(Icons.mic_rounded, 'help.cat_recording_step1'.tr()),
        _HelpStep(Icons.person_search_rounded, 'help.cat_recording_step2'.tr()),
        _HelpStep(Icons.fiber_manual_record_rounded, 'help.cat_recording_step3'.tr()),
        _HelpStep(Icons.record_voice_over_rounded, 'help.cat_recording_step4'.tr()),
        _HelpStep(Icons.stop_circle_rounded, 'help.cat_recording_step5'.tr()),
        _HelpStep(Icons.auto_awesome_rounded, 'help.cat_recording_step6'.tr()),
      ],
      tips: [
        'help.cat_recording_tip1'.tr(),
        'help.cat_recording_tip2'.tr(),
        'help.cat_recording_tip3'.tr(),
        'help.cat_recording_tip4'.tr(),
      ],
    ),
    'summary': _HelpContent(
      title: 'help.cat_summary_title'.tr(),
      icon: Icons.description_rounded,
      color: const Color(0xFF30D158),
      overview: 'help.cat_summary_overview'.tr(),
      steps: [
        _HelpStep(Icons.auto_awesome_rounded, 'help.cat_summary_step1'.tr()),
        _HelpStep(Icons.checklist_rounded, 'help.cat_summary_step2'.tr()),
        _HelpStep(Icons.flag_rounded, 'help.cat_summary_step3'.tr()),
        _HelpStep(Icons.edit_rounded, 'help.cat_summary_step4'.tr()),
        _HelpStep(Icons.save_rounded, 'help.cat_summary_step5'.tr()),
      ],
      tips: [
        'help.cat_summary_tip1'.tr(),
        'help.cat_summary_tip2'.tr(),
        'help.cat_summary_tip3'.tr(),
      ],
    ),
    'search': _HelpContent(
      title: 'help.cat_search_title'.tr(),
      icon: Icons.search_rounded,
      color: const Color(0xFFF5A623),
      overview: 'help.cat_search_overview'.tr(),
      steps: [
        _HelpStep(Icons.search_rounded, 'help.cat_search_step1'.tr()),
        _HelpStep(Icons.keyboard_rounded, 'help.cat_search_step2'.tr()),
        _HelpStep(Icons.label_rounded, 'help.cat_search_step3'.tr()),
        _HelpStep(Icons.date_range_rounded, 'help.cat_search_step4'.tr()),
        _HelpStep(Icons.open_in_new_rounded, 'help.cat_search_step5'.tr()),
      ],
      tips: [
        'help.cat_search_tip1'.tr(),
        'help.cat_search_tip2'.tr(),
        'help.cat_search_tip3'.tr(),
      ],
    ),
    'editing': _HelpContent(
      title: 'help.cat_editing_title'.tr(),
      icon: Icons.edit_note_rounded,
      color: const Color(0xFF14B8A6),
      overview: 'help.cat_editing_overview'.tr(),
      steps: [
        _HelpStep(Icons.open_in_new_rounded, 'help.cat_editing_step1'.tr()),
        _HelpStep(Icons.edit_rounded, 'help.cat_editing_step2'.tr()),
        _HelpStep(Icons.text_fields_rounded, 'help.cat_editing_step3'.tr()),
        _HelpStep(Icons.save_rounded, 'help.cat_editing_step4'.tr()),
        _HelpStep(Icons.history_rounded, 'help.cat_editing_step5'.tr()),
      ],
      tips: [
        'help.cat_editing_tip1'.tr(),
        'help.cat_editing_tip2'.tr(),
        'help.cat_editing_tip3'.tr(),
      ],
    ),
    'settings': _HelpContent(
      title: 'help.cat_settings_title'.tr(),
      icon: Icons.settings_rounded,
      color: const Color(0xFF60A5FA),
      overview: 'help.cat_settings_overview'.tr(),
      steps: [
        _HelpStep(Icons.settings_rounded, 'help.cat_settings_step1'.tr()),
        _HelpStep(Icons.person_rounded, 'help.cat_settings_step2'.tr()),
        _HelpStep(Icons.palette_rounded, 'help.cat_settings_step3'.tr()),
        _HelpStep(Icons.tune_rounded, 'help.cat_settings_step4'.tr()),
        _HelpStep(Icons.refresh_rounded, 'help.cat_settings_step5'.tr()),
      ],
      tips: [
        'help.cat_settings_tip1'.tr(),
        'help.cat_settings_tip2'.tr(),
        'help.cat_settings_tip3'.tr(),
      ],
    ),
    'admin': _HelpContent(
      title: 'help.cat_admin_title'.tr(),
      icon: Icons.admin_panel_settings_rounded,
      color: const Color(0xFFE8735A),
      overview: 'help.cat_admin_overview'.tr(),
      steps: [
        _HelpStep(Icons.admin_panel_settings_rounded, 'help.cat_admin_step1'.tr()),
        _HelpStep(Icons.manage_accounts_rounded, 'help.cat_admin_step2'.tr()),
        _HelpStep(Icons.security_rounded, 'help.cat_admin_step3'.tr()),
        _HelpStep(Icons.show_chart_rounded, 'help.cat_admin_step4'.tr()),
        _HelpStep(Icons.assessment_rounded, 'help.cat_admin_step5'.tr()),
      ],
      tips: [
        'help.cat_admin_tip1'.tr(),
        'help.cat_admin_tip2'.tr(),
        'help.cat_admin_tip3'.tr(),
      ],
    ),
  };
}

class _HelpContent {
  final String title;
  final IconData icon;
  final Color color;
  final String overview;
  final List<_HelpStep> steps;
  final List<String> tips;
  const _HelpContent({required this.title, required this.icon, required this.color, required this.overview, required this.steps, required this.tips});
}

class _HelpStep {
  final IconData icon;
  final String text;
  const _HelpStep(this.icon, this.text);
}
