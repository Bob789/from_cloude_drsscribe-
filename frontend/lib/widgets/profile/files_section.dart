import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/providers/patient_files_provider.dart';
import 'package:medscribe_ai/widgets/file_upload_widget.dart';
import 'package:medscribe_ai/widgets/file_list_widget.dart';

class FilesSection extends ConsumerStatefulWidget {
  final String patientId;
  const FilesSection({super.key, required this.patientId});

  @override
  ConsumerState<FilesSection> createState() => _FilesSectionState();
}

class _FilesSectionState extends ConsumerState<FilesSection> {
  bool _showUpload = false;

  @override
  Widget build(BuildContext context) {
    final filesState = ref.watch(patientFilesProvider);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Icon(Icons.folder_rounded, size: 20, color: AppColors.primary),
          const SizedBox(width: 8),
          Text('files.title'.tr(), style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
          const SizedBox(width: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8)),
            child: Text('${filesState.total}', style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primary)),
          ),
          const Spacer(),
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => setState(() => _showUpload = !_showUpload),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)), borderRadius: BorderRadius.circular(8)),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  Icon(_showUpload ? Icons.close_rounded : Icons.add_rounded, size: 16, color: AppColors.primary),
                  const SizedBox(width: 4),
                  Text(_showUpload ? 'common.close'.tr() : 'files.add_file'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500, color: AppColors.primary)),
                ]),
              ),
            ),
          ),
        ]),
        const SizedBox(height: 14),
        if (_showUpload) ...[
          FileUploadWidget(patientId: widget.patientId),
          const SizedBox(height: 16),
        ],
        FileListWidget(patientId: widget.patientId),
      ],
    );
  }
}
