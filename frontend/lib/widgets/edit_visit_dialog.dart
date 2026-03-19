import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/utils/app_theme.dart';

Future<bool> showEditVisitDialog(BuildContext context, String visitId, Map<String, dynamic> visitData) async {
  final result = await showDialog<bool>(context: context, builder: (context) => _EditVisitDialog(visitId: visitId, visitData: visitData));
  return result ?? false;
}

class _EditVisitDialog extends StatefulWidget {
  final String visitId;
  final Map<String, dynamic> visitData;
  const _EditVisitDialog({required this.visitId, required this.visitData});

  @override
  State<_EditVisitDialog> createState() => _EditVisitDialogState();
}

class _EditVisitDialogState extends State<_EditVisitDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _chiefComplaintCtrl;
  late final TextEditingController _findingsCtrl;
  late final TextEditingController _treatmentCtrl;
  late final TextEditingController _recommendationsCtrl;
  late final TextEditingController _diagnosisCtrl;
  String? _urgency;
  String? _status;
  bool _isLoading = false;

  Map<String, String> get _urgencyOptions => {
    'low': 'urgency.low'.tr(),
    'medium': 'urgency.medium'.tr(),
    'high': 'urgency.high'.tr(),
  };

  Map<String, String> get _statusOptions => {
    'scheduled': 'status.scheduled'.tr(),
    'in_progress': 'status.in_progress'.tr(),
    'completed': 'status.completed'.tr(),
    'cancelled': 'status.cancelled'.tr(),
  };

  @override
  void initState() {
    super.initState();
    final summary = widget.visitData['summary'] as Map<String, dynamic>?;
    _chiefComplaintCtrl = TextEditingController(text: summary?['chief_complaint'] ?? '');
    _findingsCtrl = TextEditingController(text: summary?['findings'] ?? '');
    _treatmentCtrl = TextEditingController(text: summary?['treatment_plan'] ?? '');
    _recommendationsCtrl = TextEditingController(text: summary?['recommendations'] ?? '');
    final diagnosis = summary?['diagnosis'];
    String diagnosisText = '';
    if (diagnosis is List && diagnosis.isNotEmpty) {
      diagnosisText = diagnosis.map((d) => d is Map ? '${d['code'] ?? ''} - ${d['description'] ?? d['label'] ?? ''}' : d.toString()).join('\n');
    }
    _diagnosisCtrl = TextEditingController(text: diagnosisText);
    _urgency = summary?['urgency'] ?? 'low';
    _status = widget.visitData['status'] ?? 'completed';
  }

  @override
  void dispose() {
    _chiefComplaintCtrl.dispose();
    _findingsCtrl.dispose();
    _treatmentCtrl.dispose();
    _recommendationsCtrl.dispose();
    _diagnosisCtrl.dispose();
    super.dispose();
  }

  InputDecoration _decoration(String label, {String? hint}) {
    return InputDecoration(
      labelText: label, hintText: hint,
      hintStyle: hint != null ? GoogleFonts.heebo(color: AppColors.textMuted.withValues(alpha: 0.5), fontSize: 12) : null,
      labelStyle: GoogleFonts.heebo(color: AppColors.textMuted),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.cardBorder)),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.primary)),
    );
  }

  final _textStyle = GoogleFonts.heebo(color: AppColors.textPrimary);

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      final summary = widget.visitData['summary'] as Map<String, dynamic>?;
      final data = <String, dynamic>{};
      void addIfChanged(String key, String val, String? orig) { if (val != (orig ?? '')) data[key] = val; }
      addIfChanged('chief_complaint', _chiefComplaintCtrl.text, summary?['chief_complaint']);
      addIfChanged('findings', _findingsCtrl.text, summary?['findings']);
      addIfChanged('treatment_plan', _treatmentCtrl.text, summary?['treatment_plan']);
      addIfChanged('recommendations', _recommendationsCtrl.text, summary?['recommendations']);

      final currentDiag = _diagnosisCtrl.text.trim();
      final origDiag = summary?['diagnosis'];
      String origDiagText = '';
      if (origDiag is List && origDiag.isNotEmpty) {
        origDiagText = origDiag.map((d) => d is Map ? '${d['code'] ?? ''} - ${d['description'] ?? d['label'] ?? ''}' : d.toString()).join('\n').trim();
      }
      if (currentDiag != origDiagText) {
        if (currentDiag.isEmpty) {
          data['diagnosis'] = [];
        } else {
          data['diagnosis'] = currentDiag.split('\n').where((l) => l.trim().isNotEmpty).map((line) {
            final parts = line.split(' - ');
            if (parts.length >= 2) {
              return {'code': parts[0].trim(), 'description': parts.sublist(1).join(' - ').trim()};
            }
            return {'code': '', 'description': line.trim()};
          }).toList();
        }
      }
      if (_urgency != (summary?['urgency'] ?? 'low')) data['urgency'] = _urgency;
      if (_status != widget.visitData['status']) data['status'] = _status;

      if (data.isEmpty) { if (mounted) Navigator.of(context).pop(false); return; }
      await ApiClient().dio.put('/visits/${widget.visitId}', data: data);
      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('common.update_error'.tr(), style: GoogleFonts.heebo()), backgroundColor: AppColors.accent));
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: AlertDialog(
        backgroundColor: AppColors.card,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('visit.edit_title'.tr(), style: GoogleFonts.heebo(fontSize: 20, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        content: Container(
          width: MediaQuery.of(context).size.width * 0.9,
          constraints: BoxConstraints(maxHeight: MediaQuery.of(context).size.height * 0.7),
          child: SingleChildScrollView(
            child: Form(
              key: _formKey,
              child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, mainAxisSize: MainAxisSize.min, children: [
                TextFormField(controller: _chiefComplaintCtrl, decoration: _decoration('visit.chief_complaint'.tr()), style: _textStyle),
                const SizedBox(height: 16),
                TextFormField(controller: _findingsCtrl, decoration: _decoration('visit.findings'.tr()), style: _textStyle, maxLines: 3),
                const SizedBox(height: 16),
                TextFormField(controller: _diagnosisCtrl, decoration: _decoration('visit.diagnosis'.tr(), hint: 'visit.diagnosis_hint'.tr()), style: _textStyle, maxLines: 3),
                const SizedBox(height: 16),
                TextFormField(controller: _treatmentCtrl, decoration: _decoration('visit.treatment_plan'.tr()), style: _textStyle, maxLines: 3),
                const SizedBox(height: 16),
                TextFormField(controller: _recommendationsCtrl, decoration: _decoration('visit.recommendations'.tr()), style: _textStyle, maxLines: 3),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _urgency,
                  decoration: _decoration('visit.urgency_label'.tr()),
                  style: _textStyle, dropdownColor: AppColors.card,
                  items: _urgencyOptions.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value, style: _textStyle))).toList(),
                  onChanged: (v) => setState(() => _urgency = v),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _status,
                  decoration: _decoration('visit.status_label'.tr()),
                  style: _textStyle, dropdownColor: AppColors.card,
                  items: _statusOptions.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value, style: _textStyle))).toList(),
                  onChanged: (v) => setState(() => _status = v),
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : () => Navigator.of(context).pop(false),
            child: Text('common.cancel'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w500, color: _isLoading ? AppColors.textMuted.withValues(alpha: 0.5) : AppColors.textMuted)),
          ),
          ElevatedButton(
            onPressed: _isLoading ? null : _submit,
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)), padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12)),
            child: _isLoading
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, valueColor: AlwaysStoppedAnimation<Color>(Colors.white)))
                : Text('common.save'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }
}
