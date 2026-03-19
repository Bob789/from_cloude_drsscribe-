import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:easy_localization/easy_localization.dart' as easy;
import 'package:url_launcher/url_launcher.dart';
import 'package:medscribe_ai/models/patient_file_model.dart';
import 'package:medscribe_ai/providers/patient_files_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/widgets/file_preview_modal.dart';

class FileListWidget extends ConsumerStatefulWidget {
  final String patientId;
  const FileListWidget({super.key, required this.patientId});

  @override
  ConsumerState<FileListWidget> createState() => _FileListWidgetState();
}

class _FileListWidgetState extends ConsumerState<FileListWidget> {
  String? _activeCategory;

  static final _filterChips = [
    (null, 'files.filter_all'),
    ('lab_results', 'files.category_lab_results'),
    ('imaging', 'files.category_imaging'),
    ('discharge', 'files.category_discharge'),
    ('referral', 'files.category_referral'),
    ('prescription', 'files.category_prescription'),
    ('other', 'files.category_other'),
  ];

  void _onFilterChanged(String? category) {
    setState(() => _activeCategory = category);
    ref.read(patientFilesProvider.notifier).filterByCategory(category);
    ref.read(patientFilesProvider.notifier).loadFiles(widget.patientId, category: category);
  }

  @override
  Widget build(BuildContext context) {
    final filesState = ref.watch(patientFilesProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildFilterChips(),
        const SizedBox(height: 12),
        if (filesState.isLoading)
          const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()))
        else if (filesState.files.isEmpty)
          _buildEmptyState()
        else
          ...filesState.files.map((f) => _buildFileCard(f)),
      ],
    );
  }

  Widget _buildFilterChips() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: _filterChips.map((chip) {
          final isActive = _activeCategory == chip.$1;
          return Padding(
            padding: const EdgeInsetsDirectional.only(end: 8),
            child: FilterChip(
              label: Text(
                chip.$2.tr(),
                style: GoogleFonts.heebo(
                  fontSize: 12,
                  fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                  color: isActive ? AppColors.background : AppColors.textSecondary,
                ),
              ),
              selected: isActive,
              onSelected: (_) => _onFilterChanged(chip.$1),
              backgroundColor: AppColors.card,
              selectedColor: AppColors.primary,
              side: BorderSide(color: isActive ? AppColors.primary : AppColors.border),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              showCheckmark: false,
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          Icon(Icons.folder_open_rounded, size: 48, color: AppColors.textMuted),
          const SizedBox(height: 12),
          Text('files.no_files'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
        ],
      ),
    );
  }

  Widget _buildFileCard(PatientFileModel file) {
    final dateStr = DateFormat('dd/MM/yyyy').format(file.createdAt);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.cardBorder),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(file.categoryIcon, size: 20, color: AppColors.primary),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  file.categoryLabel,
                  style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 2),
                Text(
                  '${file.fileName} — ${file.fileSizeFormatted}',
                  style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textSecondary),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  dateStr,
                  style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textMuted),
                ),
                if (file.description != null && file.description!.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    '"${file.description}"',
                    style: GoogleFonts.heebo(fontSize: 11, fontStyle: FontStyle.italic, color: AppColors.textMuted),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 8),
          _buildActions(file),
        ],
      ),
    );
  }

  Widget _buildActions(PatientFileModel file) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _actionButton(Icons.visibility_rounded, 'files.view'.tr(), () => _preview(file)),
        _actionButton(Icons.download_rounded, 'files.download'.tr(), () => _download(file)),
        _actionButton(Icons.delete_outline_rounded, 'common.delete'.tr(), () => _confirmDelete(file), isDestructive: true),
      ],
    );
  }

  Widget _actionButton(IconData icon, String tooltip, VoidCallback onTap, {bool isDestructive = false}) {
    return Tooltip(
      message: tooltip,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(6),
        child: Padding(
          padding: const EdgeInsets.all(6),
          child: Icon(icon, size: 18, color: isDestructive ? AppColors.accent : AppColors.textMuted),
        ),
      ),
    );
  }

  Future<void> _preview(PatientFileModel file) async {
    final notifier = ref.read(patientFilesProvider.notifier);
    final info = await notifier.getPreviewInfo(widget.patientId, file.id);
    if (info != null && mounted) {
      showDialog(
        context: context,
        builder: (_) => FilePreviewModal(
          fileName: file.fileName,
          category: file.categoryLabel,
          description: file.description,
          mimeType: info['mime_type'],
          previewUrl: info['preview_url'],
          isPreviewable: info['is_previewable'] ?? false,
          patientId: widget.patientId,
          fileId: file.id,
        ),
      );
    }
  }

  Future<void> _download(PatientFileModel file) async {
    final notifier = ref.read(patientFilesProvider.notifier);
    final url = await notifier.getDownloadUrl(widget.patientId, file.id);
    if (url != null && mounted) {
      _openUrl(url);
    }
  }

  void _openUrl(String url) {
    launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
  }

  Future<void> _confirmDelete(PatientFileModel file) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.card,
        title: Text('files.delete_file_title'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        content: Text(
          'files.delete_file_confirm'.tr(namedArgs: {'fileName': file.fileName}),
          style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text('common.cancel'.tr(), style: GoogleFonts.heebo(color: AppColors.textMuted)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text('common.delete'.tr(), style: GoogleFonts.heebo(color: AppColors.accent, fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      ref.read(patientFilesProvider.notifier).deleteFile(widget.patientId, file.id);
    }
  }
}
