import 'dart:async';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/screens/manual_note_screen.dart';

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
    final hasQuery = _ctrl.text.trim().isNotEmpty && _selectedId == null;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      TextField(
        controller: _ctrl,
        style: GoogleFonts.heebo(color: const Color(0xFF111111), fontSize: 14),
        decoration: InputDecoration(
          hintText: 'recording.patient_search_hint'.tr(),
          hintStyle: GoogleFonts.heebo(color: kMutedText),
          prefixIcon: const Icon(Icons.person_search_rounded, color: kMutedText, size: 20),
          suffixIcon: _selectedId != null ? IconButton(icon: const Icon(Icons.close_rounded, size: 18, color: kMutedText), onPressed: _clear) : null,
          filled: true,
          fillColor: Colors.white.withValues(alpha: 0.65),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kNavy, width: 1.5)),
          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        ),
        readOnly: _selectedId != null,
        onChanged: _search,
      ),
      if (hasQuery && _results.isNotEmpty) ...[
        const SizedBox(height: 6),
        Container(
          constraints: const BoxConstraints(maxHeight: 180),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8), border: Border.all(color: kInputBorder)),
          child: ListView.separated(
            shrinkWrap: true, padding: const EdgeInsets.symmetric(vertical: 4),
            itemCount: _results.length,
            separatorBuilder: (_, __) => const Divider(height: 1, color: Color(0xFFE5E7EB)),
            itemBuilder: (context, index) {
              final p = _results[index];
              return ListTile(
                dense: true,
                title: Text(p.name, style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w700, color: const Color(0xFF111111))),
                subtitle: p.phone != null ? Text(p.phone!, style: GoogleFonts.heebo(fontSize: 12, color: kMutedText)) : null,
                onTap: () => _select(p),
                hoverColor: const Color(0xFFF0F4FF),
              );
            },
          ),
        ),
      ],
      if (_selectedId != null)
        Padding(
          padding: const EdgeInsets.only(top: 6),
          child: Row(children: [
            const Icon(Icons.check_circle_rounded, size: 16, color: Color(0xFF16A34A)),
            const SizedBox(width: 6),
            Text('appointments.selected_patient'.tr(namedArgs: {'name': _selectedName!}), style: GoogleFonts.heebo(fontSize: 13, color: const Color(0xFF16A34A), fontWeight: FontWeight.w500)),
          ]),
        ),
    ]);
  }
}
