import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/logout_dialog.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class AppShell extends ConsumerStatefulWidget {
  final Widget child;
  const AppShell({super.key, required this.child});

  @override
  ConsumerState<AppShell> createState() => _AppShellState();
}

class _AppShellState extends ConsumerState<AppShell> {
  bool _isCompact = false;
  int? _hoveredNavIndex;

  static final _navItems = [
    _NavItem(Icons.dashboard_rounded, 'nav.dashboard', '/dashboard'),
    _NavItem(Icons.people_rounded, 'nav.patients', '/patients'),
    _NavItem(Icons.mic_rounded, 'nav.recording', '/recording'),
    _NavItem(Icons.edit_note_rounded, 'nav.manual_note', '/manual-note'),
    _NavItem(Icons.quiz_rounded, 'nav.templates', '/question-templates'),
    _NavItem(Icons.calendar_month_rounded, 'nav.appointments', '/appointments'),
    _NavItem(Icons.search_rounded, 'nav.search', '/search'),
    _NavItem(Icons.settings_rounded, 'nav.settings', '/settings'),
    _NavItem(Icons.help_outline_rounded, 'nav.help', '/help'),
    _NavItem(Icons.admin_panel_settings_rounded, 'nav.admin', '/admin'),
  ];

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(currentUserProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final location = GoRouterState.of(context).matchedLocation;
    final selectedIndex = _getSelectedIndex(location);
    final width = MediaQuery.of(context).size.width;
    final compact = width < 768 || _isCompact;

    return Scaffold(
      body: Row(
        children: [
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeInOut,
            width: compact ? 72 : 220,
            decoration: ext.sidebarDecoration,
            child: Column(
              children: [
                const SizedBox(height: 20),
                _buildUserAvatar(user, compact, ext),
                const SizedBox(height: 24),
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    itemCount: _navItems.length,
                    itemBuilder: (context, i) => _buildNavItem(
                      _navItems[i],
                      index: i,
                      isSelected: i == selectedIndex,
                      compact: compact,
                      ext: ext,
                      onTap: () => context.go(_navItems[i].route),
                    ),
                  ),
                ),
                _buildBottomSection(compact, ext),
                const SizedBox(height: 16),
              ],
            ),
          ),
          Expanded(child: SelectionArea(child: widget.child)),
        ],
      ),
    );
  }

  Widget _buildUserAvatar(dynamic user, bool compact, MedScribeThemeExtension ext) {
    final hasAvatar = user?.avatarUrl != null;
    final name = user?.name ?? '';
    final initials = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Column(
        children: [
          Container(
            width: compact ? 44 : 52,
            height: compact ? 44 : 52,
            padding: const EdgeInsets.all(2),
            decoration: ext.avatarRingDecoration,
            child: Container(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: [AppColors.primary, AppColors.primaryLight],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: hasAvatar
                  ? ClipOval(
                      child: Image.network(
                        user!.avatarUrl!,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Center(
                          child: Text(
                            initials,
                            style: GoogleFonts.heebo(
                              fontSize: compact ? 16 : 18,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    )
                  : Center(
                      child: Text(
                        initials,
                        style: GoogleFonts.heebo(
                          fontSize: compact ? 16 : 18,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
            ),
          ),
          if (!compact) ...[
            const SizedBox(height: 10),
            Text(
              name,
              style: GoogleFonts.heebo(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              user?.role ?? '',
              style: GoogleFonts.heebo(
                fontSize: 11,
                color: AppColors.textMuted,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildNavItem(
    _NavItem item, {
    required int index,
    required bool isSelected,
    required bool compact,
    required MedScribeThemeExtension ext,
    required VoidCallback onTap,
  }) {
    final isHovered = _hoveredNavIndex == index;
    final iconColor = isSelected
        ? ext.selectedNavIconColor
        : isHovered
            ? AppColors.textSecondary
            : AppColors.textMuted;
    final textColor = isSelected ? ext.selectedNavTextColor : AppColors.textSecondary;

    Widget navContent = AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 0 : 14,
        vertical: 12,
      ),
      decoration: isSelected ? ext.selectedNavDecoration : null,
      child: Row(
        mainAxisAlignment: compact ? MainAxisAlignment.center : MainAxisAlignment.start,
        children: [
          Icon(item.icon, size: 22, color: iconColor),
          if (!compact) ...[
            const SizedBox(width: 12),
            Text(
              item.label.tr(),
              style: GoogleFonts.heebo(
                fontSize: 13,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                color: textColor,
              ),
            ),
          ],
        ],
      ),
    );

    if (compact) {
      navContent = Tooltip(
        message: item.label.tr(),
        waitDuration: const Duration(milliseconds: 400),
        child: navContent,
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: MouseRegion(
        onEnter: (_) => setState(() => _hoveredNavIndex = index),
        onExit: (_) => setState(() => _hoveredNavIndex = null),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(ext.navItemRadius),
            child: navContent,
          ),
        ),
      ),
    );
  }

  Widget _buildBottomSection(bool compact, MedScribeThemeExtension ext) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Column(
        children: [
          Divider(color: ext.dividerColor, height: 1),
          const SizedBox(height: 8),
          if (!compact)
            _buildActionButton(
              icon: _isCompact ? Icons.chevron_left_rounded : Icons.chevron_right_rounded,
              label: 'nav.collapse'.tr(),
              onTap: () => setState(() => _isCompact = !_isCompact),
              compact: compact,
            ),
          _buildActionButton(
            icon: Icons.logout_rounded,
            label: compact ? '' : 'nav.logout'.tr(),
            onTap: () => showLogoutDialog(context, ref),
            compact: compact,
            isDestructive: true,
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    bool compact = false,
    bool isDestructive = false,
  }) {
    final color = isDestructive ? AppColors.accent : AppColors.textMuted;
    final tooltipLabel = isDestructive ? 'nav.logout'.tr() : label;

    Widget content = Padding(
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 0 : 14,
        vertical: 10,
      ),
      child: Row(
        mainAxisAlignment: compact ? MainAxisAlignment.center : MainAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: color),
          if (!compact && label.isNotEmpty) ...[
            const SizedBox(width: 12),
            Text(
              label,
              style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w400, color: color),
            ),
          ],
        ],
      ),
    );

    if (compact && tooltipLabel.isNotEmpty) {
      content = Tooltip(message: tooltipLabel, child: content);
    }

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: content,
      ),
    );
  }

  int _getSelectedIndex(String location) {
    for (int i = 0; i < _navItems.length; i++) {
      if (location.startsWith(_navItems[i].route)) return i;
    }
    return 0;
  }
}

class _NavItem {
  final IconData icon;
  final String label;
  final String route;
  const _NavItem(this.icon, this.label, this.route);
}
