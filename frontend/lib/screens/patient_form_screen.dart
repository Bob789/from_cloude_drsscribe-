import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/widgets/patient_form.dart';

class PatientFormScreen extends ConsumerWidget {
  final String? patientId;
  const PatientFormScreen({super.key, this.patientId});

  bool get isEditing => patientId != null && patientId != 'new';

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final keyType = user?.patientKeyType ?? 'national_id';

    return Scaffold(
      appBar: AppBar(title: Text(isEditing ? 'patient_form.edit_title'.tr() : 'patient_form.new_title'.tr())),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 600),
            child: PatientForm(
              patientId: isEditing ? patientId : null,
              onSaved: () => context.go('/patients'),
              patientKeyType: keyType,
            ),
          ),
        ),
      ),
    );
  }
}
