import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';

class AuditScreen extends ConsumerStatefulWidget {
  const AuditScreen({super.key});

  @override
  ConsumerState<AuditScreen> createState() => _AuditScreenState();
}

class _AuditScreenState extends ConsumerState<AuditScreen> {
  List<Map<String, dynamic>> _logs = [];
  bool _isLoading = true;
  int _total = 0;
  int _page = 1;
  final _actionFilter = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    try {
      final params = <String, dynamic>{'page': _page, 'per_page': 50};
      if (_actionFilter.text.isNotEmpty) params['action'] = _actionFilter.text;
      final response = await api.get('/admin/audit', queryParameters: params);
      setState(() {
        _logs = List<Map<String, dynamic>>.from(response.data['items']);
        _total = (response.data['total'] as num?)?.toInt() ?? 0;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _actionFilter.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin.audit_title'.tr())),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _actionFilter,
                    decoration: InputDecoration(hintText: 'admin.filter_by_action'.tr(), prefixIcon: const Icon(Icons.filter_list)),
                    onSubmitted: (_) => _load(),
                  ),
                ),
                const SizedBox(width: 8),
                Text('admin.total'.tr(namedArgs: {'count': '$_total'})),
              ],
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      columns: [
                        DataColumn(label: Text('admin.date'.tr())),
                        DataColumn(label: Text('admin.action'.tr())),
                        DataColumn(label: Text('admin.entity_type'.tr())),
                        DataColumn(label: Text('admin.id'.tr())),
                        DataColumn(label: Text('admin.ip'.tr())),
                      ],
                      rows: _logs.map((log) => DataRow(cells: [
                        DataCell(Text(_formatDate(log['timestamp']))),
                        DataCell(Text(log['action'] ?? '')),
                        DataCell(Text(log['entity_type'] ?? '')),
                        DataCell(Text(log['entity_id'] ?? '')),
                        DataCell(Text(log['ip_address'] ?? '')),
                      ])).toList(),
                    ),
                  ),
          ),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(icon: const Icon(Icons.chevron_right), onPressed: _page > 1 ? () { setState(() => _page--); _load(); } : null),
                Text('admin.page'.tr(namedArgs: {'page': '$_page'})),
                IconButton(icon: const Icon(Icons.chevron_left), onPressed: () { setState(() => _page++); _load(); }),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return dateStr;
    }
  }
}
