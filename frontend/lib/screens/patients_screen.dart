import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/providers/patients_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:html' as html;

class PatientsScreen extends ConsumerStatefulWidget {
  const PatientsScreen({super.key});

  @override
  ConsumerState<PatientsScreen> createState() => _PatientsScreenState();
}

class _PatientsScreenState extends ConsumerState<PatientsScreen> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(patientsProvider.notifier).loadPatients();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final patientsState = ref.watch(patientsProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(context, ext),
          _buildSearchBar(ext),
          Expanded(
            child: patientsState.when(
              loading: () => Center(
                child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5),
              ),
              error: (error) => _buildErrorState(error),
              data: (patients) => patients.isEmpty ? _buildEmptyState() : _buildPatientsList(patients, ext),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context, MedScribeThemeExtension ext) {
    final isNarrow = MediaQuery.of(context).size.width < 600;
    return Padding(
      padding: EdgeInsets.fromLTRB(isNarrow ? 12 : 24, isNarrow ? 12 : 24, isNarrow ? 12 : 24, 0),
      child: Wrap(
        spacing: 12,
        runSpacing: 10,
        alignment: WrapAlignment.spaceBetween,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('patients.title'.tr(), style: GoogleFonts.heebo(fontSize: isNarrow ? 20 : 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
              const SizedBox(height: 4),
              Text('patients.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: isNarrow ? 12 : 14, color: AppColors.textMuted)),
            ],
          ),
          Row(mainAxisSize: MainAxisSize.min, children: [
            IconButton(
              onPressed: _exportCsv,
              tooltip: 'ייצוא CSV',
              icon: Icon(Icons.download_rounded, size: 20, color: AppColors.textSecondary),
            ),
            IconButton(
              onPressed: _importCsv,
              tooltip: 'ייבוא CSV',
              icon: Icon(Icons.upload_rounded, size: 20, color: AppColors.textSecondary),
            ),
            const SizedBox(width: 4),
            Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: () => context.go('/patients/new'),
                borderRadius: BorderRadius.circular(ext.cardRadius),
                child: Container(
                  padding: EdgeInsets.symmetric(horizontal: isNarrow ? 10 : 16, vertical: 10),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]),
                    borderRadius: BorderRadius.circular(ext.cardRadius),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.add_rounded, color: Colors.white, size: 18),
                      if (!isNarrow) ...[
                        const SizedBox(width: 6),
                        Text('patients.add_new'.tr(), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white)),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ]),
        ],
      ),
    );
  }

  Widget _buildSearchBar(MedScribeThemeExtension ext) {
    return Padding(
      padding: EdgeInsets.fromLTRB(MediaQuery.of(context).size.width < 600 ? 12 : 24, 16, MediaQuery.of(context).size.width < 600 ? 12 : 24, 12),
      child: TextField(
        controller: _searchController,
        style: GoogleFonts.heebo(color: AppColors.textPrimary, fontSize: 14),
        decoration: InputDecoration(
          hintText: 'patients.search_hint'.tr(),
          prefixIcon: Icon(Icons.search_rounded, color: AppColors.textMuted, size: 20),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: Icon(Icons.close_rounded, size: 18, color: AppColors.textMuted),
                  onPressed: () {
                    _searchController.clear();
                    ref.read(patientsProvider.notifier).search('');
                  },
                )
              : null,
          filled: true,
          fillColor: AppColors.card,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(ext.cardRadius), borderSide: BorderSide(color: AppColors.cardBorder)),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(ext.cardRadius), borderSide: BorderSide(color: AppColors.cardBorder)),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(ext.cardRadius), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        ),
        onChanged: (value) {
          setState(() {});
          ref.read(patientsProvider.notifier).search(value);
        },
      ),
    );
  }

  Widget _buildPatientsList(List<PatientModel> patients, MedScribeThemeExtension ext) {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(24, 4, 24, 24),
      itemCount: patients.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) => _buildPatientCard(patients[index], ext),
    );
  }

  Widget _buildPatientCard(PatientModel patient, MedScribeThemeExtension ext) {
    final initials = patient.name.isNotEmpty ? patient.name[0].toUpperCase() : '?';

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => context.go('/patients/${patient.displayId}'),
        borderRadius: BorderRadius.circular(ext.cardRadius),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: ext.cardDecoration,
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppColors.primary.withValues(alpha: 0.2), AppColors.secondary.withValues(alpha: 0.1)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(initials, style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.primary)),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(patient.name, style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                    if (patient.phone != null && patient.phone!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 2),
                        child: Text(patient.phone!, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
                      ),
                  ],
                ),
              ),
              if (patient.allergies != null && patient.allergies!.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.accent.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.warning_amber_rounded, size: 12, color: AppColors.accent),
                      const SizedBox(width: 4),
                      Text('patients.allergies'.tr(), style: GoogleFonts.heebo(fontSize: 10, fontWeight: FontWeight.w500, color: AppColors.accent)),
                    ],
                  ),
                ),
              const SizedBox(width: 4),
              IconButton(
                icon: Icon(Icons.delete_outline_rounded, size: 18, color: AppColors.accent.withValues(alpha: 0.6)),
                tooltip: 'מחק מטופל',
                padding: const EdgeInsets.all(6),
                constraints: const BoxConstraints(),
                onPressed: () => _showDeleteDialog(patient),
              ),
              const SizedBox(width: 4),
              Icon(Icons.chevron_left_rounded, color: AppColors.textMuted, size: 20),
            ],
          ),
        ),
      ),
    );
  }

  void _showDeleteDialog(PatientModel patient) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1a2744),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(children: [
          Icon(Icons.warning_amber_rounded, color: AppColors.accent, size: 28),
          const SizedBox(width: 10),
          Text('מחיקת מטופל', style: GoogleFonts.heebo(fontWeight: FontWeight.w700, color: AppColors.accent)),
        ]),
        content: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          RichText(text: TextSpan(style: GoogleFonts.heebo(fontSize: 14, color: Colors.white, height: 1.7), children: [
            const TextSpan(text: 'אתה עומד למחוק את המטופל '),
            TextSpan(text: patient.name, style: GoogleFonts.heebo(fontWeight: FontWeight.w700, color: AppColors.accent)),
            const TextSpan(text: ' לצמיתות.'),
          ])),
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.accent.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: AppColors.accent.withValues(alpha: 0.2)),
            ),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('פעולה זו תמחק לצמיתות:', style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.accent)),
              const SizedBox(height: 6),
              ...[
                'כל היסטוריית הביקורים',
                'כל הסיכומים הרפואיים',
                'כל ההקלטות והתמלולים',
                'כל הקבצים המצורפים',
              ].map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 3),
                child: Row(children: [
                  Icon(Icons.remove_circle_outline, size: 14, color: AppColors.accent.withValues(alpha: 0.7)),
                  const SizedBox(width: 6),
                  Text(item, style: GoogleFonts.heebo(fontSize: 12, color: Colors.white70)),
                ]),
              )),
            ]),
          ),
          const SizedBox(height: 14),
          Text('לא ניתן לבטל פעולה זו!', style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.accent)),
        ]),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('ביטול', style: GoogleFonts.heebo(color: Colors.white60, fontWeight: FontWeight.w500)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accent,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () async {
              Navigator.pop(ctx);
              await _deletePatient(patient);
            },
            child: Text('מחק לצמיתות', style: GoogleFonts.heebo(fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
  }

  Future<void> _deletePatient(PatientModel patient) async {
    try {
      final dio = ApiClient().dio;
      await dio.delete('/patients/${patient.displayId}');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('המטופל ${patient.name} נמחק בהצלחה', style: GoogleFonts.heebo()),
          backgroundColor: Colors.green.shade700,
        ));
        ref.read(patientsProvider.notifier).loadPatients();
      }
    } on DioException catch (e) {
      if (mounted) {
        final msg = e.response?.data?['message'] ?? 'שגיאה במחיקת המטופל';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(msg, style: GoogleFonts.heebo()),
          backgroundColor: Colors.red.shade700,
        ));
      }
    }
  }

  Future<void> _exportCsv() async {
    final patients = ref.read(patientsProvider).patients;
    if (patients.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('אין מטופלים לייצוא', style: GoogleFonts.heebo()), backgroundColor: Colors.orange.shade700));
      return;
    }

    // Selection dialog
    final selected = await showDialog<List<int>?>(
      context: context,
      builder: (ctx) => _ExportDialog(patients: patients),
    );

    if (selected == null) return; // cancelled

    try {
      final queryParams = <String, dynamic>{};
      if (selected.isNotEmpty) {
        queryParams['ids'] = selected.join(',');
      }
      // empty list = all patients

      final dio = ApiClient().dio;
      final response = await dio.get('/patients/export/csv', queryParameters: queryParams, options: Options(responseType: ResponseType.bytes));
      final blob = html.Blob([response.data], 'text/csv');
      final url = html.Url.createObjectUrlFromBlob(blob);
      final anchor = html.AnchorElement(href: url)
        ..setAttribute('download', 'patients_export.csv')
        ..click();
      html.Url.revokeObjectUrl(url);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('הקובץ הורד בהצלחה', style: GoogleFonts.heebo()), backgroundColor: Colors.green.shade700));
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('שגיאה בייצוא', style: GoogleFonts.heebo()), backgroundColor: Colors.red.shade700));
      }
    }
  }

  Future<void> _importCsv() async {
    try {
      final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['csv'], withData: true);
      if (result == null || result.files.isEmpty || result.files.first.bytes == null) return;
      final file = result.files.first;

      final confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: const Color(0xFF1a2744),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Text('ייבוא מטופלים מ-CSV', style: GoogleFonts.heebo(fontWeight: FontWeight.w700, color: Colors.white)),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            Text('קובץ: ${file.name}', style: GoogleFonts.heebo(fontSize: 14, color: Colors.white70)),
            const SizedBox(height: 10),
            Text('מטופלים קיימים לא יידרסו — רק חדשים ייווצרו.', style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
          ]),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text('ביטול', style: GoogleFonts.heebo(color: Colors.white60))),
            ElevatedButton(
              onPressed: () => Navigator.pop(ctx, true),
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.black, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))),
              child: Text('ייבא', style: GoogleFonts.heebo(fontWeight: FontWeight.w700)),
            ),
          ],
        ),
      );

      if (confirm != true) return;

      final dio = ApiClient().dio;
      final formData = FormData.fromMap({'file': MultipartFile.fromBytes(file.bytes!, filename: file.name)});
      final response = await dio.post('/patients/import/csv', data: formData);
      final data = response.data;

      if (mounted) {
        final msg = 'יובאו ${data['created_patients']} מטופלים ו-${data['created_visits']} ביקורים';
        final errCount = (data['errors'] as List?)?.length ?? 0;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(errCount > 0 ? '$msg ($errCount שגיאות)' : msg, style: GoogleFonts.heebo()),
          backgroundColor: errCount > 0 ? Colors.orange.shade700 : Colors.green.shade700,
          duration: const Duration(seconds: 4),
        ));
        ref.read(patientsProvider.notifier).loadPatients();
      }
    } on DioException catch (e) {
      if (mounted) {
        final msg = e.response?.data?['message'] ?? 'שגיאה בייבוא';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg, style: GoogleFonts.heebo()), backgroundColor: Colors.red.shade700));
      }
    } catch (_) {}
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.people_outline_rounded, size: 56, color: AppColors.textMuted.withValues(alpha: 0.4)),
          const SizedBox(height: 16),
          Text('patients.empty'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
          const SizedBox(height: 6),
          Text('patients.empty_hint'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline_rounded, size: 48, color: AppColors.accent.withValues(alpha: 0.6)),
          const SizedBox(height: 16),
          Text('patients.load_error'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textSecondary)),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => ref.read(patientsProvider.notifier).loadPatients(),
            icon: const Icon(Icons.refresh_rounded, size: 18),
            label: Text('common.retry'.tr()),
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.primary,
              side: BorderSide(color: AppColors.primary),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Export Selection Dialog ──────────────────────────────────────────────────

