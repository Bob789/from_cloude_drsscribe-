import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';

class AdminUsersScreen extends ConsumerStatefulWidget {
  const AdminUsersScreen({super.key});

  @override
  ConsumerState<AdminUsersScreen> createState() => _AdminUsersScreenState();
}

class _AdminUsersScreenState extends ConsumerState<AdminUsersScreen> {
  List<Map<String, dynamic>> _users = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final response = await api.get('/admin/users');
      setState(() {
        _users = List<Map<String, dynamic>>.from(response.data);
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _changeRole(String userId, String role) async {
    try {
      await api.put('/admin/users/$userId/role', queryParameters: {'role': role});
      _load();
    } catch (_) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('admin.error_update_role'.tr())));
    }
  }

  Future<void> _toggleActive(String userId, bool active) async {
    try {
      await api.put('/admin/users/$userId/active', queryParameters: {'active': active});
      _load();
    } catch (_) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('admin.error_update_status'.tr())));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());

    return Scaffold(
      appBar: AppBar(title: Text('admin.users_title'.tr())),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(MediaQuery.of(context).size.width < 500 ? 12 : 24),
        child: DataTable(
          columns: [
            DataColumn(label: Text('admin.name'.tr())),
            DataColumn(label: Text('admin.email'.tr())),
            DataColumn(label: Text('admin.role'.tr())),
            DataColumn(label: Text('admin.active'.tr())),
          ],
          rows: _users.map((user) => DataRow(cells: [
            DataCell(Text(user['name'] ?? '')),
            DataCell(Text(user['email'] ?? '')),
            DataCell(DropdownButton<String>(
              value: user['role'],
              items: ['doctor', 'admin', 'receptionist'].map((r) => DropdownMenuItem(value: r, child: Text(r))).toList(),
              onChanged: (v) => v != null ? _changeRole(user['id'], v) : null,
            )),
            DataCell(Switch(
              value: user['is_active'] ?? true,
              onChanged: (v) => _toggleActive(user['id'], v),
            )),
          ])).toList(),
        ),
      ),
    );
  }
}
