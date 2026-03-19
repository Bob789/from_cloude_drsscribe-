import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/providers/manual_note_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/widgets/manual_note/patient_selector.dart';
import 'package:medscribe_ai/widgets/manual_note/note_form_widgets.dart';
import 'package:medscribe_ai/widgets/manual_note/diagnoses_tags_section.dart';
import 'package:medscribe_ai/widgets/manual_note/custom_fields_section.dart';
import 'package:medscribe_ai/widgets/manual_note/questionnaire_section.dart';
import 'package:medscribe_ai/widgets/manual_note/note_success_view.dart';

// ── Shared design constants ──
const kCream = Color(0xFFFCF9C6);
const kNavy = Color(0xFF003399);
const kNavyLight = Color(0xFF1A56DB);
const kGold = Color(0xFFC8A000);
const kHeaderGrad1 = Color(0xFF2D3A4A);
const kHeaderGrad2 = Color(0xFF5A6A5A);
const kInputBorder = Color(0xFF1A56DB);
const kMutedText = Color(0xFF8899AA);

class ManualNoteScreen extends ConsumerStatefulWidget {
  final String? visitId;
  const ManualNoteScreen({super.key, this.visitId});

  @override
  ConsumerState<ManualNoteScreen> createState() => _ManualNoteScreenState();
}

class _ManualNoteScreenState extends ConsumerState<ManualNoteScreen> {
  final _chiefComplaintCtrl = TextEditingController();
  final _findingsCtrl = TextEditingController();
  final _treatmentCtrl = TextEditingController();
  final _recommendationsCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();
  final _patientSelectorKey = GlobalKey<PatientSelectorState>();
  final _questionnaireKey = GlobalKey<QuestionnaireSectionState>();

  String _urgency = 'low';
  List<Map<String, dynamic>> _questionnaireData = [];
  String? _selectedPatientId;
  int _resetKey = 0;

  @override
  void initState() {
    super.initState();
    Future(() async {
      ref.read(manualNoteProvider.notifier).reset();
      await ref.read(manualNoteProvider.notifier).loadCustomFields();
    });
  }

