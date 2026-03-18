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

// ── Design constants ──
const _kCream = Color(0xFFFCF9C6);
const _kNavy = Color(0xFF003399);
const _kNavyLight = Color(0xFF1A56DB);
const _kGold = Color(0xFFC8A000);
const _kHeaderGradient1 = Color(0xFF2D3A4A);
const _kHeaderGradient2 = Color(0xFF5A6A5A);
const _kInputBorder = Color(0xFF1A56DB);
const _kMuted = Color(0xFF8899AA);

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
    final isNarrow = MediaQuery.of(context).size.width < 600;

    return Scaffold(
      backgroundColor: const Color(0xFF0A1628),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 820),
          child: Column(
            children: [
              // ── Header bar ──
              _buildHeaderBar(isNarrow),
              // ── Red title lines ──
              Container(
                color: _kCream,
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                child: Column(children: [
                  Container(height: 2, color: Colors.red),
                  const SizedBox(height: 4),
                  Container(height: 2, color: Colors.red),
                ]),
              ),
              // ── Content ──
              Expanded(
                child: Container(
                  color: _kCream,
                  child: Column(
                    children: [
                      _buildSearchSection(isNarrow),
                      _buildPipeDivider(),
                      Expanded(
                        child: patientsState.when(
                          loading: () => const Center(child: CircularProgressIndicator(color: _kNavy, strokeWidth: 2.5)),
                          error: (error) => _buildEmptyState(error, isError: true),
                          data: (patients) => patients.isEmpty ? _buildEmptyState('', isError: false) : _buildPatientsList(patients, isNarrow),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              // ── Footer ──
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(colors: [_kHeaderGradient1, _kHeaderGradient2]),
                  border: Border(top: BorderSide(color: _kGold, width: 2)),
                ),
                child: Text('Doctor Scribe AI — פרטי קשר | תמיכה | הגדרות', textAlign: TextAlign.center, style: GoogleFonts.rubik(fontSize: 12, color: Colors.white)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Header bar ──
  Widget _buildHeaderBar(bool isNarrow) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(horizontal: isNarrow ? 14 : 24, vertical: 14),
      decoration: const BoxDecoration(
        gradient: LinearGradient(colors: [_kHeaderGradient1, _kHeaderGradient2]),
        border: Border(bottom: BorderSide(color: _kGold, width: 2)),
      ),
      child: Wrap(
        spacing: 12,
        runSpacing: 8,
        alignment: WrapAlignment.spaceBetween,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Row(mainAxisSize: MainAxisSize.min, children: [
            InkWell(
              onTap: () => context.go('/dashboard'),
              child: Container(
                width: 36, height: 36,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  border: Border.all(color: Colors.white.withValues(alpha: 0.3)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 18),
              ),
            ),
            const SizedBox(width: 14),
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('patients.title'.tr(), style: GoogleFonts.rubik(fontSize: isNarrow ? 18 : 22, fontWeight: FontWeight.w800, color: Colors.white)),
              Text('patients.subtitle'.tr(), style: GoogleFonts.rubik(fontSize: 12, color: Colors.white70)),
            ]),
          ]),
          Row(mainAxisSize: MainAxisSize.min, children: [
            _headerIconBtn(Icons.download_rounded, 'ייצוא CSV', _exportCsv),
            const SizedBox(width: 4),
            _headerIconBtn(Icons.upload_rounded, 'ייבוא CSV', _importCsv),
            const SizedBox(width: 8),
            InkWell(
              onTap: () => context.go('/patients/new'),
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: isNarrow ? 10 : 16, vertical: 8),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [_kNavyLight, _kNavy]),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.white.withValues(alpha: 0.3)),
                ),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  const Icon(Icons.add_rounded, color: Colors.white, size: 18),
                  if (!isNarrow) ...[
                    const SizedBox(width: 6),
                    Text('patients.add_new'.tr(), style: GoogleFonts.rubik(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white)),
                  ],
                ]),
              ),
            ),
          ]),
        ],
      ),
    );
  }

  Widget _headerIconBtn(IconData icon, String tooltip, VoidCallback onTap) {
    return Tooltip(
      message: tooltip,
      child: InkWell(
        onTap: onTap,
        child: Container(
          width: 34, height: 34,
          decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6)),
          child: Icon(icon, size: 18, color: Colors.white.withValues(alpha: 0.8)),
        ),
      ),
    );
  }

  // ── Search section ──
  Widget _buildSearchSection(bool isNarrow) {
    return Padding(
      padding: EdgeInsets.fromLTRB(isNarrow ? 12 : 20, 14, isNarrow ? 12 : 20, 0),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('patients.title'.tr(), style: GoogleFonts.rubik(fontSize: 20, fontWeight: FontWeight.w800, color: _kNavy)),
        const SizedBox(height: 10),
        TextField(
          controller: _searchController,
          style: GoogleFonts.heebo(color: const Color(0xFF111111), fontSize: 14),
          decoration: InputDecoration(
            hintText: 'patients.search_hint'.tr(),
            hintStyle: GoogleFonts.heebo(color: _kMuted, fontSize: 14),
            prefixIcon: const Icon(Icons.search_rounded, color: _kMuted, size: 20),
            suffixIcon: _searchController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.close_rounded, size: 18, color: _kMuted),
                    onPressed: () { _searchController.clear(); ref.read(patientsProvider.notifier).search(''); },
                  )
                : null,
            filled: true,
            fillColor: Colors.white.withValues(alpha: 0.65),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _kInputBorder)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _kInputBorder)),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _kNavy, width: 1.5)),
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          ),
          onChanged: (value) {
            setState(() {});
            ref.read(patientsProvider.notifier).search(value);
          },
        ),
      ]),
    );
  }

  // ── Pipe divider ──
  Widget _buildPipeDivider() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        children: [
          Container(
            width: 18,
            height: 12,
            decoration: BoxDecoration(
              border: Border.all(color: _kNavyLight, width: 2),
              borderRadius: const BorderRadius.only(topRight: Radius.circular(50), bottomRight: Radius.circular(50)),
            ),
          ),
          Expanded(
            child: Column(children: [
              Container(height: 2, color: _kNavyLight),
              const SizedBox(height: 4),
              Container(height: 2, color: _kNavyLight),
            ]),
          ),
          Container(
            width: 18,
            height: 12,
            decoration: BoxDecoration(
              border: Border.all(color: _kNavyLight, width: 2),
              borderRadius: const BorderRadius.only(topLeft: Radius.circular(50), bottomLeft: Radius.circular(50)),
            ),
          ),
        ],
      ),
    );
  }

  // ── Patients list ──
  Widget _buildPatientsList(List<PatientModel> patients, bool isNarrow) {
    return ListView.separated(
      padding: EdgeInsets.fromLTRB(isNarrow ? 12 : 20, 0, isNarrow ? 12 : 20, 20),
      itemCount: patients.length,
      separatorBuilder: (_, __) => const SizedBox(height: 6),
      itemBuilder: (context, index) => _buildPatientCard(patients[index], isNarrow),
    );
  }

  Widget _buildPatientCard(PatientModel patient, bool isNarrow) {
    final initials = patient.name.isNotEmpty ? patient.name[0].toUpperCase() : '?';

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => context.go('/patients/${patient.displayId}'),
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: EdgeInsets.all(isNarrow ? 10 : 14),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.65),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: _kInputBorder.withValues(alpha: 0.3)),
          ),
          child: Row(
            children: [
              Container(
                width: isNarrow ? 36 : 42,
                height: isNarrow ? 36 : 42,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [Color(0xFFFFFFFF), Color(0xFFC8D8FF)]),
                  borderRadius: BorderRadius.circular(isNarrow ? 8 : 10),
                  border: Border.all(color: _kNavy.withValues(alpha: 0.2)),
                ),
                child: Center(
                  child: Text(initials, style: GoogleFonts.rubik(fontSize: isNarrow ? 14 : 17, fontWeight: FontWeight.w800, color: _kNavy)),
                ),
              ),
              SizedBox(width: isNarrow ? 10 : 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(patient.name, style: GoogleFonts.rubik(fontSize: isNarrow ? 13 : 15, fontWeight: FontWeight.w600, color: const Color(0xFF111111)), overflow: TextOverflow.ellipsis),
                    if (patient.phone != null && patient.phone!.isNotEmpty)
                      Text(patient.phone!, style: GoogleFonts.rubik(fontSize: 12, color: _kMuted)),
                  ],
                ),
              ),
              if (!isNarrow && patient.allergies != null && patient.allergies!.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  margin: const EdgeInsets.only(left: 4),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    const Icon(Icons.warning_amber_rounded, size: 12, color: Colors.red),
                    const SizedBox(width: 4),
                    Text('patients.allergies'.tr(), style: GoogleFonts.rubik(fontSize: 10, fontWeight: FontWeight.w600, color: Colors.red)),
                  ]),
                ),
              const SizedBox(width: 4),
              IconButton(
                icon: Icon(Icons.delete_outline_rounded, size: 18, color: Colors.red.withValues(alpha: 0.5)),
                tooltip: 'מחק מטופל',
                padding: const EdgeInsets.all(6),
                constraints: const BoxConstraints(),
                onPressed: () => _showDeleteDialog(patient),
              ),
              Icon(Icons.chevron_left_rounded, color: _kNavy.withValues(alpha: 0.4), size: 20),
            ],
          ),
        ),
      ),
    );
  }

  // ── Empty / Error states ──
  Widget _buildEmptyState(String error, {required bool isError}) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(isError ? Icons.error_outline_rounded : Icons.people_outline_rounded, size: 56, color: _kNavy.withValues(alpha: 0.3)),
          const SizedBox(height: 16),
          Text(isError ? 'patients.load_error'.tr() : 'patients.empty'.tr(), style: GoogleFonts.rubik(fontSize: 16, fontWeight: FontWeight.w600, color: _kNavy)),
          const SizedBox(height: 6),
          Text(isError ? '' : 'patients.empty_hint'.tr(), style: GoogleFonts.rubik(fontSize: 13, color: _kMuted)),
          if (isError) ...[
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () => ref.read(patientsProvider.notifier).loadPatients(),
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: Text('common.retry'.tr()),
              style: OutlinedButton.styleFrom(foregroundColor: _kNavy, side: const BorderSide(color: _kNavy), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
            ),
          ],
        ],
      ),
    );
  }

  // ── Delete dialog ──
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
              ...['כל היסטוריית הביקורים', 'כל הסיכומים הרפואיים', 'כל ההקלטות והתמלולים', 'כל הקבצים המצורפים'].map((item) => Padding(
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
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text('ביטול', style: GoogleFonts.heebo(color: Colors.white60, fontWeight: FontWeight.w500))),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.accent, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))),
            onPressed: () async { Navigator.pop(ctx); await _deletePatient(patient); },
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
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('המטופל ${patient.name} נמחק בהצלחה', style: GoogleFonts.heebo()), backgroundColor: Colors.green.shade700));
        ref.read(patientsProvider.notifier).loadPatients();
      }
    } on DioException catch (e) {
      if (mounted) {
        final msg = e.response?.data?['message'] ?? 'שגיאה במחיקת המטופל';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg, style: GoogleFonts.heebo()), backgroundColor: Colors.red.shade700));
      }
    }
  }

  Future<void> _exportCsv() async {
    final patients = ref.read(patientsProvider).patients;
    if (patients.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('אין מטופלים לייצוא', style: GoogleFonts.heebo()), backgroundColor: Colors.orange.shade700));
      return;
    }
    final selected = await showDialog<List<int>?>(context: context, builder: (ctx) => _ExportDialog(patients: patients));
    if (selected == null) return;
    try {
      final queryParams = <String, dynamic>{};
      if (selected.isNotEmpty) queryParams['ids'] = selected.join(',');
      final dio = ApiClient().dio;
      final response = await dio.get('/patients/export/csv', queryParameters: queryParams, options: Options(responseType: ResponseType.bytes));
      final blob = html.Blob([response.data], 'text/csv');
      final url = html.Url.createObjectUrlFromBlob(blob);
      html.AnchorElement(href: url)..setAttribute('download', 'patients_export.csv')..click();
      html.Url.revokeObjectUrl(url);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('הקובץ הורד בהצלחה', style: GoogleFonts.heebo()), backgroundColor: Colors.green.shade700));
    } catch (_) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('שגיאה בייצוא', style: GoogleFonts.heebo()), backgroundColor: Colors.red.shade700));
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
              style: ElevatedButton.styleFrom(backgroundColor: _kNavy, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))),
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
      if (_selectAll) { _selected = widget.patients.map((p) => p.displayId).toSet(); } else { _selected.clear(); }
    });
  }

  void _toggle(int id) {
    setState(() {
      _selected.contains(id) ? _selected.remove(id) : _selected.add(id);
      _selectAll = _selected.length == widget.patients.length;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: _kCream,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        width: MediaQuery.of(context).size.width < 500 ? MediaQuery.of(context).size.width * 0.92 : 420,
        constraints: const BoxConstraints(maxHeight: 520),
        padding: const EdgeInsets.all(20),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Row(children: [
            const Icon(Icons.download_rounded, color: _kNavy, size: 24),
            const SizedBox(width: 10),
            Expanded(child: Text('ייצוא מטופלים ל-CSV', style: GoogleFonts.rubik(fontSize: 18, fontWeight: FontWeight.w700, color: _kNavy))),
          ]),
          const SizedBox(height: 6),
          Text('בחר מטופלים לייצוא כולל היסטוריית ביקורים', style: GoogleFonts.rubik(fontSize: 13, color: _kMuted)),
          const SizedBox(height: 14),
          InkWell(
            onTap: () => _toggleAll(!_selectAll),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(color: _kNavy.withValues(alpha: 0.06), borderRadius: BorderRadius.circular(8), border: Border.all(color: _kNavy.withValues(alpha: 0.2))),
              child: Row(children: [
                Checkbox(value: _selectAll, onChanged: _toggleAll, activeColor: _kNavy, checkColor: Colors.white),
                Text('כל המטופלים (${widget.patients.length})', style: GoogleFonts.rubik(fontSize: 14, fontWeight: FontWeight.w600, color: _kNavy)),
              ]),
            ),
          ),
          const SizedBox(height: 10),
          Flexible(
            child: Container(
              decoration: BoxDecoration(border: Border.all(color: _kInputBorder.withValues(alpha: 0.2)), borderRadius: BorderRadius.circular(10)),
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
                        border: Border(bottom: BorderSide(color: _kInputBorder.withValues(alpha: 0.1))),
                        color: isChecked ? _kNavy.withValues(alpha: 0.04) : Colors.transparent,
                      ),
                      child: Row(children: [
                        Checkbox(value: isChecked, onChanged: (_) => _toggle(p.displayId), activeColor: _kNavy, checkColor: Colors.white),
                        const SizedBox(width: 6),
                        Container(
                          width: 32, height: 32,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(colors: [Color(0xFFFFFFFF), Color(0xFFC8D8FF)]),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Center(child: Text(p.name.isNotEmpty ? p.name[0].toUpperCase() : '?', style: GoogleFonts.rubik(fontSize: 14, fontWeight: FontWeight.w700, color: _kNavy))),
                        ),
                        const SizedBox(width: 10),
                        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Text(p.name, style: GoogleFonts.rubik(fontSize: 13, fontWeight: FontWeight.w600, color: const Color(0xFF111111))),
                          if (p.phone != null && p.phone!.isNotEmpty) Text(p.phone!, style: GoogleFonts.rubik(fontSize: 11, color: _kMuted)),
                        ])),
                      ]),
                    ),
                  );
                },
              ),
            ),
          ),
          const SizedBox(height: 14),
          Row(mainAxisAlignment: MainAxisAlignment.end, children: [
            TextButton(onPressed: () => Navigator.pop(context, null), child: Text('ביטול', style: GoogleFonts.rubik(color: _kMuted))),
            const SizedBox(width: 10),
            ElevatedButton.icon(
              onPressed: _selected.isEmpty ? null : () { Navigator.pop(context, _selectAll ? <int>[] : _selected.toList()); },
              icon: const Icon(Icons.download_rounded, size: 18),
              label: Text(_selected.isEmpty ? 'בחר מטופלים' : 'ייצא ${_selectAll ? "הכל" : "${_selected.length} מטופלים"}', style: GoogleFonts.rubik(fontWeight: FontWeight.w700)),
              style: ElevatedButton.styleFrom(
                backgroundColor: _kNavy, foregroundColor: Colors.white,
                disabledBackgroundColor: _kMuted.withValues(alpha: 0.3),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              ),
            ),
          ]),
        ]),
      ),
    );
  }
}
