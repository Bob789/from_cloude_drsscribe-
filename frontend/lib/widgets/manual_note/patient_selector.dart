import 'dart:async';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class PatientSelector extends StatefulWidget {
  final void Function(String id, String name) onSelected;
  final VoidCallback onCleared;

  const PatientSelector({super.key, required this.onSelected, required this.onCleared});

  @override
  State<PatientSelector> createState() => PatientSelectorState();
}

class PatientSelectorState extends State<PatientSelector> {
  final _ctrl = TextEditingController();
  String? _selectedId;
  String? _selectedName;
  List<PatientModel> _results = [];
  Timer? _debounce;

  @override
  void dispose() {
    _ctrl.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void reset() {
    _ctrl.clear();
    setState(() { _selectedId = null; _selectedName = null; _results = []; });
  }

  void _search(String query) {
    _debounce?.cancel();
    if (query.trim().isEmpty) { setState(() => _results = []); return; }
    _debounce = Timer(const Duration(milliseconds: 250), () async {
      try {
        final response = await ApiClient().dio.get('/patients/search', queryParameters: {'q': query.trim()});
        if (mounted) setState(() => _results = (response.data as List).map((e) => PatientModel.fromJson(e)).toList());
      } catch (_) {}
    });
  }

  void _select(PatientModel p) {
    setState(() { _selectedId = p.id; _selectedName = p.name; _ctrl.text = p.name; _results = []; });
    widget.onSelected(p.id, p.name);
  }

  void _clear() {
    _ctrl.clear();
    setState(() { _selectedId = null; _selectedName = null; _results = []; });
    widget.onCleared();
  }

  @override
  Widget build(BuildContext context) {
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;
    final hasQuery = _ctrl.text.trim().isNotEmpty && _selectedId == null;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('search.patient_label'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
        const SizedBox(height: 10),
        TextField(
          controller: _ctrl,
          style: GoogleFonts.heebo(color: AppColors.textPrimary, fontSize: 14),
          decoration: InputDecoration(
            hintText: 'recording.patient_search_hint'.tr(),
            prefixIcon: Icon(Icons.person_search_rounded, color: AppColors.textMuted, size: 20),
            suffixIcon: _selectedId != null ? IconButton(icon: Icon(Icons.close_rounded, size: 18, color: AppColors.textMuted), onPressed: _clear) : null,
            filled: true, fillColor: AppColors.background,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.cardBorder)),
            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.cardBorder)),
            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          ),
          readOnly: _selectedId != null,
          onChanged: _search,
        ),
        if (hasQuery && _results.isNotEmpty) ...[
          const SizedBox(height: 8),
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            decoration: BoxDecoration(color: AppColors.card, borderRadius: BorderRadius.circular(10), border: Border.all(color: AppColors.cardBorder)),
            child: ListView.separated(
              shrinkWrap: true, padding: const EdgeInsets.symmetric(vertical: 4),
              itemCount: _results.length,
              separatorBuilder: (_, __) => Divider(height: 1, color: AppColors.cardBorder),
              itemBuilder: (context, index) {
                final p = _results[index];
                return ListTile(
                  dense: true,
                  title: Text(p.name, style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                  subtitle: p.phone != null ? Text(p.phone!, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)) : null,
                  onTap: () => _select(p),
                );
              },
            ),
          ),
        ],
        if (_selectedId != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Row(children: [
              Icon(Icons.check_circle_rounded, size: 16, color: AppColors.secondary),
              const SizedBox(width: 6),
              Text('appointments.selected_patient'.tr(namedArgs: {'name': _selectedName!}), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.secondary, fontWeight: FontWeight.w500)),
            ]),
          ),
      ]),
    );
  }
}