  @override
  void dispose() {
    _chiefComplaintCtrl.dispose();
    _findingsCtrl.dispose();
    _treatmentCtrl.dispose();
    _recommendationsCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (_selectedPatientId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('manual_note.select_patient'.tr(), style: GoogleFonts.heebo()), backgroundColor: AppColors.accent),
      );
      return;
    }
    await ref.read(manualNoteProvider.notifier).save(
      patientId: _selectedPatientId!,
      chiefComplaint: _chiefComplaintCtrl.text,
      findings: _findingsCtrl.text,
      treatmentPlan: _treatmentCtrl.text,
      recommendations: _recommendationsCtrl.text,
      urgency: _urgency,
      notes: _notesCtrl.text,
      questionnaireData: _questionnaireData.isNotEmpty ? _questionnaireData : null,
    );
  }

  void _resetForm() {
    ref.read(manualNoteProvider.notifier).reset();
    _patientSelectorKey.currentState?.reset();
    _questionnaireKey.currentState?.reset();
    setState(() {
      _chiefComplaintCtrl.clear();
      _findingsCtrl.clear();
      _treatmentCtrl.clear();
      _recommendationsCtrl.clear();
      _notesCtrl.clear();
      _selectedPatientId = null;
      _urgency = 'low';
      _questionnaireData = [];
      _resetKey++;
    });
  }

  @override
  Widget build(BuildContext context) {
    final noteState = ref.watch(manualNoteProvider);
    final isNarrow = MediaQuery.of(context).size.width < 600;
    final hPad = isNarrow ? 12.0 : 20.0;

    if (noteState.isSaved) {
      return NoteSuccessView(onNewNote: _resetForm, onGoToPatients: () => context.go('/patients'));
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0A1628),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 820),
          child: Column(
            children: [
              // ── Header bar ──
              Container(
                width: double.infinity,
                padding: EdgeInsets.symmetric(horizontal: isNarrow ? 14 : 24, vertical: 14),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(colors: [kHeaderGrad1, kHeaderGrad2]),
                  border: Border(bottom: BorderSide(color: kGold, width: 2)),
                ),
                child: Row(children: [
                  InkWell(
                    onTap: () => context.go('/patients'),
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
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('manual_note.title'.tr(), style: GoogleFonts.rubik(fontSize: isNarrow ? 18 : 22, fontWeight: FontWeight.w800, color: Colors.white)),
                    Text('manual_note.subtitle'.tr(), style: GoogleFonts.rubik(fontSize: 12, color: Colors.white70)),
                  ])),
                ]),
              ),
              // ── Red title lines ──
              Container(
                color: kCream,
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
                  color: kCream,
                  child: SingleChildScrollView(
                    padding: EdgeInsets.symmetric(horizontal: hPad, vertical: 4),
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      // Patient selector
                      _sectionTitle('manual_note.select_patient'.tr()),
                      PatientSelector(
                        key: _patientSelectorKey,
                        onSelected: (id, name) => _selectedPatientId = id,
                        onCleared: () => _selectedPatientId = null,
                      ),
                      _pipeDivider(),

                      // Urgency
                      _sectionTitle('visit.urgency_label'.tr()),
                      UrgencySelector(value: _urgency, onChanged: (v) => setState(() => _urgency = v)),
                      _pipeDivider(),

                      // Questionnaire
                      QuestionnaireSection(key: _questionnaireKey, onChanged: (data) => _questionnaireData = data),
                      _pipeDivider(),

                      // Chief complaint
                      _sectionTitle('manual_note.chief_complaint'.tr()),
                      _noteField(_chiefComplaintCtrl, 3),
                      _pipeDivider(),

                      // Findings
                      _sectionTitle('manual_note.findings'.tr()),
                      _noteField(_findingsCtrl, 5),
                      _pipeDivider(),

                      // Diagnoses
                      const DiagnosesSection(),
                      _pipeDivider(),

                      // Treatment plan
                      _sectionTitle('manual_note.treatment_plan'.tr()),
                      _noteField(_treatmentCtrl, 5),
                      _pipeDivider(),

                      // Recommendations
                      _sectionTitle('manual_note.recommendations'.tr()),
                      _noteField(_recommendationsCtrl, 3),
                      _pipeDivider(),

                      // Notes
                      _sectionTitle('manual_note.notes'.tr()),
                      _noteField(_notesCtrl, 4),
                      _pipeDivider(),

                      // Custom fields
                      CustomFieldsSection(key: ValueKey(_resetKey)),
                      _pipeDivider(),

                      // Tags
                      const TagsSection(),
                      _pipeDivider(),

                      // Error
                      if (noteState.error != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 16),
                          child: Text(noteState.error!, style: GoogleFonts.heebo(color: Colors.red, fontSize: 13)),
                        ),

                      // Save button
                      const SizedBox(height: 8),
                      SizedBox(
                        width: double.infinity,
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            onTap: noteState.isLoading ? null : _save,
                            borderRadius: BorderRadius.circular(10),
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 15),
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(colors: [kNavyLight, kNavy]),
                                borderRadius: BorderRadius.circular(10),
                                boxShadow: [BoxShadow(color: kNavyLight.withValues(alpha: 0.3), blurRadius: 20)],
                              ),
                              child: Center(
                                child: noteState.isLoading
                                    ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                    : Row(mainAxisSize: MainAxisSize.min, children: [
                                        const Icon(Icons.save_rounded, color: Colors.white, size: 18),
                                        const SizedBox(width: 8),
                                        Text('common.save'.tr(), style: GoogleFonts.rubik(fontSize: 16, fontWeight: FontWeight.w800, color: Colors.white)),
                                      ]),
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                    ]),
                  ),
                ),
              ),
              // ── Footer ──
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(colors: [kHeaderGrad1, kHeaderGrad2]),
                  border: Border(top: BorderSide(color: kGold, width: 2)),
                ),
                child: Text('Doctor Scribe AI — פרטי קשר | תמיכה | הגדרות', textAlign: TextAlign.center, style: GoogleFonts.rubik(fontSize: 12, color: Colors.white)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 4),
      child: Text(text, style: GoogleFonts.rubik(fontSize: 20, fontWeight: FontWeight.w800, color: kNavy)),
    );
  }

  Widget _noteField(TextEditingController ctrl, int maxLines) {
    return TextField(
      controller: ctrl,
      maxLines: maxLines,
      style: GoogleFonts.heebo(color: const Color(0xFF111111), fontSize: 14, height: 1.6),
      decoration: InputDecoration(
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.65),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kInputBorder)),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: kNavy, width: 1.5)),
        contentPadding: const EdgeInsets.all(12),
      ),
    );
  }

  Widget _pipeDivider() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          Container(
            width: 18, height: 12,
            decoration: BoxDecoration(
              border: Border.all(color: kNavyLight, width: 2),
              borderRadius: const BorderRadius.only(topRight: Radius.circular(50), bottomRight: Radius.circular(50)),
            ),
          ),
          Expanded(child: Column(children: [
            Container(height: 2, color: kNavyLight),
            const SizedBox(height: 4),
            Container(height: 2, color: kNavyLight),
          ])),
          Container(
            width: 18, height: 12,
            decoration: BoxDecoration(
              border: Border.all(color: kNavyLight, width: 2),
              borderRadius: const BorderRadius.only(topLeft: Radius.circular(50), bottomLeft: Radius.circular(50)),
            ),
          ),
        ],
      ),
    );
  }
}
