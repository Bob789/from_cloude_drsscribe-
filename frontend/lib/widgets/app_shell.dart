import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/logout_dialog.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';

class AppShell extends ConsumerStatefulWidget {
  final Widget child;
  const AppShell({super.key, required this.child});

  @override
  ConsumerState<AppShell> createState() => _AppShellState();
}

class _AppShellState extends ConsumerState<AppShell> {
  bool _isCompact = false;
  int? _hoveredNavIndex;
  int _unreadCount = 0;

  @override
  void initState() {
    super.initState();
    _fetchUnreadCount();
  }

  Future<void> _fetchUnreadCount() async {
    try {
      final dio = ApiClient().dio;
      final res = await dio.get('/messages/unread-count');
      if (mounted) {
        setState(() => _unreadCount = res.data['unread'] ?? 0);
      }
    } catch (_) {}
  }

  Widget _buildInitials(String initials, bool compact) {
    return Center(
      child: Text(
        initials,
        style: GoogleFonts.heebo(
          fontSize: compact ? 16 : 18,
          fontWeight: FontWeight.w700,
          color: Colors.white,
        ),
      ),
    );
  }

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

  Widget _buildUserAvatar(
    dynamic user,
    bool compact,
    MedScribeThemeExtension ext,
  ) {
    final hasAvatar = user?.avatarUrl != null;
    final name = user?.name ?? '';
    final initials = name.isNotEmpty ? name[0].toUpperCase() : '?';

    final avatarWidget = Container(
      width: compact ? 44 : 48,
      height: compact ? 44 : 48,
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
                  errorBuilder: (_, __, ___) =>
                      _buildInitials(initials, compact),
                ),
              )
            : _buildInitials(initials, compact),
      ),
    );

    if (compact) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Column(
          children: [
            avatarWidget,
            const SizedBox(height: 6),
            InkWell(
              onTap: () => _showMessagesPanel(context, user),
              borderRadius: BorderRadius.circular(20),
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  Icon(
                    Icons.mail_outline_rounded,
                    size: 20,
                    color: AppColors.textMuted,
                  ),
                  if (_unreadCount > 0)
                    Positioned(
                      top: -6,
                      right: -8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 4,
                          vertical: 1,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEF4444),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 16,
                          minHeight: 16,
                        ),
                        child: Center(
                          child: Text(
                            _unreadCount > 99 ? '99+' : '$_unreadCount',
                            style: GoogleFonts.heebo(
                              fontSize: 9,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.04),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
        ),
        child: Row(
          children: [
            avatarWidget,
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
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
              ),
            ),
            InkWell(
              onTap: () => _showMessagesPanel(context, user),
              borderRadius: BorderRadius.circular(20),
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      Icons.mail_outline_rounded,
                      size: 22,
                      color: AppColors.primary,
                    ),
                  ),
                  if (_unreadCount > 0)
                    Positioned(
                      top: -4,
                      right: -4,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 5,
                          vertical: 1,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEF4444),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: const Color(0xFF141828),
                            width: 1.5,
                          ),
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 18,
                          minHeight: 18,
                        ),
                        child: Center(
                          child: Text(
                            _unreadCount > 99 ? '99+' : '$_unreadCount',
                            style: GoogleFonts.heebo(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showMessagesPanel(BuildContext context, dynamic user) {
    showDialog(
      context: context,
      builder: (ctx) => _MessagesDialog(user: user),
    ).then((_) => _fetchUnreadCount());
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
    final textColor =
        isSelected ? ext.selectedNavTextColor : AppColors.textSecondary;

    Widget navContent = AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: EdgeInsets.symmetric(horizontal: compact ? 0 : 14, vertical: 12),
      decoration: isSelected ? ext.selectedNavDecoration : null,
      child: Row(
        mainAxisAlignment:
            compact ? MainAxisAlignment.center : MainAxisAlignment.start,
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
              icon: _isCompact
                  ? Icons.chevron_left_rounded
                  : Icons.chevron_right_rounded,
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
      padding: EdgeInsets.symmetric(horizontal: compact ? 0 : 14, vertical: 10),
      child: Row(
        mainAxisAlignment:
            compact ? MainAxisAlignment.center : MainAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: color),
          if (!compact && label.isNotEmpty) ...[
            const SizedBox(width: 12),
            Text(
              label,
              style: GoogleFonts.heebo(
                fontSize: 12,
                fontWeight: FontWeight.w400,
                color: color,
              ),
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

class _MessagesDialog extends StatefulWidget {
  final dynamic user;
  const _MessagesDialog({required this.user});

  @override
  State<_MessagesDialog> createState() => _MessagesDialogState();
}

class _MessagesDialogState extends State<_MessagesDialog> {
  final _subjectCtrl = TextEditingController();
  final _bodyCtrl = TextEditingController();
  final _replyCtrl = TextEditingController();
  String _category = 'general';
  List<dynamic> _threads = [];
  List<dynamic> _threadMessages = [];
  Map<String, dynamic>? _selectedThread;
  bool _loading = true;
  bool _sending = false;
  bool _showCompose = false;
  bool _threadLoading = false;
  List<Map<String, dynamic>> _attachments = [];
  bool _uploading = false;

  @override
  void initState() {
    super.initState();
    _loadThreads();
  }

  @override
  void dispose() {
    _subjectCtrl.dispose();
    _bodyCtrl.dispose();
    _replyCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadThreads() async {
    try {
      final dio = ApiClient().dio;
      final res = await dio.get('/messages/threads');
      if (mounted)
        setState(() {
          _threads = res.data is List ? res.data : [];
          _loading = false;
        });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _openThread(Map<String, dynamic> thread) async {
    setState(() {
      _selectedThread = thread;
      _threadLoading = true;
      _showCompose = false;
      _replyCtrl.clear();
    });
    try {
      final dio = ApiClient().dio;
      final res = await dio.get('/messages/thread/${thread['thread_id']}');
      if (mounted)
        setState(() {
          _threadMessages = res.data is List ? res.data : [];
          _threadLoading = false;
        });
    } catch (_) {
      if (mounted) setState(() => _threadLoading = false);
    }
  }

  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: [
          'jpg',
          'jpeg',
          'png',
          'gif',
          'webp',
          'pdf',
          'doc',
          'docx',
          'xls',
          'xlsx',
          'csv',
          'txt',
          'rtf',
        ],
        withData: true,
      );
      if (result == null || result.files.isEmpty) return;
      final file = result.files.first;
      if (file.bytes == null) return;
      if (file.size > 10 * 1024 * 1024) {
        if (mounted)
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'קובץ גדול מדי — מקסימום 10MB',
                style: GoogleFonts.heebo(),
              ),
              backgroundColor: Colors.orange.shade700,
            ),
          );
        return;
      }
      setState(() => _uploading = true);
      final dio = ApiClient().dio;
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(file.bytes!, filename: file.name),
      });
      final res = await dio.post('/messages/upload-attachment', data: formData);
      if (mounted && res.data != null) {
        setState(() {
          _attachments.add({
            'key': res.data['key'],
            'name': res.data['name'],
            'url': res.data['url'],
            'size': res.data['size'],
          });
          _uploading = false;
        });
      }
    } on DioException catch (e) {
      setState(() => _uploading = false);
      final msg = e.response?.data?['message'] ?? 'שגיאה בהעלאת הקובץ';
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(msg, style: GoogleFonts.heebo()),
            backgroundColor: Colors.red.shade700,
          ),
        );
    } catch (_) {
      setState(() => _uploading = false);
    }
  }

  Future<void> _sendNewMessage() async {
    if (_subjectCtrl.text.trim().isEmpty || _bodyCtrl.text.trim().isEmpty)
      return;
    setState(() => _sending = true);
    try {
      final dio = ApiClient().dio;
      await dio.post(
        '/admin/messages',
        data: {
          'subject': _subjectCtrl.text.trim(),
          'body': _bodyCtrl.text.trim(),
          'category': _category,
          'attachments': _attachments,
        },
      );
      if (mounted) {
        _subjectCtrl.clear();
        _bodyCtrl.clear();
        setState(() {
          _category = 'general';
          _sending = false;
          _showCompose = false;
          _attachments = [];
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('ההודעה נשלחה בהצלחה', style: GoogleFonts.heebo()),
            backgroundColor: Colors.green.shade700,
          ),
        );
        _loadThreads();
      }
    } on DioException catch (_) {
      setState(() => _sending = false);
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('שגיאה בשליחת ההודעה', style: GoogleFonts.heebo()),
            backgroundColor: Colors.red.shade700,
          ),
        );
    }
  }

  Future<void> _sendReply() async {
    if (_replyCtrl.text.trim().isEmpty || _selectedThread == null) return;
    setState(() => _sending = true);
    try {
      final dio = ApiClient().dio;
      await dio.post(
        '/admin/messages',
        data: {
          'subject': 'תגובה: ${_selectedThread!['subject']}',
          'body': _replyCtrl.text.trim(),
          'category': _selectedThread!['category'] ?? 'general',
          'thread_id': _selectedThread!['thread_id'],
        },
      );
      if (mounted) {
        _replyCtrl.clear();
        setState(() => _sending = false);
        _openThread(_selectedThread!);
        _loadThreads();
      }
    } on DioException catch (_) {
      setState(() => _sending = false);
    }
  }

  InputDecoration _inputDeco(
    String label, {
    bool alignTop = false,
  }) =>
      InputDecoration(
        labelText: label,
        alignLabelWithHint: alignTop,
        labelStyle: GoogleFonts.heebo(color: Colors.white38, fontSize: 13),
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.04),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.08)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide:
              BorderSide(color: AppColors.primary.withValues(alpha: 0.5)),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      );

  @override
  Widget build(BuildContext context) {
    final screenW = MediaQuery.of(context).size.width;
    final dialogW = (screenW * 0.85).clamp(400.0, 800.0);
    final screenH = MediaQuery.of(context).size.height;
    final dialogH = (screenH * 0.8).clamp(450.0, 700.0);

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.all(20),
      child: Container(
        width: dialogW,
        height: dialogH,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF141828), Color(0xFF0E1220)],
          ),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.5),
              blurRadius: 40,
              spreadRadius: 4,
            ),
          ],
        ),
        child: Column(
          children: [
            // Header
            Container(
              padding: const EdgeInsets.fromLTRB(20, 16, 12, 12),
              decoration: BoxDecoration(
                border: Border(
                  bottom: BorderSide(
                    color: Colors.white.withValues(alpha: 0.06),
                  ),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          AppColors.primary.withValues(alpha: 0.2),
                          AppColors.primaryLight.withValues(alpha: 0.1),
                        ],
                      ),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Icon(
                      Icons.mail_rounded,
                      color: AppColors.primary,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'הודעות',
                          style: GoogleFonts.heebo(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          'צוות התמיכה · Doctor Scribe AI',
                          style: GoogleFonts.heebo(
                            fontSize: 12,
                            color: AppColors.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // New message button
                  IconButton(
                    onPressed: () => setState(() {
                      _showCompose = true;
                      _selectedThread = null;
                    }),
                    tooltip: 'הודעה חדשה',
                    icon: Icon(
                      Icons.edit_rounded,
                      color: AppColors.primary,
                      size: 20,
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(
                      Icons.close_rounded,
                      color: Colors.white38,
                      size: 22,
                    ),
                  ),
                ],
              ),
            ),
            // Body — two-panel layout
            Expanded(
              child: Row(
                children: [
                  // Thread list panel
                  Container(
                    width: dialogW * 0.38,
                    decoration: BoxDecoration(
                      border: Border(
                        left: BorderSide(
                          color: Colors.white.withValues(alpha: 0.06),
                        ),
                      ),
                    ),
                    child: _loading
                        ? const Center(child: CircularProgressIndicator())
                        : _threads.isEmpty
                            ? Center(
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      Icons.inbox_rounded,
                                      size: 40,
                                      color: AppColors.textMuted.withValues(
                                        alpha: 0.3,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      'אין שיחות',
                                      style: GoogleFonts.heebo(
                                        fontSize: 14,
                                        color: AppColors.textMuted,
                                      ),
                                    ),
                                  ],
                                ),
                              )
                            : ListView.builder(
                                itemCount: _threads.length,
                                itemBuilder: (ctx, i) {
                                  final t = _threads[i] as Map<String, dynamic>;
                                  final selected =
                                      _selectedThread?['thread_id'] ==
                                          t['thread_id'];
                                  final unread =
                                      (t['unread_count'] ?? 0) as int;
                                  return InkWell(
                                    onTap: () => _openThread(t),
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 14,
                                        vertical: 12,
                                      ),
                                      decoration: BoxDecoration(
                                        color: selected
                                            ? AppColors.primary.withValues(
                                                alpha: 0.08,
                                              )
                                            : Colors.transparent,
                                        border: Border(
                                          bottom: BorderSide(
                                            color: Colors.white.withValues(
                                              alpha: 0.04,
                                            ),
                                          ),
                                        ),
                                      ),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            children: [
                                              if (unread > 0) ...[
                                                Container(
                                                  width: 8,
                                                  height: 8,
                                                  decoration: BoxDecoration(
                                                    shape: BoxShape.circle,
                                                    color: AppColors.primary,
                                                  ),
                                                ),
                                                const SizedBox(width: 6),
                                              ],
                                              Expanded(
                                                child: Text(
                                                  t['subject'] ?? '',
                                                  style: GoogleFonts.heebo(
                                                    fontSize: 13,
                                                    fontWeight: unread > 0
                                                        ? FontWeight.w700
                                                        : FontWeight.w400,
                                                    color: Colors.white,
                                                  ),
                                                  maxLines: 1,
                                                  overflow:
                                                      TextOverflow.ellipsis,
                                                ),
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 2),
                                          Text(
                                            t['last_message']?['body']
                                                    ?.toString()
                                                    .replaceAll('\n', ' ') ??
                                                '',
                                            style: GoogleFonts.heebo(
                                              fontSize: 12,
                                              color: AppColors.textMuted,
                                            ),
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                          const SizedBox(height: 2),
                                          Row(
                                            children: [
                                              Text(
                                                t['last_activity']
                                                        ?.toString()
                                                        .substring(0, 10) ??
                                                    '',
                                                style: GoogleFonts.heebo(
                                                  fontSize: 10,
                                                  color: AppColors.textMuted,
                                                ),
                                              ),
                                              const Spacer(),
                                              if ((t['message_count'] ?? 0) > 1)
                                                Text(
                                                  '${t['message_count']}',
                                                  style: GoogleFonts.heebo(
                                                    fontSize: 10,
                                                    color: AppColors.textMuted,
                                                  ),
                                                ),
                                            ],
                                          ),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              ),
                  ),
                  // Right panel — thread or compose
                  Expanded(
                    child: _showCompose
                        ? _buildComposePanel()
                        : _selectedThread != null
                            ? _buildThreadPanel()
                            : _buildEmptyState(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.forum_rounded,
              size: 48,
              color: AppColors.textMuted.withValues(alpha: 0.3),
            ),
            const SizedBox(height: 12),
            Text(
              'בחר שיחה או צור הודעה חדשה',
              style:
                  GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted),
            ),
          ],
        ),
      );

  Widget _buildComposePanel() => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'הודעה חדשה לצוות התמיכה',
              style: GoogleFonts.heebo(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _category,
              dropdownColor: const Color(0xFF1a2744),
              style: GoogleFonts.heebo(color: Colors.white, fontSize: 14),
              decoration: _inputDeco('קטגוריה'),
              items: [
                DropdownMenuItem(
                  value: 'general',
                  child: Text('כללי', style: GoogleFonts.heebo()),
                ),
                DropdownMenuItem(
                  value: 'bug',
                  child: Text('דיווח על תקלה', style: GoogleFonts.heebo()),
                ),
                DropdownMenuItem(
                  value: 'feature',
                  child: Text('בקשת תכונה', style: GoogleFonts.heebo()),
                ),
                DropdownMenuItem(
                  value: 'improvement',
                  child: Text('הצעה לשיפור', style: GoogleFonts.heebo()),
                ),
                DropdownMenuItem(
                  value: 'billing',
                  child: Text('חיוב ותשלום', style: GoogleFonts.heebo()),
                ),
              ],
              onChanged: (v) => setState(() => _category = v ?? 'general'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _subjectCtrl,
              style: GoogleFonts.heebo(color: Colors.white, fontSize: 14),
              decoration: _inputDeco('נושא'),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: TextField(
                controller: _bodyCtrl,
                maxLines: null,
                expands: true,
                textAlignVertical: TextAlignVertical.top,
                style: GoogleFonts.heebo(color: Colors.white, fontSize: 14),
                decoration: _inputDeco('תוכן ההודעה', alignTop: true),
              ),
            ),
            const SizedBox(height: 10),
            // Attachments
            if (_attachments.isNotEmpty)
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: _attachments
                    .map(
                      (a) => Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: AppColors.primary.withValues(alpha: 0.2),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.attach_file_rounded,
                              size: 14,
                              color: AppColors.primary,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              a['name'] ?? '',
                              style: GoogleFonts.heebo(
                                fontSize: 12,
                                color: AppColors.primary,
                              ),
                            ),
                            const SizedBox(width: 6),
                            InkWell(
                              onTap: () =>
                                  setState(() => _attachments.remove(a)),
                              child: Icon(
                                Icons.close_rounded,
                                size: 14,
                                color: AppColors.textMuted,
                              ),
                            ),
                          ],
                        ),
                      ),
                    )
                    .toList(),
              ),
            if (_attachments.isNotEmpty) const SizedBox(height: 8),
            // Buttons row
            Row(
              children: [
                // Attach button
                IconButton(
                  onPressed: _uploading ? null : _pickFile,
                  tooltip: 'צרף קובץ',
                  icon: _uploading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Icon(
                          Icons.attach_file_rounded,
                          size: 20,
                          color: AppColors.textMuted,
                        ),
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: SizedBox(
                    height: 46,
                    child: ElevatedButton.icon(
                      onPressed: _sending ? null : _sendNewMessage,
                      icon: _sending
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.black,
                              ),
                            )
                          : const Icon(Icons.send_rounded, size: 18),
                      label: Text(
                        _sending ? 'שולח...' : 'שלח הודעה',
                        style: GoogleFonts.heebo(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.black,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        elevation: 0,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                TextButton(
                  onPressed: () => setState(() {
                    _showCompose = false;
                    _attachments = [];
                  }),
                  child: Text(
                    'ביטול',
                    style: GoogleFonts.heebo(color: AppColors.textMuted),
                  ),
                ),
              ],
            ),
          ],
        ),
      );

  Widget _buildThreadPanel() {
    return Column(
      children: [
        // Thread header
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(color: Colors.white.withValues(alpha: 0.06)),
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _selectedThread!['subject'] ?? '',
                      style: GoogleFonts.heebo(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      '${_selectedThread!['message_count'] ?? 0} הודעות',
                      style: GoogleFonts.heebo(
                        fontSize: 11,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        // Messages — chat-style
        Expanded(
          child: _threadLoading
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  itemCount: _threadMessages.length,
                  itemBuilder: (ctx, i) {
                    final m = _threadMessages[i] as Map<String, dynamic>;
                    final isOutbound = m['direction'] == 'outbound';
                    return Align(
                      alignment: isOutbound
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        constraints: BoxConstraints(
                          maxWidth: MediaQuery.of(context).size.width * 0.4,
                        ),
                        decoration: BoxDecoration(
                          color: isOutbound
                              ? AppColors.primary.withValues(alpha: 0.1)
                              : Colors.white.withValues(alpha: 0.05),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                            color: isOutbound
                                ? AppColors.primary.withValues(alpha: 0.2)
                                : Colors.white.withValues(alpha: 0.06),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  isOutbound
                                      ? Icons.support_agent_rounded
                                      : Icons.person_rounded,
                                  size: 14,
                                  color: isOutbound
                                      ? AppColors.primary
                                      : AppColors.textMuted,
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  isOutbound ? 'צוות תמיכה' : 'את/ה',
                                  style: GoogleFonts.heebo(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: isOutbound
                                        ? AppColors.primary
                                        : AppColors.textMuted,
                                  ),
                                ),
                                const Spacer(),
                                Text(
                                  m['created_at']
                                          ?.toString()
                                          .substring(0, 16)
                                          .replaceAll('T', ' ') ??
                                      '',
                                  style: GoogleFonts.heebo(
                                    fontSize: 10,
                                    color: AppColors.textMuted,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              m['body'] ?? '',
                              style: GoogleFonts.heebo(
                                fontSize: 13,
                                color: AppColors.textSecondary,
                                height: 1.6,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
        // Reply box
        Container(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
          decoration: BoxDecoration(
            border: Border(
              top: BorderSide(color: Colors.white.withValues(alpha: 0.06)),
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _replyCtrl,
                  style: GoogleFonts.heebo(color: Colors.white, fontSize: 13),
                  maxLines: 2,
                  minLines: 1,
                  decoration: InputDecoration(
                    hintText: 'כתוב תגובה...',
                    hintStyle: GoogleFonts.heebo(
                      color: Colors.white24,
                      fontSize: 13,
                    ),
                    filled: true,
                    fillColor: Colors.white.withValues(alpha: 0.04),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 10,
                    ),
                  ),
                  onSubmitted: (_) => _sendReply(),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                onPressed: _sending ? null : _sendReply,
                style: IconButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                icon: _sending
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.black,
                        ),
                      )
                    : const Icon(
                        Icons.send_rounded,
                        size: 18,
                        color: Colors.black,
                      ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
