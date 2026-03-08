import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/models/patient_model.dart';
import 'package:medscribe_ai/providers/patients_provider.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class PatientsScreen extends ConsumerStatefulWidget {
  const PatientsScreen({super.key});

  @override
  ConsumerState<PatientsScreen> createState() => _PatientsScreenState();
}

class _PatientsScreenState extends ConsumerState<PatientsScreen> {
  final _searchController = TextEditingController();

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
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('patients.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
                const SizedBox(height: 4),
                Text('patients.subtitle'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted)),
              ],
            ),
          ),
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => context.go('/patients/new'),
              borderRadius: BorderRadius.circular(ext.cardRadius),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryLight]),
                  borderRadius: BorderRadius.circular(ext.cardRadius),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.add_rounded, color: Colors.white, size: 18),
                    const SizedBox(width: 6),
                    Text('patients.add_new'.tr(), style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar(MedScribeThemeExtension ext) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 12),
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
              const SizedBox(width: 8),
              Icon(Icons.chevron_left_rounded, color: AppColors.textMuted, size: 20),
            ],
          ),
        ),
      ),
    );
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
