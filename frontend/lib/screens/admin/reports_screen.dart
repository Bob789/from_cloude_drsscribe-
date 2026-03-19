import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';

class ReportsScreen extends ConsumerStatefulWidget {
  const ReportsScreen({super.key});

  @override
  ConsumerState<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends ConsumerState<ReportsScreen> {
  Map<String, dynamic>? _usage;
  List<Map<String, dynamic>> _doctors = [];
  String _period = 'month';
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    try {
      final api = ApiClient().dio;
      final usageRes = await api.get('/reports/usage', queryParameters: {'period': _period});
      final doctorsRes = await api.get('/reports/doctors');
      setState(() {
        _usage = usageRes.data;
        _doctors = List<Map<String, dynamic>>.from(doctorsRes.data);
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin.reports_title'.tr())),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: EdgeInsets.all(MediaQuery.of(context).size.width < 500 ? 12 : 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    spacing: 12,
                    runSpacing: 8,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      Text('admin.period'.tr(namedArgs: {'colon': ': '}), style: Theme.of(context).textTheme.titleMedium),
                      SegmentedButton<String>(
                        segments: [
                          ButtonSegment(value: 'week', label: Text('admin.week'.tr())),
                          ButtonSegment(value: 'month', label: Text('admin.month'.tr())),
                          ButtonSegment(value: 'year', label: Text('admin.year'.tr())),
                        ],
                        selected: {_period},
                        onSelectionChanged: (v) { setState(() => _period = v.first); _load(); },
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  if (_usage != null)
                    Wrap(
                      spacing: 16,
                      runSpacing: 16,
                      children: [
                        _statCard('admin.visits'.tr(), '${_usage!['visits']}', Icons.calendar_today, Colors.blue),
                        _statCard('admin.transcriptions'.tr(), '${_usage!['transcriptions']}', Icons.text_snippet, Colors.green),
                        _statCard('admin.summaries'.tr(), '${_usage!['summaries']}', Icons.summarize, Colors.purple),
                      ],
                    ),
                  const SizedBox(height: 32),
                  Text('admin.doctor_stats'.tr(), style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 12),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      columns: [
                        DataColumn(label: Text('admin.name'.tr())),
                        DataColumn(label: Text('admin.email'.tr())),
                        DataColumn(label: Text('admin.visits'.tr()), numeric: true),
                      ],
                      rows: _doctors.map((d) => DataRow(cells: [
                        DataCell(Text(d['name'] ?? '')),
                        DataCell(Text(d['email'] ?? '')),
                        DataCell(Text('${d['visit_count']}')),
                      ])).toList(),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _statCard(String title, String value, IconData icon, Color color) {
    return SizedBox(
      width: MediaQuery.of(context).size.width < 500 ? (MediaQuery.of(context).size.width - 80) / 2 : 200,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(icon, color: color, size: 32),
              const SizedBox(height: 8),
              Text(value, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
              Text(title, style: TextStyle(color: Colors.grey[600])),
            ],
          ),
        ),
      ),
    );
  }
}
