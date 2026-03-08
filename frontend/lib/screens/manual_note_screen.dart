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

    if (noteState.isSaved) {
      return NoteSuccessView(onNewNote: _resetForm, onGoToPatients: () => context.go('/patients'));
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _buildHeader(),
              const SizedBox(height: 24),
              PatientSelector(
                key: _patientSelectorKey,
                onSelected: (id, name) => _selectedPatientId = id,
                onCleared: () => _selectedPatientId = null,
              ),
              const SizedBox(height: 20),
              UrgencySelector(value: _urgency, onChanged: (v) => setState(() => _urgency = v)),
              const SizedBox(height: 20),
              QuestionnaireSection(
                key: _questionnaireKey,
                onChanged: (data) => _questionnaireData = data,
              ),
              const SizedBox(height: 16),
              NoteTextField(label: 'manual_note.chief_complaint'.tr(), controller: _chiefComplaintCtrl, maxLines: 3),
              const SizedBox(height: 16),
              NoteTextField(label: 'manual_note.findings'.tr(), controller: _findingsCtrl, maxLines: 5),
              const SizedBox(height: 16),
              const DiagnosesSection(),
              const SizedBox(height: 16),
              NoteTextField(label: 'manual_note.treatment_plan'.tr(), controller: _treatmentCtrl, maxLines: 5),
              const SizedBox(height: 16),
              NoteTextField(label: 'manual_note.recommendations'.tr(), controller: _recommendationsCtrl, maxLines: 3),
              const SizedBox(height: 16),
              NoteTextField(label: 'manual_note.notes'.tr(), controller: _notesCtrl, maxLines: 4),
              const SizedBox(height: 16),
              CustomFieldsSection(key: ValueKey(_resetKey)),
              const SizedBox(height: 16),
              const TagsSection(),
              const SizedBox(height: 24),
              if (noteState.error != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Text(noteState.error!, style: GoogleFonts.heebo(color: AppColors.accent, fontSize: 13)),
                ),
              NoteSaveButton(isLoading: noteState.isLoading, onPressed: _save),
              const SizedBox(height: 40),
            ]),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(children: [
      IconButton(
        onPressed: () => context.go('/patients'),
        icon: Icon(Icons.arrow_forward_rounded, color: AppColors.textSecondary),
        style: IconButton.styleFrom(backgroundColor: AppColors.card, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10))),
      ),
      const SizedBox(width: 14),
      Expanded(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('manual_note.title'.tr(), style: GoogleFonts.heebo(fontSize: 24, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
          Text('manual_note.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
        ]),
      ),
    ]);
  }
}
