import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:url_launcher/url_launcher.dart';
import 'package:medscribe_ai/providers/patient_files_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';

class FilePreviewModal extends ConsumerWidget {
  final String fileName;
  final String category;
  final String? description;
  final String? mimeType;
  final String previewUrl;
  final bool isPreviewable;
  final String patientId;
  final int fileId;

  const FilePreviewModal({
    super.key,
    required this.fileName,
    required this.category,
    this.description,
    this.mimeType,
    required this.previewUrl,
    required this.isPreviewable,
    required this.patientId,
    required this.fileId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isImage = mimeType != null && mimeType!.startsWith('image/');
    final isPdf = mimeType == 'application/pdf';
    final screenSize = MediaQuery.of(context).size;

    return Dialog(
      backgroundColor: AppColors.card,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: isImage ? screenSize.width * 0.8 : 500,
          maxHeight: screenSize.height * 0.85,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(context),
            if (isImage) _buildImagePreview(),
            if (!isImage) _buildFileInfo(),
            _buildActions(context, ref, isPdf),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  fileName,
                  style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  category,
                  style: GoogleFonts.heebo(fontSize: 12, color: AppColors.primary),
                ),
                if (description != null && description!.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    description!,
                    style: GoogleFonts.heebo(fontSize: 12, fontStyle: FontStyle.italic, color: AppColors.textMuted),
                  ),
                ],
              ],
            ),
          ),
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: Icon(Icons.close_rounded, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }

  Widget _buildImagePreview() {
    return Flexible(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: InteractiveViewer(
          minScale: 0.5,
          maxScale: 4.0,
          child: Image.network(
            previewUrl,
            fit: BoxFit.contain,
            loadingBuilder: (_, child, progress) {
              if (progress == null) return child;
              return Center(
                child: CircularProgressIndicator(
                  value: progress.expectedTotalBytes != null
                      ? progress.cumulativeBytesLoaded / progress.expectedTotalBytes!
                      : null,
                ),
              );
            },
            errorBuilder: (_, __, ___) => Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.broken_image_rounded, size: 48, color: AppColors.textMuted),
                  const SizedBox(height: 8),
                  Text('files.image_load_error'.tr(), style: GoogleFonts.heebo(color: AppColors.textMuted)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFileInfo() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Icon(Icons.insert_drive_file_rounded, size: 56, color: AppColors.primary),
          const SizedBox(height: 12),
          Text(
            mimeType ?? 'files.file_type_generic'.tr(),
            style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }

  Widget _buildActions(BuildContext context, WidgetRef ref, bool isPdf) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          if (isPdf)
            TextButton.icon(
              onPressed: () => launchUrl(Uri.parse(previewUrl), mode: LaunchMode.externalApplication),
              icon: Icon(Icons.open_in_new_rounded, size: 16, color: AppColors.primary),
              label: Text('files.open_new_tab'.tr(), style: GoogleFonts.heebo(fontSize: 12, color: AppColors.primary)),
            ),
          const SizedBox(width: 8),
          ElevatedButton.icon(
            onPressed: () async {
              final notifier = ref.read(patientFilesProvider.notifier);
              final url = await notifier.getDownloadUrl(patientId, fileId);
              if (url != null) {
                launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
              }
            },
            icon: const Icon(Icons.download_rounded, size: 16),
            label: Text('files.download'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600)),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: AppColors.background,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
        ],
      ),
    );
  }
}
