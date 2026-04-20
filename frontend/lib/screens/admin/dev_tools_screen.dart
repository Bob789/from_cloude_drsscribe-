import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';

class DevToolsScreen extends ConsumerStatefulWidget {
  const DevToolsScreen({super.key});

  @override
  ConsumerState<DevToolsScreen> createState() => _DevToolsScreenState();
}

class _DevToolsScreenState extends ConsumerState<DevToolsScreen> {
  Map<String, dynamic>? _state;
  bool _busy = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final res = await api.get('/admin/dev-tools/status');
      setState(() => _state = Map<String, dynamic>.from(res.data));
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _action(String path) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final res = await api.post('/admin/dev-tools/$path');
      final data = Map<String, dynamic>.from(res.data);
      setState(() => _state = Map<String, dynamic>.from(data['state'] ?? {}));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text('admin.dev_tools_action_ok'
                  .tr(namedArgs: {'action': data['action'] ?? path}))),
        );
      }
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final running = _state?['running'] == true;
    final exists = _state?['exists'] == true;
    final statusText = _state?['status'] ?? '—';
    final port = _state?['host_port'] ?? 8090;

    return Scaffold(
      appBar: AppBar(title: Text('admin.dev_tools_title'.tr())),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          running ? Icons.check_circle : Icons.cancel,
                          color: running ? Colors.green : Colors.grey,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          running
                              ? 'admin.dev_tools_running'.tr()
                              : 'admin.dev_tools_stopped'.tr(),
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text('admin.dev_tools_status'
                        .tr(namedArgs: {'status': statusText.toString()})),
                    Text('admin.dev_tools_port'
                        .tr(namedArgs: {'port': port.toString()})),
                    if (_state?['id'] != null)
                      Text('admin.dev_tools_container_id'
                          .tr(namedArgs: {'id': _state!['id'].toString()})),
                    const SizedBox(height: 20),
                    Wrap(
                      spacing: 12,
                      children: [
                        ElevatedButton.icon(
                          onPressed: (_busy || running)
                              ? null
                              : () => _action('start'),
                          icon: const Icon(Icons.play_arrow),
                          label: Text(exists
                              ? 'admin.dev_tools_start'.tr()
                              : 'admin.dev_tools_create'.tr()),
                          style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                              foregroundColor: Colors.white),
                        ),
                        ElevatedButton.icon(
                          onPressed: (_busy || !running)
                              ? null
                              : () => _action('stop'),
                          icon: const Icon(Icons.stop),
                          label: Text('admin.dev_tools_stop'.tr()),
                          style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red,
                              foregroundColor: Colors.white),
                        ),
                        OutlinedButton.icon(
                          onPressed: _busy ? null : _refresh,
                          icon: const Icon(Icons.refresh),
                          label: Text('admin.dev_tools_refresh'.tr()),
                        ),
                      ],
                    ),
                    if (_busy)
                      const Padding(
                          padding: EdgeInsets.only(top: 16),
                          child: LinearProgressIndicator()),
                    if (_error != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 16),
                        child: Text(_error!,
                            style: const TextStyle(color: Colors.red)),
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              color: Colors.amber.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      const Icon(Icons.info_outline, color: Colors.amber),
                      const SizedBox(width: 8),
                      Text('admin.dev_tools_info_title'.tr(),
                          style: Theme.of(context).textTheme.titleMedium),
                    ]),
                    const SizedBox(height: 8),
                    Text('admin.dev_tools_info_body'.tr()),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
