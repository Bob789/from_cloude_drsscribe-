import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';

class ActivityScreen extends ConsumerStatefulWidget {
  const ActivityScreen({super.key});

  @override
  ConsumerState<ActivityScreen> createState() => _ActivityScreenState();
}

class _ActivityScreenState extends ConsumerState<ActivityScreen> {
  List<Map<String, dynamic>> _logs = [];
  bool _isLoading = true;
  int _total = 0;
  int _page = 1;
  String? _actionFilter;
  String? _entityTypeFilter;
  bool _errorOnly = false;

  static const _actions = ['LOGIN', 'LOGOUT', 'VIEW', 'CREATE', 'UPDATE', 'DELETE', 'SEARCH', 'UPLOAD', 'ERROR'];
  static const _entityTypes = ['patient', 'visit', 'summary', 'recording', 'transcription'];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    try {
      final params = <String, dynamic>{'page': _page, 'per_page': 50};
      if (_actionFilter != null) params['action'] = _actionFilter;
      if (_entityTypeFilter != null) params['entity_type'] = _entityTypeFilter;
      if (_errorOnly) params['error_only'] = true;
      final response = await api.get('/admin/activity-logs', queryParameters: params);
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
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin.activity_title'.tr())),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Wrap(
              spacing: 12,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                SizedBox(
                  width: MediaQuery.of(context).size.width < 500 ? 130 : 160,
                  child: DropdownButtonFormField<String>(
                    value: _actionFilter,
                    decoration: InputDecoration(labelText: 'admin.action'.tr(), isDense: true, contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8)),
                    items: [
                      DropdownMenuItem(value: null, child: Text('admin.all'.tr())),
                      ..._actions.map((a) => DropdownMenuItem(value: a, child: Text(a))),
                    ],
                    onChanged: (v) { _actionFilter = v; _page = 1; _load(); },
                  ),
                ),
                SizedBox(
                  width: MediaQuery.of(context).size.width < 500 ? 130 : 160,
                  child: DropdownButtonFormField<String>(
                    value: _entityTypeFilter,
                    decoration: InputDecoration(labelText: 'admin.entity_type'.tr(), isDense: true, contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8)),
                    items: [
                      DropdownMenuItem(value: null, child: Text('admin.all'.tr())),
                      ..._entityTypes.map((e) => DropdownMenuItem(value: e, child: Text(e))),
                    ],
                    onChanged: (v) { _entityTypeFilter = v; _page = 1; _load(); },
                  ),
                ),
                FilterChip(
                  label: Text('admin.errors_only'.tr()),
                  selected: _errorOnly,
                  onSelected: (v) { _errorOnly = v; _page = 1; _load(); },
                ),
                Text('admin.total'.tr(namedArgs: {'count': '$_total'}), style: const TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _logs.isEmpty
                    ? Center(child: Text('admin.no_records'.tr()))
                    : SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: DataTable(
                          columnSpacing: 24,
                          columns: [
                            DataColumn(label: Text('admin.date'.tr())),
                            DataColumn(label: Text('admin.user'.tr())),
                            DataColumn(label: Text('admin.action'.tr())),
                            DataColumn(label: Text('admin.type'.tr())),
                            DataColumn(label: Text('admin.description'.tr())),
                            DataColumn(label: Text('admin.error'.tr())),
                            DataColumn(label: Text('admin.ip'.tr())),
                          ],
                          rows: _logs.map((log) => DataRow(
                            color: log['error_id'] != null ? WidgetStatePropertyAll(Colors.red.shade50) : null,
                            cells: [
                              DataCell(Text(_formatDate(log['created_at']))),
                              DataCell(Text(log['user_name'] ?? '')),
                              DataCell(_actionChip(log['action'])),
                              DataCell(Text(log['entity_type'] ?? '')),
                              DataCell(ConstrainedBox(constraints: const BoxConstraints(maxWidth: 250), child: Text(log['description'] ?? '', overflow: TextOverflow.ellipsis))),
                              DataCell(Text(log['error_id'] ?? '', style: TextStyle(color: Colors.red.shade700, fontSize: 12))),
                              DataCell(Text(log['ip_address'] ?? '')),
                            ],
                          )).toList(),
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
                IconButton(icon: const Icon(Icons.chevron_left), onPressed: _logs.length < 50 ? null : () { setState(() => _page++); _load(); }),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _actionChip(String? action) {
    final color = switch (action) {
      'CREATE' => Colors.green,
      'UPDATE' => Colors.blue,
      'DELETE' => Colors.red,
      'ERROR' => Colors.red,
      'LOGIN' => Colors.teal,
      'LOGOUT' => Colors.grey,
      'SEARCH' => Colors.purple,
      'VIEW' => Colors.indigo,
      _ => Colors.grey,
    };
    return Chip(
      label: Text(action ?? '', style: TextStyle(fontSize: 11, color: color.shade700)),
      backgroundColor: color.shade50,
      visualDensity: VisualDensity.compact,
      padding: EdgeInsets.zero,
    );
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final date = DateTime.parse(dateStr).toLocal();
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return dateStr;
    }
  }
}
