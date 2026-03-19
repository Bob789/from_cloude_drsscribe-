import 'dart:typed_data';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/providers/patient_files_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';

class FileUploadWidget extends ConsumerStatefulWidget {
  final String patientId;
  const FileUploadWidget({super.key, required this.patientId});

  @override
  ConsumerState<FileUploadWidget> createState() => _FileUploadWidgetState();
}

class _FileUploadWidgetState extends ConsumerState<FileUploadWidget> {
  String _category = 'other';
  final _descriptionController = TextEditingController();
  final List<PlatformFile> _selectedFiles = [];
  bool _isDragOver = false;

  List<(String, String)> get _categories => [
    ('other', 'upload.category_other'.tr()),
    ('lab_results', 'upload.category_lab'.tr()),
    ('imaging', 'upload.category_imaging'.tr()),
    ('discharge', 'upload.category_discharge'.tr()),
    ('referral', 'upload.category_referral'.tr()),
    ('prescription', 'upload.category_prescription'.tr()),
    ('insurance', 'upload.category_insurance'.tr()),
    ('consent', 'upload.category_consent'.tr()),
  ];

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _pickFiles() async {
    final result = await FilePicker.platform.pickFiles(
      allowMultiple: true,
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'doc', 'docx'],
      withData: true,
    );
    if (result != null) {
      setState(() {
        for (final file in result.files) {
          if (file.bytes != null && !_selectedFiles.any((f) => f.name == file.name)) {
            _selectedFiles.add(file);
          }
        }
      });
    }
  }

  void _removeFile(int index) {
    setState(() => _selectedFiles.removeAt(index));
  }

  String _formatSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  Future<void> _upload() async {
    if (_selectedFiles.isEmpty) return;
    final notifier = ref.read(patientFilesProvider.notifier);

    if (_selectedFiles.length == 1) {
      final file = _selectedFiles.first;
      await notifier.uploadFile(
        patientId: widget.patientId,
        bytes: file.bytes!,
        fileName: file.name,
        category: _category,
        description: _descriptionController.text.isNotEmpty ? _descriptionController.text : null,
      );
    } else {
      final filesData = _selectedFiles
          .map((f) => MapEntry(f.name, f.bytes!))
          .toList();
      await notifier.uploadMultiple(
        patientId: widget.patientId,
        filesData: filesData,
        category: _category,
      );
    }

    if (mounted) {
      setState(() {
        _selectedFiles.clear();
        _descriptionController.clear();
        _category = 'other';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final filesState = ref.watch(patientFilesProvider);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildDropZone(),
          if (_selectedFiles.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildCategoryDropdown(),
            const SizedBox(height: 12),
            _buildDescriptionField(),
            const SizedBox(height: 16),
            _buildSelectedFilesList(),
            const SizedBox(height: 16),
            _buildUploadButton(filesState),
          ],
        ],
      ),
    );
  }

  Widget _buildDropZone() {
    return DragTarget<Object>(
      onWillAcceptWithDetails: (_) {
        setState(() => _isDragOver = true);
        return true;
      },
      onLeave: (_) => setState(() => _isDragOver = false),
      onAcceptWithDetails: (_) => setState(() => _isDragOver = false),
      builder: (context, candidateData, rejectedData) {
        return GestureDetector(
          onTap: _pickFiles,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 16),
            decoration: BoxDecoration(
              color: _isDragOver ? AppColors.primary.withValues(alpha: 0.08) : Colors.transparent,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _isDragOver ? AppColors.primary : AppColors.border,
                width: _isDragOver ? 2 : 1,
              ),
            ),
            child: Column(
              children: [
                Icon(Icons.cloud_upload_rounded, size: 40, color: AppColors.primary),
                const SizedBox(height: 12),
                Text(
                  'upload.drag_hint'.tr(),
                  style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 4),
                Text(
                  'upload.drag_subtitle'.tr(),
                  style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCategoryDropdown() {
    return Row(
      children: [
        Text('upload.category_label'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textSecondary)),
        const SizedBox(width: 12),
        Expanded(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _category,
                dropdownColor: AppColors.card,
                style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
                isExpanded: true,
                items: _categories.map((c) {
                  return DropdownMenuItem(value: c.$1, child: Text(c.$2));
                }).toList(),
                onChanged: (v) => setState(() => _category = v ?? 'other'),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDescriptionField() {
    return TextField(
      controller: _descriptionController,
      style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textPrimary),
      decoration: InputDecoration(
        hintText: 'upload.description_hint'.tr(),
        hintStyle: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted),
        filled: true,
        fillColor: AppColors.background,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.border)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.border)),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: AppColors.primary)),
      ),
    );
  }

  Widget _buildSelectedFilesList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('upload.selected_files'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
        const SizedBox(height: 8),
        ..._selectedFiles.asMap().entries.map((entry) {
          final i = entry.key;
          final file = entry.value;
          final isImage = file.extension != null && ['jpg', 'jpeg', 'png', 'gif', 'webp'].contains(file.extension!.toLowerCase());
          return Container(
            margin: const EdgeInsets.only(bottom: 6),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border),
            ),
            child: Row(
              children: [
                Icon(isImage ? Icons.image_rounded : Icons.description_rounded, size: 18, color: AppColors.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    file.name,
                    style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textPrimary),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Text(
                  _formatSize(file.size),
                  style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textMuted),
                ),
                const SizedBox(width: 8),
                InkWell(
                  onTap: () => _removeFile(i),
                  child: Icon(Icons.close_rounded, size: 16, color: AppColors.accent),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildUploadButton(PatientFilesState filesState) {
    if (filesState.isUploading) {
      return Column(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: filesState.uploadProgress,
              backgroundColor: AppColors.border,
              valueColor: AlwaysStoppedAnimation(AppColors.primary),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${(filesState.uploadProgress * 100).toInt()}%',
            style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted),
          ),
        ],
      );
    }

    return ElevatedButton.icon(
      onPressed: _selectedFiles.isEmpty ? null : _upload,
      icon: const Icon(Icons.upload_rounded, size: 18),
      label: Text('upload.upload_button'.tr(namedArgs: {'count': _selectedFiles.length.toString()}), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600)),
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.background,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}