class _ExportDialog extends StatefulWidget {
  final List<PatientModel> patients;
  const _ExportDialog({required this.patients});

  @override
  State<_ExportDialog> createState() => _ExportDialogState();
}

class _ExportDialogState extends State<_ExportDialog> {
  bool _selectAll = true;
  late Set<int> _selected;

  @override
  void initState() {
    super.initState();
    _selected = widget.patients.map((p) => p.displayId).toSet();
  }

  void _toggleAll(bool? val) {
    setState(() {
      _selectAll = val ?? false;
      if (_selectAll) {
        _selected = widget.patients.map((p) => p.displayId).toSet();
      } else {
        _selected.clear();
      }
    });
  }

  void _toggle(int id) {
    setState(() {
      if (_selected.contains(id)) {
        _selected.remove(id);
      } else {
        _selected.add(id);
      }
      _selectAll = _selected.length == widget.patients.length;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: const Color(0xFF141828),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        width: MediaQuery.of(context).size.width < 500 ? MediaQuery.of(context).size.width * 0.92 : 420,
        constraints: const BoxConstraints(maxHeight: 520),
        padding: const EdgeInsets.all(24),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Row(children: [
            Icon(Icons.download_rounded, color: AppColors.primary, size: 24),
            const SizedBox(width: 10),
            Text('ייצוא מטופלים ל-CSV', style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: Colors.white)),
          ]),
          const SizedBox(height: 6),
          Text('בחר מטופלים לייצוא כולל היסטוריית ביקורים', style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
          const SizedBox(height: 16),
          // Select all checkbox
          InkWell(
            onTap: () => _toggleAll(!_selectAll),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.06),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.primary.withValues(alpha: 0.15)),
              ),
              child: Row(children: [
                Checkbox(value: _selectAll, onChanged: _toggleAll, activeColor: AppColors.primary, checkColor: Colors.black),
                Text('כל המטופלים (${widget.patients.length})', style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.primary)),
              ]),
            ),
          ),
          const SizedBox(height: 10),
          // Patient list
          Flexible(
            child: Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
                borderRadius: BorderRadius.circular(12),
              ),
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: widget.patients.length,
                itemBuilder: (ctx, i) {
                  final p = widget.patients[i];
                  final isChecked = _selected.contains(p.displayId);
                  return InkWell(
                    onTap: () => _toggle(p.displayId),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        border: Border(bottom: BorderSide(color: Colors.white.withValues(alpha: 0.04))),
                        color: isChecked ? Colors.white.withValues(alpha: 0.02) : Colors.transparent,
                      ),
                      child: Row(children: [
                        Checkbox(value: isChecked, onChanged: (_) => _toggle(p.displayId), activeColor: AppColors.primary, checkColor: Colors.black),
                        const SizedBox(width: 6),
                        Container(
                          width: 32, height: 32,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(colors: [AppColors.primary.withValues(alpha: 0.2), AppColors.secondary.withValues(alpha: 0.1)]),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Center(child: Text(p.name.isNotEmpty ? p.name[0].toUpperCase() : '?', style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w700, color: AppColors.primary))),
                        ),
                        const SizedBox(width: 10),
                        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Text(p.name, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white)),
                          if (p.phone != null && p.phone!.isNotEmpty)
                            Text(p.phone!, style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textMuted)),
                        ])),
                      ]),
                    ),
                  );
                },
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Buttons
          Row(mainAxisAlignment: MainAxisAlignment.end, children: [
            TextButton(
              onPressed: () => Navigator.pop(context, null),
              child: Text('ביטול', style: GoogleFonts.heebo(color: Colors.white60)),
            ),
            const SizedBox(width: 10),
            ElevatedButton.icon(
              onPressed: _selected.isEmpty ? null : () {
                Navigator.pop(context, _selectAll ? <int>[] : _selected.toList());
              },
              icon: const Icon(Icons.download_rounded, size: 18),
              label: Text(
                _selected.isEmpty ? 'בחר מטופלים' : 'ייצא ${_selectAll ? "הכל" : "${_selected.length} מטופלים"}',
                style: GoogleFonts.heebo(fontWeight: FontWeight.w700),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.black,
                disabledBackgroundColor: Colors.white.withValues(alpha: 0.1),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              ),
            ),
          ]),
        ]),
      ),
    );
  }
}
