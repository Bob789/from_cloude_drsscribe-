import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/providers/recording_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';
import 'package:medscribe_ai/widgets/audio_recorder.dart';
import 'package:medscribe_ai/widgets/treatment_timer.dart';

class RecordingScreen extends ConsumerStatefulWidget {
  const RecordingScreen({super.key});

  @override
  ConsumerState<RecordingScreen> createState() => _RecordingScreenState();
}

class _RecordingScreenState extends ConsumerState<RecordingScreen> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final recordingState = ref.watch(recordingProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const SizedBox(height: 24),
            Expanded(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 560),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (recordingState.selectedPatientId == null)
                        Expanded(child: _buildPatientSelector(recordingState, ext))
                      else if (recordingState.isComplete)
                        _buildComplete(recordingState, ext)
                      else ...[
                        _buildRecorder(context, recordingState, ext),
                        const SizedBox(height: 16),
                        const TreatmentTimer(compact: true),
                      ],
                      if (recordingState.error != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                            decoration: BoxDecoration(
                              color: AppColors.accent.withValues(alpha: 0.08),
                              borderRadius: BorderRadius.circular(ext.cardRadius),
                              border: Border.all(color: AppColors.accent.withValues(alpha: 0.2)),
                            ),
                            child: Row(
                              children: [
                                Icon(Icons.error_outline_rounded, size: 18, color: AppColors.accent),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Text(recordingState.error!, style: GoogleFonts.heebo(fontSize: 13, color: AppColors.accent)),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('recording.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
        const SizedBox(height: 4),
        Text('recording.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
      ],
    );
  }

  Widget _buildPatientSelector(RecordingState recordingState, MedScribeThemeExtension ext) {
    final results = recordingState.searchResults;
    final hasQuery = _searchController.text.trim().isNotEmpty;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(28),
          decoration: ext.cardDecoration,
          child: Column(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: ext.iconContainer(AppColors.primary),
                child: Icon(Icons.person_search_rounded, size: 28, color: AppColors.primary),
              ),
              const SizedBox(height: 16),
              Text('recording.select_patient'.tr(), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
              const SizedBox(height: 6),
              Text('recording.search_hint'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
              const SizedBox(height: 20),
              TextField(
                controller: _searchController,
                style: GoogleFonts.heebo(color: AppColors.textPrimary, fontSize: 14),
                decoration: InputDecoration(
                  hintText: 'recording.patient_search_hint'.tr(),
                  prefixIcon: Icon(Icons.search_rounded, color: AppColors.textMuted, size: 20),
                  suffixIcon: hasQuery
                      ? IconButton(
                          icon: Icon(Icons.close_rounded, size: 18, color: AppColors.textMuted),
                          onPressed: () {
                            _searchController.clear();
                            ref.read(recordingProvider.notifier).searchPatient('');
                          },
                        )
                      : null,
                  filled: true,
                  fillColor: AppColors.background,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.cardBorder)),
                  enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.cardBorder)),
                  focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                ),
                onChanged: (v) {
                  setState(() {});
                  ref.read(recordingProvider.notifier).searchPatient(v);
                },
              ),
            ],
          ),
        ),
        if (hasQuery && !recordingState.isSearching && results.isNotEmpty) ...[
          const SizedBox(height: 8),
          Flexible(
            child: Container(
              constraints: const BoxConstraints(maxHeight: 320),
              decoration: ext.cardDecoration,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(ext.cardRadius),
                child: ListView.separated(
                  shrinkWrap: true,
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  itemCount: results.length,
                  separatorBuilder: (_, __) => Divider(height: 1, color: AppColors.cardBorder),
                  itemBuilder: (context, index) => _buildPatientItem(results[index], ext),
                ),
              ),
            ),
          ),
        ],
        if (hasQuery && !recordingState.isSearching && results.isEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Text('recording.no_patients'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted)),
          ),
        if (recordingState.isSearching)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary)),
          ),
      ],
    );
  }

  Widget _buildPatientItem(PatientModel patient, MedScribeThemeExtension ext) {
    final initials = patient.name.isNotEmpty ? patient.name[0].toUpperCase() : '?';

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          ref.read(recordingProvider.notifier).selectPatient(patient.id, patient.name);
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppColors.primary.withValues(alpha: 0.2), AppColors.secondary.withValues(alpha: 0.1)],
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Center(
                  child: Text(initials, style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.primary)),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(patient.name, style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                    if (patient.phone != null && patient.phone!.isNotEmpty)
                      Text(patient.phone!, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.textMuted)),
                  ],
                ),
              ),
              Icon(Icons.chevron_left_rounded, size: 20, color: AppColors.textMuted),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecorder(BuildContext context, RecordingState recordingState, MedScribeThemeExtension ext) {
    return Container(
      padding: const EdgeInsets.all(28),
      decoration: ext.cardDecoration,
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.person_rounded, size: 18, color: AppColors.textMuted),
              const SizedBox(width: 8),
              Text(recordingState.patientName ?? '', style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
            ],
          ),
          const SizedBox(height: 24),
          AudioRecorder(
            onChunkReady: (data, mime, chunkIndex, isFinal) {
              ref.read(recordingProvider.notifier).onChunkReady(data, mime, chunkIndex, isFinal);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildComplete(RecordingState recordingState, MedScribeThemeExtension ext) {
    return Container(
      padding: const EdgeInsets.all(36),
      decoration: ext.cardDecoration,
      child: Column(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: ext.success.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.check_rounded, size: 32, color: ext.success),
          ),
          const SizedBox(height: 20),
          Text('recording.upload_success'.tr(), style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
          const SizedBox(height: 8),
          Text(
            recordingState.chunksUploaded > 0
                ? 'recording.upload_message'.tr(namedArgs: {'count': recordingState.chunksUploaded.toString()})
                : 'recording.upload_message_no_count'.tr(),
            style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textMuted),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => ref.read(recordingProvider.notifier).reset(),
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.mic_rounded, color: Colors.white, size: 18),
                    const SizedBox(width: 8),
                    Text('recording.new_recording'.tr(), style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
