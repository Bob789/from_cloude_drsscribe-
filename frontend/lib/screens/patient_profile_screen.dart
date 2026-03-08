import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/models/visit_model.dart';
import 'package:medscribe_ai/models/appointment_model.dart';
import 'package:medscribe_ai/models/tag_model.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/widgets/edit_visit_dialog.dart';
import 'package:medscribe_ai/providers/patient_files_provider.dart';
import 'package:medscribe_ai/widgets/profile/patient_header.dart';
import 'package:medscribe_ai/widgets/profile/patient_info_card.dart';
import 'package:medscribe_ai/widgets/profile/visit_card.dart';
import 'package:medscribe_ai/widgets/profile/files_section.dart';

class PatientProfileScreen extends ConsumerStatefulWidget {
  final String patientId;
  const PatientProfileScreen({super.key, required this.patientId});

  @override
  ConsumerState<PatientProfileScreen> createState() => _PatientProfileScreenState();
}

class _PatientProfileScreenState extends ConsumerState<PatientProfileScreen> {
  Map<String, dynamic>? _patient;
  List<VisitModel> _visits = [];
  List<AppointmentModel> _appointments = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final dioClient = ApiClient().dio;
      final responses = await Future.wait([
        dioClient.get('/patients/${widget.patientId}'),
        dioClient.get('/visits/patient/${widget.patientId}'),
      ]);
      List<AppointmentModel> appts = [];
      try {
        final apptRes = await dioClient.get('/appointments/patient/${widget.patientId}');
        appts = (apptRes.data as List).map((a) => AppointmentModel.fromJson(a)).toList();
      } catch (_) {}
      setState(() {
        _patient = responses[0].data;
        _visits = (responses[1].data as List).map((v) => VisitModel.fromJson(v)).toList();
        _appointments = appts;
        _isLoading = false;
      });
      ref.read(patientFilesProvider.notifier).loadFiles(widget.patientId);
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _deleteTag(String tagId) async {
    try {
      await ApiClient().dio.delete('/tags/$tagId');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('common.tag_deleted'.tr(), style: GoogleFonts.heebo()), backgroundColor: AppColors.secondary),
        );
        setState(() => _isLoading = true);
        await _load();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('common.tag_delete_error'.tr(), style: GoogleFonts.heebo()), backgroundColor: AppColors.accent),
        );
      }
    }
  }

  Future<void> _editTag(String tagId, TagModel tag) async {
    final labelCtrl = TextEditingController(text: tag.tagLabel);
    final codeCtrl = TextEditingController(text: tag.tagCode);
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.card,
        title: Text('profile.edit_tag'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: labelCtrl, style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textPrimary), decoration: InputDecoration(labelText: 'profile.tag_name'.tr(), labelStyle: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted))),
          const SizedBox(height: 12),
          TextField(controller: codeCtrl, style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textPrimary), decoration: InputDecoration(labelText: 'profile.tag_code'.tr(), labelStyle: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted))),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text('common.cancel'.tr(), style: GoogleFonts.heebo())),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text('common.save'.tr(), style: GoogleFonts.heebo())),
        ],
      ),
    );
    if (result == true) {
      try {
        await ApiClient().dio.put('/tags/$tagId', data: {'tag_label': labelCtrl.text, 'tag_code': codeCtrl.text});
        if (mounted) { setState(() => _isLoading = true); await _load(); }
      } catch (_) {}
    }
    labelCtrl.dispose();
    codeCtrl.dispose();
  }

  Future<void> _editVisit(String visitId, VisitModel visit) async {
    final result = await showEditVisitDialog(context, visitId, visit.toMap());
    if (result && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('profile.visit_updated'.tr(), style: GoogleFonts.heebo()), backgroundColor: AppColors.secondary));
      setState(() => _isLoading = true);
      await _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(backgroundColor: AppColors.background, body: Center(child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5)));
    }
    if (_patient == null) {
      return Scaffold(
        backgroundColor: AppColors.background,
        body: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(Icons.person_off_rounded, size: 48, color: AppColors.textMuted.withValues(alpha: 0.4)),
          const SizedBox(height: 16),
          Text('profile.patient_not_found'.tr(), style: GoogleFonts.heebo(fontSize: 16, color: AppColors.textSecondary)),
        ])),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          PatientHeader(patient: _patient!, patientId: widget.patientId),
          const SizedBox(height: 20),
          PatientInfoCard(patient: _patient!),
          const SizedBox(height: 20),
          _buildAppointmentsSection(),
          const SizedBox(height: 20),
          _buildVisitsSection(),
          const SizedBox(height: 24),
          FilesSection(patientId: widget.patientId),
        ]),
      ),
    );
  }

  Widget _buildAppointmentsSection() {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final now = DateTime.now();
    final upcoming = _appointments.where((a) => a.startTime.isAfter(now)).toList()..sort((a, b) => a.startTime.compareTo(b.startTime));
    final past = _appointments.where((a) => !a.startTime.isAfter(now)).toList();

    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Icon(Icons.calendar_month_rounded, size: 20, color: AppColors.primary),
        const SizedBox(width: 8),
        Text('profile.appointments'.tr(), style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(width: 10),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8)),
          child: Text('${_appointments.length}', style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primary)),
        ),
      ]),
      const SizedBox(height: 14),
      if (_appointments.isEmpty)
        Container(
          width: double.infinity, padding: const EdgeInsets.all(32), decoration: ext.cardDecoration,
          child: Column(children: [
            Icon(Icons.event_busy_rounded, size: 40, color: AppColors.textMuted.withValues(alpha: 0.3)),
            const SizedBox(height: 12),
            Text('profile.no_appointments'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
          ]),
        )
      else
        Container(
          width: double.infinity, padding: const EdgeInsets.all(16), decoration: ext.cardDecoration,
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            if (upcoming.isNotEmpty) ...[
              Text('profile.upcoming_appointments'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.success)),
              const SizedBox(height: 8),
              ...upcoming.map((a) => _buildAppointmentRow(a, isUpcoming: true)),
            ],
            if (upcoming.isNotEmpty && past.isNotEmpty)
              Padding(padding: const EdgeInsets.symmetric(vertical: 10), child: Divider(color: AppColors.cardBorder, height: 1)),
            if (past.isNotEmpty) ...[
              Text('profile.past_appointments'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textMuted)),
              const SizedBox(height: 8),
              ...past.map((a) => _buildAppointmentRow(a, isUpcoming: false)),
            ],
          ]),
        ),
    ]);
  }

  Widget _buildAppointmentRow(AppointmentModel appt, {required bool isUpcoming}) {
    final d = appt.startTime;
    final date = DateFormat('d MMMM yyyy', context.locale.toString()).format(d);
    final time = '${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
    final statusColor = switch (appt.status) {
      'completed' => AppColors.success,
      'cancelled' => Colors.red,
      'no_show' => AppColors.warning,
      _ => isUpcoming ? AppColors.primary : AppColors.textMuted,
    };
    final statusLabel = switch (appt.status) {
      'completed' => 'status.completed'.tr(),
      'cancelled' => 'status.cancelled'.tr(),
      'no_show' => 'status.no_show'.tr(),
      _ => 'status.scheduled'.tr(),
    };

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(children: [
        Container(width: 4, height: 36, decoration: BoxDecoration(color: statusColor, borderRadius: BorderRadius.circular(2))),
        const SizedBox(width: 12),
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(date, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
          Text(time, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
        ]),
        const SizedBox(width: 16),
        Expanded(child: Text(appt.title, style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary))),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(color: statusColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6)),
          child: Text(statusLabel, style: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w600, color: statusColor)),
        ),
        if (appt.syncedToGoogle)
          Padding(padding: const EdgeInsets.only(right: 8), child: Icon(Icons.event, size: 16, color: AppColors.textMuted)),
      ]),
    );
  }

  Widget _buildVisitsSection() {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Text('profile.visits_history'.tr(), style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(width: 10),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8)),
          child: Text('${_visits.length}', style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primary)),
        ),
      ]),
      const SizedBox(height: 14),
      if (_visits.isEmpty)
        Container(
          width: double.infinity, padding: const EdgeInsets.all(32), decoration: ext.cardDecoration,
          child: Column(children: [
            Icon(Icons.event_note_rounded, size: 40, color: AppColors.textMuted.withValues(alpha: 0.3)),
            const SizedBox(height: 12),
            Text('profile.no_visits'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
          ]),
        )
      else
        ..._visits.map((visit) => VisitCard(
          visit: visit,
          onDeleteTag: _deleteTag,
          onEditTag: _editTag,
          onEditVisit: _editVisit,
        )),
    ]);
  }
}
