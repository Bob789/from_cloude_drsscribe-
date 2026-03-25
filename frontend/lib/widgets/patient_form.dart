import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';

class PatientForm extends StatefulWidget {
  final String? patientId;
  final VoidCallback onSaved;
  final String patientKeyType;

  const PatientForm({
    super.key,
    this.patientId,
    required this.onSaved,
    this.patientKeyType = 'national_id',
  });

  @override
  State<PatientForm> createState() => _PatientFormState();
}

class _PatientFormState extends State<PatientForm> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _idNumberController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _professionController = TextEditingController();
  final _addressController = TextEditingController();
  DateTime? _dob;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    if (widget.patientId != null) _loadPatient();
  }

  Future<void> _loadPatient() async {
    setState(() => _isLoading = true);
    try {
      final response = await ApiClient().dio.get(
        '/patients/${widget.patientId}',
      );
      final data = response.data;
      _nameController.text = data['name'] ?? '';
      _idNumberController.text = data['id_number'] ?? '';
      _phoneController.text = data['phone'] ?? '';
      _emailController.text = data['email'] ?? '';
      _professionController.text = data['profession'] ?? '';
      _addressController.text = data['address'] ?? '';
      if (data['dob'] != null) _dob = DateTime.tryParse(data['dob']);
    } catch (_) {}
    setState(() => _isLoading = false);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      final data = {
        'name': _nameController.text,
        if (_idNumberController.text.isNotEmpty)
          'id_number': _idNumberController.text,
        if (_phoneController.text.isNotEmpty) 'phone': _phoneController.text,
        if (_emailController.text.isNotEmpty) 'email': _emailController.text,
        if (_professionController.text.isNotEmpty)
          'profession': _professionController.text,
        if (_addressController.text.isNotEmpty)
          'address': _addressController.text,
        if (_dob != null) 'dob': _dob!.toIso8601String().split('T')[0],
      };
      if (widget.patientId != null) {
        await ApiClient().dio.put('/patients/${widget.patientId}', data: data);
      } else {
        await ApiClient().dio.post('/patients', data: data);
      }
      widget.onSaved();
    } catch (e) {
      if (mounted) {
        String msg = 'common.save_error'.tr();
        if (e is DioException) {
          final detail = e.response?.data?['detail'];
          if (detail != null) msg = detail.toString();
        }
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(msg)));
      }
    }
    setState(() => _isLoading = false);
  }

  @override
  void dispose() {
    _nameController.dispose();
    _idNumberController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _professionController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading &&
        widget.patientId != null &&
        _nameController.text.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextFormField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: 'patient_form.full_name'.tr(),
            ),
            validator: (v) => (v == null || v.length < 2)
                ? 'patient_form.name_required'.tr()
                : null,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _idNumberController,
            decoration: InputDecoration(
              labelText: widget.patientKeyType == 'national_id'
                  ? 'patient_form.id_number'.tr()
                  : 'patient_form.id_number_optional'.tr(),
            ),
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            autocorrect: false,
            enableSuggestions: false,
            validator: (v) {
              if (widget.patientKeyType == 'national_id' &&
                  (v == null || v.isEmpty))
                return 'patient_form.id_required'.tr();
              if (v != null && v.isNotEmpty && !RegExp(r'^\d{9}$').hasMatch(v))
                return 'patient_form.id_format'.tr();
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _phoneController,
            decoration: InputDecoration(
              labelText: widget.patientKeyType == 'phone'
                  ? 'patient_form.phone'.tr()
                  : 'patient_form.phone_optional'.tr(),
            ),
            keyboardType: TextInputType.phone,
            inputFormatters: [
              FilteringTextInputFormatter.allow(RegExp(r'[0-9+\-() ]')),
            ],
            autocorrect: false,
            enableSuggestions: false,
            validator: (v) {
              if (widget.patientKeyType == 'phone' && (v == null || v.isEmpty))
                return 'patient_form.phone_required'.tr();
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: widget.patientKeyType == 'email'
                  ? 'patient_form.email'.tr()
                  : 'patient_form.email_optional'.tr(),
            ),
            keyboardType: TextInputType.emailAddress,
            validator: (v) {
              if (widget.patientKeyType == 'email' && (v == null || v.isEmpty))
                return 'patient_form.email_required'.tr();
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _professionController,
            decoration: InputDecoration(
              labelText: 'patient_form.profession'.tr(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _addressController,
            decoration: InputDecoration(labelText: 'patient_form.address'.tr()),
          ),
          const SizedBox(height: 16),
          ListTile(
            title: Text(
              _dob != null
                  ? 'patient_form.dob_selected'.tr(
                      namedArgs: {
                        'date': '${_dob!.day}/${_dob!.month}/${_dob!.year}',
                      },
                    )
                  : 'patient_form.dob'.tr(),
            ),
            trailing: const Icon(Icons.calendar_today),
            onTap: () async {
              final picked = await showDatePicker(
                context: context,
                initialDate: _dob ?? DateTime(1990),
                firstDate: DateTime(1900),
                lastDate: DateTime.now(),
              );
              if (picked != null) setState(() => _dob = picked);
            },
          ),
          const SizedBox(height: 32),
          ElevatedButton(
            onPressed: _isLoading ? null : _submit,
            child: _isLoading
                ? const CircularProgressIndicator()
                : Text('common.save'.tr()),
          ),
        ],
      ),
    );
  }
}
